from unittest import expectedFailure
from django.test import TestCase, SimpleTestCase

from wagtail_streamfield_migration_toolkit.utils import apply_changes_to_raw_data
from .. import factories


class RenameUtilsTestCase(SimpleTestCase):
    """
    For testing any utility functions only relevant to renaming.
    """

    pass


class RenameRawDataIndividualTestCase(TestCase):
    """
    Tests with raw json data for different possible block structures involved in renaming.
    Each test here only includes just an instance of the block which is being renamed.

    Check if renamed. Check if value is correct.
    """

    # TODO list out all combinations : struct_struct_nested, stream_struct_nested...
    # TODO write with wagtail-factories (streamblocks, when available)

    @expectedFailure
    def test_simple_rename(self):
        """Rename `char1` to `renamed1`"""

        raw_data = factories.SampleModelFactory(
            content__0__char1__value="Char Block 1"
        ).content.raw_data
        altered_raw_data = apply_changes_to_raw_data(
            raw_data, "char1", "rename", new_name="renamed1"
        )

        altered_block = altered_raw_data[0]
        self.assertEqual(altered_block["type"], "renamed1")
        self.assertEqual(altered_block["value"], "Char Block 1")

    @expectedFailure
    def test_struct_nested_rename(self):
        """Rename `simplestruct.char1` to `simplestruct.renamed1`"""

        raw_data = factories.SampleModelFactory(
            content__0__simplestruct__label="SimpleStruct 1"
        ).content.raw_data
        altered_raw_data = apply_changes_to_raw_data(
            raw_data, "simplestruct.char1", "rename", new_name="renamed1"
        )

        altered_block = altered_raw_data[0]
        self.assertNotIn("char1", altered_block["value"])
        self.assertIn("char2", altered_block["value"])
        self.assertIn("renamed1", altered_block["value"])
        self.assertEqual(altered_block["value"]["renamed1"], "Char Block 1")

    @expectedFailure
    def test_stream_nested_rename(self):
        # TODO streamblock, write in wagtail-factories when available
        """Rename `simplestream.char1` to `simplestream.renamed1`"""

        raw_data = [
            {
                "type": "simplestream",
                "value": [{"type": "char1", "value": "Char Block 1"}],
            }
        ]
        altered_raw_data = apply_changes_to_raw_data(
            raw_data, "simplestream.char1", "rename", new_name="renamed1"
        )

        altered_nested_block = altered_raw_data[0]["value"][0]
        self.assertEqual(altered_nested_block["type"], "renamed1")
        self.assertEqual(altered_nested_block["value"], "Char Block 1")

    @expectedFailure
    def test_struct_stream_nested_rename(self):
        # TODO streamblock, write in wagtail-factories when available
        """Rename `nestedstruct.stream1.char1` to `nestedstruct.stream1.renamed1`"""

        raw_data = [
            {
                "type": "nestedstruct",
                "value": {"stream1": [{"type": "char1", "value": "Char Block 1"}]},
            }
        ]
        altered_raw_data = apply_changes_to_raw_data(
            raw_data,
            "nestedstruct.stream1.char1",
            "rename",
            new_name="renamed1",
        )

        altered_nested_block = altered_raw_data[0]["value"]["stream1"][0]
        self.assertEqual(altered_nested_block["type"], "renamed1")
        self.assertEqual(altered_nested_block["value"], "Char Block 1")

    @expectedFailure
    def test_list_stream_nested_rename(self):
        # TODO streamblock, write in wagtail-factories when available
        """Rename `nestedlist_stream.char1` to `nestedlist_stream.renamed1`"""

        raw_data = [
            {
                "type": "nestedlist_stream",
                "value": [
                    {
                        "type": "item",
                        "value": [{"type": "char1", "value": "Char Block 1"}],
                    }
                ],
            }
        ]
        altered_raw_data = apply_changes_to_raw_data(
            raw_data,
            "nestedlist_stream.char1",
            "rename",
            new_name="renamed1",
        )

        list_item = altered_raw_data[0]["value"][0]
        altered_nested_block = list_item["value"][0]
        self.assertEqual(altered_nested_block["type"], "renamed1")
        self.assertEqual(altered_nested_block["value"], "Char Block 1")

    @expectedFailure
    def test_list_struct_nested_rename(self):
        """Rename `nestedlist_struct.char1` to `nestedlist_struct.renamed1`"""

        raw_data = factories.SampleModelFactory(
            content__0__nestedlist_struct__0__label="NestedList Struct1"
        ).content.raw_data
        altered_raw_data = apply_changes_to_raw_data(
            raw_data,
            "nestedlist_struct.char1",
            "rename",
            new_name="renamed1",
        )

        list_item = altered_raw_data[0]["value"][0]
        altered_nested_block = list_item["value"]
        self.assertNotIn("char1", altered_nested_block)
        self.assertIn("renamed1", altered_nested_block)
        self.assertEqual(altered_nested_block["renamed1"], "Char Block 1")


