from wagtail.blocks import StreamBlock, StructBlock


class BaseBlockDefComparer:
    """TODO"""

    # TODO need a proper way to measure similarity
    similarity_threshold = None

    @classmethod
    def compare(cls, old_def, new_def):

        # TODO this might not be a black and white decision for all cases
        # However for cases like where old block is a StreamBlock and compared block is a CharBlock,
        # it is fair to say that we can be certain it is not a renamed block.
        if not cls.compare_types(old_def, new_def):
            return False

        similarity = 0
        similarity += cls.compare_args(old_def, new_def)
        similarity += cls.compare_children(old_def, new_def)
        return similarity >= cls.similarity_threshold

    @staticmethod
    def compare_types(old_def, new_def):
        return True if type(old_def) is type(new_def) else False

    @staticmethod
    def compare_args(old_def, new_def):
        raise NotImplementedError

    @staticmethod
    def compare_children(old_def, new_def):
        raise NotImplementedError


class StreamOrStructBlockDefComparer(BaseBlockDefComparer):
    """TODO"""

    similarity_threshold = 1.66

    @staticmethod
    def compare_types(old_def, new_def):
        if isinstance(old_def, StreamBlock):
            return isinstance(new_def, StreamBlock)
        elif isinstance(old_def, StructBlock):
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
            if old_child_name in new_children and type(
                new_children[old_child_name]
            ) is type(old_child_def):
                count += 1

        return count / len(old_children)


# class ListBlockDefComparer(BaseBlockDefComparer):
#     pass
# TODO


class DefaultBlockDefComparer(BaseBlockDefComparer):
    """TODO"""

    similarity_threshold = 2

    @staticmethod
    def compare_args(old_def, new_def):
        return 1

    @staticmethod
    def compare_children(old_def, new_def):
        return 1
