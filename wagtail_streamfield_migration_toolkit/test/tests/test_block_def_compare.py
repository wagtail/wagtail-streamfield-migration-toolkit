from typing import Callable
from django.test import TestCase
from wagtail.blocks import (
    Block,
    CharBlock,
    IntegerBlock,
    DateBlock,
    StreamBlock,
    StructBlock,
    ListBlock,
    TextBlock,
    BooleanBlock,
)

from wagtail_streamfield_migration_toolkit.autodetect.comparers import (
    BaseBlockDefComparer,
    StreamBlockDefComparer,
    StructBlockDefComparer,
    CharBlockDefComparer,
    ListBlockDefComparer
)
from wagtail_streamfield_migration_toolkit.autodetect.streamchangedetector import (
    VERIFYING_SIMILARITY_THRESHOLD,
    CONFIDENT_SIMILARITY_THRESHOLD,
)


class TwoFieldStruct(StructBlock):
    char_block = CharBlock(max_length=255)
    int_block = IntegerBlock()


class ThreeFieldStruct(TwoFieldStruct):
    date_block = DateBlock()


class FourFieldStruct(ThreeFieldStruct):
    list_char_block = ListBlock(CharBlock())


class FiveFieldStruct(FourFieldStruct):
    word_block = CharBlock(max_length=125)


class DiffThreeFieldStruct(StructBlock):
    my_text = TextBlock()
    my_int = IntegerBlock()
    my_boolean = BooleanBlock()


class NestedStruct1(StructBlock):
    char_block = CharBlock()
    nested_struct_one = FourFieldStruct()
    nested_struct_two = ThreeFieldStruct()


class NestedStruct2(StructBlock):
    char_block = CharBlock()
    nested_struct_one = ThreeFieldStruct()
    nested_struct_two = ThreeFieldStruct()


class BlockComparerTestCase(TestCase):
    # TODO predicates
    @staticmethod
    def is_similar(score):
        return score > CONFIDENT_SIMILARITY_THRESHOLD

    @staticmethod
    def is_unsure(score):
        return (
            score < CONFIDENT_SIMILARITY_THRESHOLD
            and score >= VERIFYING_SIMILARITY_THRESHOLD
        )

    @staticmethod
    def is_dissimilar(score):
        return score < VERIFYING_SIMILARITY_THRESHOLD

    def assertBlockComparisonScore(
        self,
        comparer: BaseBlockDefComparer,
        old_def: Block,
        old_name: str,
        new_def: Block,
        new_name: str,
        predicate: Callable[[float], bool],
    ):
        # predicate would be one of the functions `is_similar`, `is_unsure`, `is_dissimilar`
        comparison_score = comparer.compare(
            old_def=old_def, old_name=old_name, new_def=new_def, new_name=new_name
        )
        self.assertTrue(predicate(comparison_score))


