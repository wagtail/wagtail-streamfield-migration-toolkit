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


class TestStructBlocks(TestCase):
    def test(self):
        # These will need to change if we change the logic for comparison

        self.assertAlmostEqual(
            StructBlockDefComparer.compare(
                old_def=FourFieldStruct(),
                old_name="foo",
                new_def=ThreeFieldStruct(),
                new_name="foo",
            ),
            3 / 4,
            delta=0.01,
        )

        self.assertAlmostEqual(
            StructBlockDefComparer.compare(
                old_def=ThreeFieldStruct(),
                old_name="foo",
                new_def=FourFieldStruct(),
                new_name="foo",
            ),
            3 / 3,
            delta=0.01,
        )

        self.assertAlmostEqual(
            StructBlockDefComparer.compare(
                old_def=ThreeFieldStruct(),
                old_name="foo",
                new_def=DiffThreeFieldStruct(),
                new_name="foo",
            ),
            0 / 3,
            delta=0.01,
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


class TestStreamBlocks(TestCase):
    def test(self):
        # These will need to change if we change the logic for comparison

        self.assertAlmostEqual(
            StreamBlockDefComparer.compare(
                old_def=FourFieldStream(),
                old_name="foo",
                new_def=ThreeFieldStream(),
                new_name="foo",
            ),
            3 / 4,
            delta=0.01,
        )

        self.assertAlmostEqual(
            StreamBlockDefComparer.compare(
                old_def=ThreeFieldStream(),
                old_name="foo",
                new_def=FourFieldStream(),
                new_name="foo",
            ),
            3 / 3,
            delta=0.01,
        )

        self.assertAlmostEqual(
            StreamBlockDefComparer.compare(
                old_def=ThreeFieldStream(),
                old_name="foo",
                new_def=DiffThreeFieldStream(),
                new_name="foo",
            ),
            0 / 3,
            delta=0.01,
        )
