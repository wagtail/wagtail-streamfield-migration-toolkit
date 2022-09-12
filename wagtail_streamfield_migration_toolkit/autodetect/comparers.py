from wagtail import hooks
from wagtail.blocks import StreamBlock, StructBlock, ListBlock, Block


class BaseBlockDefComparer:
    """Base class for all BlockDefComparers"""

    # TODO Include name comparison logic here too
    #

    # weights for the importance of argument similarity and direct child block similarity.
    arg_weight = None
    child_weight = None
    # name_weight = None # TODO

    @classmethod
    def compare(cls, old_def, old_name, new_def, new_name):

        # TODO this might not be a black and white decision for all cases
        # However for cases like where old block is a StreamBlock and compared block is a CharBlock,
        # it is fair to say that we can be certain it is not a renamed block.
        # TODO consider eg. like CharBlock, TextBlock
        if not cls.compare_types(old_def, new_def):
            return False

        # name_similarity = cls.compare_names(old_name, new_name) # TODO

        arg_similarity = cls.compare_args(old_def, new_def)

        child_similarity = cls.compare_children(old_def, new_def)

        return (
            arg_similarity * cls.arg_weight + child_similarity * cls.child_weight
        ) / (cls.arg_weight + cls.child_weight)

    @staticmethod
    def compare_types(old_def, new_def):
        # returns a boolean
        return True if type(old_def) is type(new_def) else False

    @staticmethod
    def compare_args(old_def, new_def):
        # returns a normalized score (0 to 1)
        raise NotImplementedError

    @staticmethod
    def compare_children(old_def, new_def):
        # returns a normalized score (0 to 1)
        raise NotImplementedError

    @staticmethod
    def compare_names(old_name, new_name):
        return 1 if old_name == new_name else 0


class DefaultBlockDefComparer(BaseBlockDefComparer):
    """Default used when no other comparer is available"""

    arg_weight = 0.5
    child_weight = 0.5

    @staticmethod
    def compare_args(old_def, new_def):
        return 1

    @staticmethod
    def compare_children(old_def, new_def):
        return 1


class StreamBlockDefComparer(BaseBlockDefComparer):
    """Comparer for StreamBlocks"""

    # a weight for args and children
    arg_weight = 0
    child_weight = 1

    @staticmethod
    def compare_types(old_def, new_def):
        return isinstance(new_def, StreamBlock)

    @staticmethod
    def compare_args(old_def, new_def):
        return 1

    @staticmethod
    def compare_children(old_def, new_def):
        old_children = old_def.child_blocks
        new_children = new_def.child_blocks
        count = 0
        for old_child_name, old_child_def in old_children.items():
            # TODO use a comparer here?
            if old_child_name in new_children and type(
                new_children[old_child_name]
            ) is type(old_child_def):
                count += 1

        return count / len(old_children)


class StructBlockDefComparer(BaseBlockDefComparer):
    """Comparer for StructBlocks"""

    arg_weight = 0
    child_weight = 1

    @staticmethod
    def compare_types(old_def, new_def):
        return isinstance(new_def, StructBlock)

    @staticmethod
    def compare_args(old_def, new_def):
        return 1

    @staticmethod
    def compare_children(old_def, new_def):
        old_children = old_def.child_blocks
        new_children = new_def.child_blocks
        count = 0
        for old_child_name, old_child_def in old_children.items():
            # comparer = block_def_comparer_registry.get_block_def_comparer(old_child_def)
            # score = comparer.compare()
            # TODO using comparers: how to get mapping? do we compare all pairs and get a mapping?
            #
            # TODO might need to cache when using comparers here, @lru_cache
            if old_child_name in new_children and type(
                new_children[old_child_name]
            ) is type(old_child_def):
                count += 1

        return count / len(old_children)


class ListBlockDefComparer(BaseBlockDefComparer):
    """Comparer for ListBlocks"""

    arg_weight = 0
    child_weight = 1

    @staticmethod
    def compare_types(old_def, new_def):
        return isinstance(new_def, ListBlock)

    @staticmethod
    def compare_args(old_def, new_def):
        return 1

    @staticmethod
    def compare_children(old_def, new_def):
        old_child = old_def.child_block
        new_child = new_def.child_block
        # TODO we might need a less strict comparison here
        return old_child == new_child


class BlockDefComparerRegistry:
    BASE_COMPARERS_BY_BLOCK_TYPE = {
        Block: DefaultBlockDefComparer,
        ListBlock: ListBlockDefComparer,
        StreamBlock: StreamBlockDefComparer,
        StructBlock: StructBlockDefComparer,
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

    def get_block_def_comparer(self, block_def):
        # find the comparer class for the most specific class in the block's inheritance tree

        if not self._scanned_for_comparers:
            self._scan_for_comparers()

        for block_class in type(block_def).__mro__:
            if block_class in self.comparers_by_block_type:
                return self.comparers_by_block_type[block_class]


block_def_comparer_registry = BlockDefComparerRegistry()