class TestStructBlocks(BlockComparerTestCase):
    def test_same_block(self):
        # comparing the same blocks should obviously give a score of 1; we would be pretty confident
        # that they are the same block.
        self.assertBlockComparisonScore(
            comparer=StructBlockDefComparer,
            old_def=FourFieldStruct(),
            old_name="foo",
            new_def=FourFieldStruct(),
            new_name="foo",
            predicate=self.is_similar,
        )

    def test_diff_names(self):
        # If names are different we should not be sure if it is the same block
        # (We have actually used the same block here)
        self.assertBlockComparisonScore(
            comparer=StructBlockDefComparer,
            old_def=FourFieldStruct(),
            old_name="foo",
            new_def=FourFieldStruct(),
            new_name="fee",
            predicate=self.is_unsure,
        )

    def test_removed_children(self):
        # When looking at removed children, if there are only one or two children, there is a
        # significant chance that the two blocks are different.
        # (We have actually used the same block here)
        self.assertBlockComparisonScore(
            comparer=StructBlockDefComparer,
            old_def=ThreeFieldStruct(),
            old_name="foo",
            new_def=TwoFieldStruct(),
            new_name="foo",
            predicate=self.is_unsure,
        )

        # When looking at removed children, if there are many children and only one is removed,
        # we can be fairly confident that the blocks are the same.
        # (We have actually used the same block here)
        self.assertBlockComparisonScore(
            comparer=StructBlockDefComparer,
            old_def=FiveFieldStruct(),
            old_name="foo",
            new_def=FourFieldStruct(),
            new_name="foo",
            predicate=self.is_similar,
        )

        # NOTE that there are probably situations between these that could go either way

        # NOTE that even if the children are very different, (eg: several children are removed),
        # as long as the blocks have the same name, we cannot be that the blocks are indeed
        # different.
        self.assertBlockComparisonScore(
            comparer=StructBlockDefComparer,
            old_def=FiveFieldStruct(),
            old_name="foo",
            new_def=TwoFieldStruct(),
            new_name="foo",
            predicate=self.is_unsure,
        )

    def test_added_children(self):
        # added child, this would return a score of 1 currently. NOTE that this will change when
        # the logic changes to consider additions for children too
        self.assertBlockComparisonScore(
            comparer=StructBlockDefComparer,
            old_def=ThreeFieldStruct(),
            old_name="foo",
            new_def=FourFieldStruct(),
            new_name="foo",
            predicate=self.is_similar,
        )

    def test_same_name_diff_children(self):
        # same name, different children. As long as the same name is there, we can't be sure that it
        # is not the same block.
        # (We have actually used different blocks here)
        self.assertBlockComparisonScore(
            comparer=StructBlockDefComparer,
            old_def=ThreeFieldStruct(),
            old_name="foo",
            new_def=DiffThreeFieldStruct(),
            new_name="foo",
            predicate=self.is_unsure,
        )

    def test_nested_child_comparison(self):
        # A small difference in nested children shouldn't require verifying whether the block is the
        # same.
        self.assertBlockComparisonScore(
            comparer=StructBlockDefComparer,
            old_def=NestedStruct1(),
            old_name="foo",
            new_def=NestedStruct2(),
            new_name="foo",
            predicate=self.is_similar,
        )

    def test_removed_kwargs(self):
        # For struct blocks with the same names and same children, we can be fairly certain that
        # they are the same block regardless of changes to kwargs. (This isn't necessarily the case
        # for non structural blocks)
        self.assertBlockComparisonScore(
            comparer=StructBlockDefComparer,
            old_def=FourFieldStruct(label="FOO", icon="cup"),
            old_name="foo",
            new_def=FourFieldStruct(),
            new_name="foo",
            predicate=self.is_similar,
        )

    def test_diff_name_diff_children(self):
        # These are clearly different blocks. Even if a user renames a block and then changes
        # children, that is not something we want to recognize in the autodetector.
        self.assertBlockComparisonScore(
            comparer=StructBlockDefComparer,
            old_def=ThreeFieldStruct(),
            old_name="foo",
            new_def=DiffThreeFieldStruct(),
            new_name="fee",
            predicate=self.is_dissimilar,
        )


class TwoFieldStream(StreamBlock):
    char_block = CharBlock()
    int_block = IntegerBlock()


class ThreeFieldStream(TwoFieldStream):
    date_block = DateBlock()


class FourFieldStream(ThreeFieldStream):
    list_char_block = ListBlock(CharBlock())


class FiveFieldStream(FourFieldStream):
    word_block = CharBlock(max_length=125)


class DiffThreeFieldStream(StreamBlock):
    my_text = TextBlock()
    my_int = IntegerBlock()
    my_boolean = BooleanBlock()


