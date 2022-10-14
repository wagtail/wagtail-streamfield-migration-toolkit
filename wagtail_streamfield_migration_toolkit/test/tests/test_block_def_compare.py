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
    # ListBlockDefComparer,
    StreamBlockDefComparer,
    StructBlockDefComparer,
)


class ThreeFieldStruct(StructBlock):
    char_block = CharBlock(max_length=255)
    int_block = IntegerBlock()
    date_block = DateBlock()


class FourFieldStruct(ThreeFieldStruct):
    list_char_block = ListBlock(CharBlock())


class DiffThreeFieldStruct(StructBlock):
    my_text = TextBlock()
    my_int = IntegerBlock()
    my_boolean = BooleanBlock()


class NestedStruct1(StructBlock):
    char_block = CharBlock()
    struct_4f = FourFieldStruct()
    struct_3f = ThreeFieldStruct()


class NestedStruct2(StructBlock):
    char_block = CharBlock()
    struct_new3f = ThreeFieldStruct()
    struct_3f = ThreeFieldStruct()


class NestedStruct3(StructBlock):
    char_block = CharBlock()
    struct_4f = FourFieldStruct()
    struct_diff = DiffThreeFieldStruct()


class BlockComparerTestCase(TestCase):
    def assertBlockComparisonScore(
        self,
        comparer,
        old_def,
        old_name,
        new_def,
        new_name,
        name_similarity=1,
        arg_similarity=1,
        kwarg_similarity=1,
    ):
        comparison_score = comparer.compare(
            old_def=old_def, old_name=old_name, new_def=new_def, new_name=new_name
        )
        expected_score = (
            comparer.arg_weight * arg_similarity
            + comparer.name_weight * name_similarity
            + comparer.kwarg_weight * kwarg_similarity
        ) / (comparer.arg_weight + comparer.name_weight + comparer.kwarg_weight)
        self.assertAlmostEqual(comparison_score, expected_score, delta=0.01)

        # TODO roughly is fine, may want to consider whether their within thresholds
        # depending on the blocks being compared


class TestStructBlocks(BlockComparerTestCase):
    # NOTE These will need to change if we change the logic for comparison

    def test_diff_names(self):
        self.assertBlockComparisonScore(
            comparer=StructBlockDefComparer,
            old_def=FourFieldStruct(),
            old_name="foo",
            new_def=FourFieldStruct(),
            new_name="fee",
            name_similarity=0,
        )

    def test_removed_children(self):
        # removed child
        self.assertBlockComparisonScore(
            comparer=StructBlockDefComparer,
            old_def=FourFieldStruct(),
            old_name="foo",
            new_def=ThreeFieldStruct(),
            new_name="foo",
            arg_similarity=3 / 4,
        )

    def test_added_children(self):
        # added child, this would return a score of 1 currently. NOTE change if logic changes to
        # consider additions for children too
        self.assertBlockComparisonScore(
            comparer=StructBlockDefComparer,
            old_def=ThreeFieldStruct(),
            old_name="foo",
            new_def=FourFieldStruct(),
            new_name="foo",
        )

    def test_same_name_diff_children(self):
        # same name, different children
        self.assertBlockComparisonScore(
            comparer=StructBlockDefComparer,
            old_def=ThreeFieldStruct(),
            old_name="foo",
            new_def=DiffThreeFieldStruct(),
            new_name="foo",
            arg_similarity=0,
        )

    def test_nested_child_comparison(self):
        self.assertBlockComparisonScore(
            comparer=StructBlockDefComparer,
            old_def=NestedStruct1(),
            old_name="foo",
            new_def=NestedStruct2(),
            new_name="foo",
            arg_similarity=2 / 3,
        )

    def test_removed_kwargs(self):
        self.assertBlockComparisonScore(
            comparer=StructBlockDefComparer,
            old_def=FourFieldStruct(label="FOO", icon="cup"),
            old_name="foo",
            new_def=FourFieldStruct(),
            new_name="foo",
            kwarg_similarity=0,
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
    # NOTE These will need to change if we change the logic for comparison

    def test_removed_children(self):
        self.assertBlockComparisonScore(
            comparer=StreamBlockDefComparer,
            old_def=FourFieldStream(),
            old_name="foo",
            new_def=ThreeFieldStream(),
            new_name="foo",
            arg_similarity=3 / 4,
        )

    def test_added_children(self):
        # added child, this would return a score of 1 currently. NOTE change if logic changes to
        # consider additions for children too
        self.assertBlockComparisonScore(
            comparer=StreamBlockDefComparer,
            old_def=ThreeFieldStream(),
            old_name="foo",
            new_def=FourFieldStream(),
            new_name="foo",
        )

    def test_same_name_diff_children(self):
        # same name, different children
        self.assertBlockComparisonScore(
            comparer=StreamBlockDefComparer,
            old_def=ThreeFieldStream(),
            old_name="foo",
            new_def=DiffThreeFieldStream(),
            new_name="foo",
            arg_similarity=0,
        )
