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

    # weights for the importance of option similarity and name similarity
    name_weight = None
    option_weight = None

    # custom weights for specific options - NOTE that sum of all weights should add up to 1
    custom_option_weights = {}

    @classmethod
    def compare(cls, old_def, old_name, new_def, new_name):

        # TODO it might be best to add some separate tests for the hashable_deep_deconstruct method
        # itself
        old_path, _, old_options = cls.hashable_deep_deconstruct(old_def)
        new_path, _, new_options = cls.hashable_deep_deconstruct(new_def)

        # options are a list of all args and kwargs with any defaults applied for all blocks
        # see https://docs.wagtail.org/en/stable/reference/streamfield/blocks.html for options
        # for different block types

        return cls._compare(
            old_name=old_name,
            old_path=old_path,
            old_options=old_options,
            new_name=new_name,
            new_path=new_path,
            new_options=new_options,
        )

    @classmethod
    @lru_cache()
    def _compare(
        cls,
        old_name,
        old_path,
        old_options,
        new_name,
        new_path,
        new_options,
    ):
        # This might not be a black and white decision for all cases. However for cases like where
        # old block is a StreamBlock and compared block is a CharBlock, it is fair to say that we
        # can be certain it is not a renamed block.
        # TODO consider eg. like CharBlock, TextBlock. In that case do we give this a weight and
        # return a non zero score for blocks like char and text that may have compatible content?
        if not cls.compare_types(old_path, new_path):
            return 0

        name_similarity = cls.compare_names(old_name, new_name)
        option_similarity = cls.compare_options(old_options, new_options)

        return cls.normalize_similarity(
            name_similarity=name_similarity, option_similarity=option_similarity
        )

    @staticmethod
    def compare_types(old_path, new_path):
        # returns a boolean
        return old_path == new_path

    @classmethod
    def compare_options(cls, old_options, new_options):
        # TODO - suggestion: add a weight to options we want to specifically give a different
        # weight, and take 1-(x) / len(remaining options) for the rest of the options

        # returns a score between 0 and 1

        if len(old_options) == 0 and len(new_options) == 0:
            return 1

        old_options_dict = dict(old_options)
        new_options_dict = dict(new_options)
        all_keys = set(old_options_dict.keys()).union(set(new_options_dict.keys()))

        # Default weight is calculated as (1 - sum of custom weights) / (number of options)
        default_weight = 1
        option_count = len(all_keys)
        for _, weight in cls.custom_option_weights.items():
            default_weight -= weight
            option_count -= 1
        default_weight = default_weight / option_count

        option_score = 0
        for key in all_keys:
            old_value = old_options_dict.get(key, None)
            new_value = new_options_dict.get(key, None)

            if old_value == new_value:
                if key in cls.custom_option_weights:
                    option_score += cls.custom_option_weights[key]
                else:
                    option_score += default_weight
        return option_score

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
            path, options = cls.get_options(obj)
            setattr(
                obj,
                "_hashable_deep_deconstructed",
                (
                    path,
                    (),
                    tuple(
                        (key, cls.hashable_deep_deconstruct(value))
                        for key, value in options.items()
                    ),
                ),
            )
            return getattr(obj, "_hashable_deep_deconstructed")
        elif isinstance(obj, StreamValue):
            return obj.__class__.__name__
        else:
            return obj

    @staticmethod
    def get_options(block):

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

        options_dict = {**defaults, **flat_bound}

        for attr in dir(block.meta):
            if attr.startswith("_"):
                continue
            value = getattr(block.meta, attr)
            options_dict[attr] = value

        return path, options_dict

    @classmethod
    def normalize_similarity(cls, name_similarity, option_similarity):
        return (
            name_similarity * cls.name_weight + option_similarity * cls.option_weight
        ) / (cls.name_weight + cls.option_weight)


class StructuralBlockDefComparer(BaseBlockDefComparer):
    # For structural blocks, i.e., Stream, Struct and List Blocks.

    child_option_weight = None
    base_option_weight = None

    @classmethod
    def compare_options(cls, old_options, new_options):
        old_children, new_children, old_options, new_options = cls.extract_children(
            old_options, new_options
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
        option_score = super().compare_options(old_options, new_options)

        return (
            child_score * cls.child_option_weight + option_score * cls.base_option_weight
        ) / (cls.child_option_weight + cls.base_option_weight)

    @classmethod
    def extract_children(cls, old_options, new_options):
        # define method to get children in subclasses
        # make sure to pop them from the options
        return (), (), old_options, new_options


class DefaultBlockDefComparer(BaseBlockDefComparer):
    """Default used when no other comparer is available"""

    name_weight = 2
    option_weight = 1


class CharBlockDefComparer(BaseBlockDefComparer):
    """Comparer for CharBlocks"""

    # TODO in future might allow comparing other block types too, e.g. CharBlock vs TextBlock

    name_weight = 1
    option_weight = 0.8


class StreamBlockDefComparer(StructuralBlockDefComparer):
    """Comparer for StreamBlocks"""

    name_weight = 1
    option_weight = 1
    child_option_weight = 1
    base_option_weight = 0.1

    @classmethod
    def extract_children(cls, old_options, new_options):
        old_children = ()
        _old_options = []
        for (key, value) in old_options:
            if key == "local_blocks":
                old_children = value
            else:
                _old_options.append((key, value))

        new_children = ()
        _new_options = []
        for (key, value) in new_options:
            if key == "local_blocks":
                new_children = value
            else:
                _new_options.append((key, value))

        return old_children, new_children, _old_options, _new_options


class StructBlockDefComparer(StructuralBlockDefComparer):
    """Comparer for StructBlocks"""

    name_weight = 1
    option_weight = 1
    child_option_weight = 1
    base_option_weight = 0.1

    @classmethod
    def extract_children(cls, old_options, new_options):
        old_children = ()
        _old_options = []
        for (key, value) in old_options:
            if key == "local_blocks":
                old_children = value
            else:
                _old_options.append((key, value))

        new_children = ()
        _new_options = []
        for (key, value) in new_options:
            if key == "local_blocks":
                new_children = value
            else:
                _new_options.append((key, value))

        return old_children, new_children, _old_options, _new_options


class ListBlockDefComparer(StructuralBlockDefComparer):
    """Comparer for ListBlocks"""

    name_weight = 1
    option_weight = 0.5
    child_option_weight = 1
    base_option_weight = 0.2

    @staticmethod
    def extract_children(old_options, new_options):
        old_child = ()
        _old_options = []
        for (key, value) in old_options:
            if key == "child_block":
                old_child = ((key, value),)
            else:
                _old_options.append((key, value))

        new_child = ()
        _new_options = []
        for (key, value) in new_options:
            if key == "child_block":
                new_child = ((key, value),)
            else:
                _new_options.append((key, value))

        return old_child, new_child, _old_options, _new_options


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