class TestStreamBlocks(BlockComparerTestCase):
    def test_same_block(self):
        # comparing the same blocks should obviously give a score of 1; we would be pretty confident
        # that they are the same block
        self.assertBlockComparisonScore(
            comparer=StreamBlockDefComparer,
            old_def=FourFieldStream(),
            old_name="foo",
            new_def=FourFieldStream(),
            new_name="foo",
            predicate=self.is_similar,
        )

    def test_removed_children(self):
        # When looking at removed children, if there are only one or two children, there is a
        # significant chance that the two blocks are different.
        # (We have actually used the same block here)
        self.assertBlockComparisonScore(
            comparer=StreamBlockDefComparer,
            old_def=ThreeFieldStream(),
            old_name="foo",
            new_def=TwoFieldStream(),
            new_name="foo",
            predicate=self.is_unsure,
        )

        # When looking at removed children, if there are many children and only one is removed,
        # we can be fairly confident that the blocks are the same.
        # (We have actually used the same block here)
        self.assertBlockComparisonScore(
            comparer=StreamBlockDefComparer,
            old_def=FiveFieldStream(),
            old_name="foo",
            new_def=FourFieldStream(),
            new_name="foo",
            predicate=self.is_similar,
        )

        # NOTE that there are probably situations between these that could go either way

    def test_added_children(self):
        # added child, this would return a score of 1 currently. NOTE that this will change when
        # the logic changes to consider additions for children too
        self.assertBlockComparisonScore(
            comparer=StreamBlockDefComparer,
            old_def=ThreeFieldStream(),
            old_name="foo",
            new_def=FourFieldStream(),
            new_name="foo",
            predicate=self.is_similar,
        )

    def test_same_name_diff_children(self):
        # same name, different children. As long as the same name is there, we can't be sure that it
        # is not the same block.
        # (We have actually used different blocks here)
        self.assertBlockComparisonScore(
            comparer=StreamBlockDefComparer,
            old_def=ThreeFieldStream(),
            old_name="foo",
            new_def=DiffThreeFieldStream(),
            new_name="foo",
            predicate=self.is_unsure,
        )

    def test_diff_name_diff_children(self):
        # These are clearly different blocks. Even if a user renames a block and then changes
        # children, that is not something we want to recognize in the autodetector.
        self.assertBlockComparisonScore(
            comparer=StreamBlockDefComparer,
            old_def=ThreeFieldStream(),
            old_name="foo",
            new_def=DiffThreeFieldStream(),
            new_name="fee",
            predicate=self.is_dissimilar,
        )


class TestListBlocks(BlockComparerTestCase):
    def test_same_block(self):
        # comparing the same blocks should obviously give a score of 1; we would be pretty confident
        # that they are the same block
        self.assertBlockComparisonScore(
            comparer=ListBlockDefComparer,
            old_def=ListBlock(CharBlock()),
            old_name="foo",
            new_def=ListBlock(CharBlock()),
            new_name="foo",
            predicate=self.is_similar,
        )


class TestCharBlocks(BlockComparerTestCase):
    def test_same_block(self):
        # comparing the same blocks should obviously give a score of 1; we would be pretty confident
        # that they are the same block
        self.assertBlockComparisonScore(
            comparer=CharBlockDefComparer,
            old_def=CharBlock(),
            old_name="foo",
            new_def=CharBlock(),
            new_name="foo",
            predicate=self.is_similar,
        )

    def test_diff_kwargs(self):
        # For char blocks with the same names, we can be fairly certain that they are the same block
        # regardless of changes to kwargs.
        self.assertBlockComparisonScore(
            comparer=CharBlockDefComparer,
            old_def=CharBlock(label="FOO", icon="cup"),
            old_name="foo",
            new_def=CharBlock(required=False),
            new_name="foo",
            predicate=self.is_similar,
        )

    def test_diff_name(self):
        # If the name is different, for char blocks we would assume that they are most probably
        # different blocks
        self.assertBlockComparisonScore(
            comparer=CharBlockDefComparer,
            old_def=CharBlock(),
            old_name="foo",
            new_def=CharBlock(),
            new_name="fee",
            predicate=self.is_unsure,
        )
