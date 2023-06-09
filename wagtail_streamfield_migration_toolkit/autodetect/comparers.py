import importlib
import inspect
from functools import lru_cache
from wagtail import hooks
from wagtail.blocks import (
    StreamBlock,
    StructBlock,
    ListBlock,
    Block,
    CharBlock,
    StreamValue,
)


@lru_cache()
def import_class(path):
    module_path, class_name = ".".join(path.split(".")[:-1]), path.split(".")[-1]
    return getattr(importlib.import_module(module_path), class_name)


class BaseBlockDefComparer:
    """Base class for all BlockDefComparers"""

    # weights for the importance of keyword argument similarity and name similarity
    name_weight = None
    kwarg_weight = None

    @classmethod
    def compare(cls, old_def, old_name, new_def, new_name):

        # TODO it might be best to add some separate tests for the hashable_deep_deconstruct method
        # itself
        old_path, _, old_kwargs = cls.hashable_deep_deconstruct(old_def)
        new_path, _, new_kwargs = cls.hashable_deep_deconstruct(new_def)

        # TODO rewrite explanation for changes to kwargs
        # - For structural blocks, args are a list of children, and kwargs contain block options
        # like label, icon etc.
        # - For other blocks, args includes any positional arguments and kwargs contains the block
        # options. Most basic blocks like CharBlock have no args it seems.

        return cls._compare(
            old_name=old_name,
            old_path=old_path,
            old_kwargs=old_kwargs,
            new_name=new_name,
            new_path=new_path,
            new_kwargs=new_kwargs,
        )

    @classmethod
    @lru_cache()
    def _compare(
        cls,
        old_name,
        old_path,
        old_kwargs,
        new_name,
        new_path,
        new_kwargs,
    ):
        # This might not be a black and white decision for all cases. However for cases like where
        # old block is a StreamBlock and compared block is a CharBlock, it is fair to say that we
        # can be certain it is not a renamed block.
        # TODO consider eg. like CharBlock, TextBlock. In that case do we give this a weight and
        # return a non zero score for blocks like char and text that may have compatible content?
        if not cls.compare_types(old_path, new_path):
            return 0

        name_similarity = cls.compare_names(old_name, new_name)
        kwarg_similarity = cls.compare_kwargs(old_kwargs, new_kwargs)

        return cls.normalize_similarity(
            name_similarity=name_similarity, kwarg_similarity=kwarg_similarity
        )

    @staticmethod
    def compare_types(old_path, new_path):
        # returns a boolean
        return old_path == new_path

    @classmethod
    def compare_kwargs(cls, old_kwargs, new_kwargs):
        # returns a score between 0 and 1

        if len(old_kwargs) == 0 and len(new_kwargs) == 0:
            return 1

        old_kwargs_dict = dict(old_kwargs)
        new_kwargs_dict = dict(new_kwargs)
        all_keys = set(old_kwargs_dict.keys()).union(set(new_kwargs_dict.keys()))

        kwarg_score = 0
        for key in all_keys:
            old_value = old_kwargs_dict.get(key, None)
            new_value = new_kwargs_dict.get(key, None)

            if old_value == new_value:
                kwarg_score += 1
        kwarg_score = kwarg_score / len(all_keys)

        return kwarg_score

    @staticmethod
    def compare_names(old_name, new_name):
        # returns a normalized score (0 to 1)
        return 1 if old_name == new_name else 0

    @classmethod
    def hashable_deep_deconstruct(cls, obj):
        """Recursively deconstructs blocks and converts returned structures into hashable types.

        This method is useful for use with the lru_cache decorator, since it requires method
        arguments to be hashable, and the Block objects we are working with are not hashable. This
        calls deconstruct on Blocks and converts the returned lists, dicts and child Blocks into
        hashable objects.

        NOTE: an attribute `_hashable_deep_deconstructed` is added to Block objects for which
        this has already been called once.
        """

        # if we've already computed this for a block, keep that as an attribute on the block
        # and return it. Note that this would be done only for blocks.
        if hasattr(obj, "_hashable_deep_deconstructed"):
            return getattr(obj, "_hashable_deep_deconstructed")

        if isinstance(obj, list):
            return tuple(cls.hashable_deep_deconstruct(value) for value in obj)
        elif isinstance(obj, tuple):
            return tuple(cls.hashable_deep_deconstruct(value) for value in obj)
        elif isinstance(obj, dict):
            return tuple(
                (key, cls.hashable_deep_deconstruct(value))
                for key, value in obj.items()
            )
        elif isinstance(obj, type):
            return obj.__qualname__
        elif hasattr(obj, "deconstruct"):
            path, args, kwargs = cls.get_default_kwargs(obj)
            setattr(
                obj,
                "_hashable_deep_deconstructed",
                (
                    path,
                    tuple(cls.hashable_deep_deconstruct(value) for value in args),
                    tuple(
                        (key, cls.hashable_deep_deconstruct(value))
                        for key, value in kwargs.items()
                    ),
                ),
            )
            return getattr(obj, "_hashable_deep_deconstructed")
        elif isinstance(obj, StreamValue):
            return obj.__class__.__name__
        else:
            return obj

    @staticmethod
    def get_default_kwargs(block):

        path, args, kwargs = block.deconstruct()
        signature = inspect.Signature.from_callable(block.__init__)
        defaults = {
            k: v.default
            for k, v in signature.parameters.items()
            if k not in ("self", "kwargs")
        }
        bound = signature.bind(*args, **kwargs).arguments
        extras = bound.pop("kwargs", {})
        flat_bound = {**bound, **extras}

        kwargs_dict = {**defaults, **flat_bound}

        for attr in dir(block.meta):
            if attr.startswith("_"):
                continue
            value = getattr(block.meta, attr)
            kwargs_dict[attr] = value

        return path, (), kwargs_dict

    @classmethod
    def normalize_similarity(cls, name_similarity, kwarg_similarity):
        return (
            name_similarity * cls.name_weight + kwarg_similarity * cls.kwarg_weight
        ) / (cls.name_weight + cls.kwarg_weight)


