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
            StructBlockDefComparer.compare(FourFieldStruct(), ThreeFieldStruct()),
            3 / 4,
            delta=0.01,
        )

        self.assertAlmostEqual(
            StructBlockDefComparer.compare(ThreeFieldStruct(), FourFieldStruct()),
            3 / 3,
            delta=0.01,
        )

        self.assertAlmostEqual(
            StructBlockDefComparer.compare(ThreeFieldStruct(), DiffThreeFieldStruct()),
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
            StreamBlockDefComparer.compare(FourFieldStream(), ThreeFieldStream()),
            3 / 4,
            delta=0.01,
        )

        self.assertAlmostEqual(
            StreamBlockDefComparer.compare(ThreeFieldStream(), FourFieldStream()),
            3 / 3,
            delta=0.01,
        )

        self.assertAlmostEqual(
            StreamBlockDefComparer.compare(ThreeFieldStream(), DiffThreeFieldStream()),
            0 / 3,
            delta=0.01,
        )