class RenameRawDataMultipleBlocksTestCase(TestCase):
    """
    Test whether changes are applied to all blocks when multiple blocks are there.
    Test whether other blocks are intact.
    """

    # TODO complete remaining nested tests

    @expectedFailure
    def test_simple_rename_multiple(self):
        """Rename `char1` to `renamed1`"""

        raw_data = factories.SampleModelFactory(
            content__0__char1__value="Char Block 1",
            content__1__char2__value="Char Block 2",
            content__2__char1__value="Char Block 1",
        ).content.raw_data

        altered_raw_data = apply_changes_to_raw_data(raw_data, "char1", "rename")

        self.assertEqual(altered_raw_data[0]["type"], "renamed1")
        self.assertEqual(altered_raw_data[1]["type"], "char2")
        self.assertEqual(altered_raw_data[2]["type"], "renamed1")

    @expectedFailure
    def test_struct_nested_rename(self):
        """Rename `simplestruct.char1` to `simplestruct.renamed1`"""

        raw_data = factories.SampleModelFactory(
            content__0__char1__value="Char Block 1",
            content__1__simplestruct__label="SimpleStruct 1",
            content__2__simplestruct__label="SimpleStruct 2",
        ).content.raw_data

        altered_raw_data = apply_changes_to_raw_data(
            raw_data, "simplestruct.char1", "rename"
        )

        self.assertEqual(altered_raw_data[0]["type"], "char1")
        self.assertEqual(altered_raw_data[1]["type"], "simplestruct")
        self.assertEqual(altered_raw_data[2]["type"], "simplestruct")

        self.assertNotIn("char1", altered_raw_data[1]["value"])
        self.assertNotIn("char1", altered_raw_data[2]["value"])
        self.assertIn("renamed1", altered_raw_data[1]["value"])
        self.assertIn("renamed1", altered_raw_data[2]["value"])
        self.assertIn("char2", altered_raw_data[1]["value"])
        self.assertIn("char2", altered_raw_data[2]["value"])

    @expectedFailure
    def test_list_struct_nested_rename(self):
        """Rename `nestedlist_struct.char1` to `nestedlist_struct.renamed1`"""

        raw_data = factories.SampleModelFactory(
            content__0__char1__value="Char Block 1",
            content__1__nestedlist_struct__0__label="NestedList Struct 1",
            content__1__nestedlist_struct__1__label="NestedList Struct 2",
            content__2__nestedlist_struct__0__label="NestedList Struct 3",
        ).content.raw_data

        altered_raw_data = apply_changes_to_raw_data(
            raw_data, "nestedlist_struct.char1", "rename"
        )

        self.assertEqual(altered_raw_data[0]["type"], "char1")
        self.assertEqual(altered_raw_data[1]["type"], "nestedlist_struct")
        self.assertEqual(altered_raw_data[2]["type"], "nestedlist_struct")

        self.assertNotIn("char1", altered_raw_data[1]["value"][0]["value"])
        self.assertNotIn("char1", altered_raw_data[1]["value"][1]["value"])
        self.assertNotIn("char1", altered_raw_data[2]["value"][0]["value"])
        self.assertIn("renamed1", altered_raw_data[1]["value"][0]["value"])
        self.assertIn("renamed1", altered_raw_data[1]["value"][1]["value"])
        self.assertIn("renamed1", altered_raw_data[2]["value"][0]["value"])
        self.assertIn("char2", altered_raw_data[1]["value"][0]["value"])
        self.assertIn("char2", altered_raw_data[1]["value"][1]["value"])
        self.assertIn("char2", altered_raw_data[2]["value"][0]["value"])


class RenameFullTestCase(TestCase):
    pass