class StructuralBlockDefComparer(BaseBlockDefComparer):
    # For structural blocks, i.e., Stream, Struct and List Blocks.

    child_kwarg_weight = None
    base_kwarg_weight = None

    @classmethod
    def compare_kwargs(cls, old_kwargs, new_kwargs):
        old_children, new_children, old_kwargs, new_kwargs = cls.get_children(
            old_kwargs, new_kwargs
        )

        old_child_dict = dict(old_children)
        new_child_dict = dict(new_children)

        # TODO do proper mapping of children, not just by name. Currently we have a very simplistic
        # mapping by name.

        mapped_child_names = list(
            set(old_child_dict.keys()).intersection(set(new_child_dict.keys()))
        )
        all_child_names = list(
            set(old_child_dict.keys()).union(set(new_child_dict.keys()))
        )

        child_score = len(mapped_child_names) / len(all_child_names)
        kwarg_score = super().compare_kwargs(old_kwargs, new_kwargs)

        return (
            child_score * cls.child_kwarg_weight + kwarg_score * cls.base_kwarg_weight
        ) / (cls.child_kwarg_weight + cls.base_kwarg_weight)

    @classmethod
    def get_children(cls, old_kwargs, new_kwargs):
        # define method to get children in subclasses
        return (), (), old_kwargs, new_kwargs


class DefaultBlockDefComparer(BaseBlockDefComparer):
    """Default used when no other comparer is available"""

    name_weight = 2
    kwarg_weight = 1


class CharBlockDefComparer(BaseBlockDefComparer):
    """Comparer for CharBlocks"""

    # TODO in future might allow comparing other block types too, e.g. CharBlock vs TextBlock

    name_weight = 1
    kwarg_weight = 0.8


class StreamBlockDefComparer(StructuralBlockDefComparer):
    """Comparer for StreamBlocks"""

    name_weight = 1
    kwarg_weight = 1
    child_kwarg_weight = 1
    base_kwarg_weight = 0.1

    @classmethod
    def get_children(cls, old_kwargs, new_kwargs):
        old_children = ()
        for (key, value) in old_kwargs:
            if key == "local_blocks":
                old_children = value

        new_children = ()
        for (key, value) in new_kwargs:
            if key == "local_blocks":
                new_children = value

        return old_children, new_children, old_kwargs, new_kwargs


class StructBlockDefComparer(StructuralBlockDefComparer):
    """Comparer for StructBlocks"""

    name_weight = 1
    kwarg_weight = 1
    child_kwarg_weight = 1
    base_kwarg_weight = 0.1

    @classmethod
    def get_children(cls, old_kwargs, new_kwargs):
        old_children = ()
        for (key, value) in old_kwargs:
            if key == "local_blocks":
                old_children = value

        new_children = ()
        for (key, value) in new_kwargs:
            if key == "local_blocks":
                new_children = value

        return old_children, new_children, old_kwargs, new_kwargs


class ListBlockDefComparer(StructuralBlockDefComparer):
    """Comparer for ListBlocks"""

    name_weight = 1
    kwarg_weight = 0.5
    child_kwarg_weight = 1
    base_kwarg_weight = 0.2

    @staticmethod
    def get_children(old_kwargs, new_kwargs):
        old_child = ()
        for (key, value) in old_kwargs:
            if key == "child_block":
                old_child = ((key, value),)

        new_child = ()
        for (key, value) in new_kwargs:
            if key == "child_block":
                new_child = ((key, value),)

        return old_child, new_child, old_kwargs, new_kwargs


class BlockDefComparerRegistry:
    BASE_COMPARERS_BY_BLOCK_TYPE = {
        Block: DefaultBlockDefComparer,
        ListBlock: ListBlockDefComparer,
        StreamBlock: StreamBlockDefComparer,
        StructBlock: StructBlockDefComparer,
        CharBlock: CharBlockDefComparer,
    }

    def __init__(self):
        self._scanned_for_comparers = False
        self.comparers_by_block_type = {}

    def _scan_for_comparers(self):
        comparers = dict(self.BASE_COMPARERS_BY_BLOCK_TYPE)

        for fn in hooks.get_hooks("register_block_def_comparers"):
            comparers.update(fn())

        self.comparers_by_block_type = comparers
        self._scanned_for_comparers = True

    def get_block_def_comparer_for_instance(self, block_def):
        # find the comparer class for the most specific class in the block's inheritance tree

        if not self._scanned_for_comparers:
            self._scan_for_comparers()

        for block_class in type(block_def).__mro__:
            if block_class in self.comparers_by_block_type:
                return self.comparers_by_block_type[block_class]

    def get_block_def_comparer_for_class(self, block_def_class):
        # find the comparer class for the most specific class in the block's inheritance tree

        if not self._scanned_for_comparers:
            self._scan_for_comparers()

        for block_class in block_def_class.__mro__:
            if block_class in self.comparers_by_block_type:
                return self.comparers_by_block_type[block_class]


block_def_comparer_registry = BlockDefComparerRegistry()
