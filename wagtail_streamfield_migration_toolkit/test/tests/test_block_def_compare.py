from django.test import TestCase
from wagtail.blocks import (
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
    # DefaultBlockDefComparer,
    StreamBlockDefComparer,
    StructBlockDefComparer,
)


class ThreeFieldStruct(StructBlock):
    char_block = CharBlock()
    int_block = IntegerBlock()
    date_block = DateBlock()


class FourFieldStruct(ThreeFieldStruct):
    list_char_block = ListBlock(CharBlock())


class DiffThreeFieldStruct(StructBlock):
    my_text = TextBlock()
    my_int = IntegerBlock()
    my_boolean = BooleanBlock()


class BlockComparerTestCase(TestCase):
    def assertBlocksAlmostEqual(
        self,
        comparer,
        old_def,
        old_name,
        new_def,
        new_name,
        arg_similarity=1,
        child_similarity=1,
        name_similarity=1,
    ):
        comparison_score = comparer.compare(
            old_def=old_def, old_name=old_name, new_def=new_def, new_name=new_name
        )
        expected_score = (
            comparer.arg_weight * arg_similarity
            + comparer.child_weight * child_similarity
            + comparer.name_weight * name_similarity
        ) / (comparer.arg_weight + comparer.child_weight + comparer.name_weight)
        self.assertAlmostEqual(comparison_score, expected_score, delta=0.01)


class TestStructBlocks(BlockComparerTestCase):
    def test(self):
        # These will need to change if we change the logic for comparison

        self.assertBlocksAlmostEqual(
            comparer=StructBlockDefComparer,
            old_def=FourFieldStruct(),
            old_name="foo",
            new_def=ThreeFieldStruct(),
            new_name="foo",
            child_similarity=3 / 4,
        )

        self.assertBlocksAlmostEqual(
            comparer=StructBlockDefComparer,
            old_def=ThreeFieldStruct(),
            old_name="foo",
            new_def=FourFieldStruct(),
            new_name="foo",
        )

        self.assertBlocksAlmostEqual(
            comparer=StructBlockDefComparer,
            old_def=ThreeFieldStruct(),
            old_name="foo",
            new_def=DiffThreeFieldStruct(),
            new_name="foo",
            child_similarity=0,
        )


class ThreeFieldStream(StreamBlock):
    char_block = CharBlock()
    int_block = IntegerBlock()
    date_block = DateBlock()


class FourFieldStream(ThreeFieldStream):
    list_char_block = ListBlock(CharBlock())


class DiffThreeFieldStream(StreamBlock):
    my_text = TextBlock()
    my_int = IntegerBlock()
    my_boolean = BooleanBlock()


class TestStreamBlocks(BlockComparerTestCase):
    def test(self):
        # These will need to change if we change the logic for comparison

        self.assertBlocksAlmostEqual(
            comparer=StreamBlockDefComparer,
            old_def=FourFieldStream(),
            old_name="foo",
            new_def=ThreeFieldStream(),
            new_name="foo",
            child_similarity=3 / 4,
        )

        self.assertBlocksAlmostEqual(
            comparer=StreamBlockDefComparer,
            old_def=ThreeFieldStream(),
            old_name="foo",
            new_def=FourFieldStream(),
            new_name="foo",
        )

        self.assertBlocksAlmostEqual(
            comparer=StreamBlockDefComparer,
            old_def=ThreeFieldStream(),
            old_name="foo",
            new_def=DiffThreeFieldStream(),
            new_name="foo",
            child_similarity=0,
        )
