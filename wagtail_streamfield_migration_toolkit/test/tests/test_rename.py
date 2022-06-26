from unittest import expectedFailure
from django.test import TestCase, SimpleTestCase

from wagtail_streamfield_migration_toolkit.utils import apply_changes_to_raw_data


class RenameUtilsTestCase(SimpleTestCase):
    """
    For testing any utility functions only relevant to renaming.
    """

    pass


class RenameRawDataIndividualTestCase(SimpleTestCase):
    """
    Tests with raw json data for different possible block structures involved in renaming.
    Each test here only includes just the
    """

    # TODO list out all combinations
    # TODO test multiple blocks at once
    # TODO write with wagtail-factories

    @expectedFailure
    def test_simple_rename(self):
        """Rename `char1` to `renamed1`"""

        raw_data = [{"type": "char1", "value": "Char Block 1"}]
        altered_raw_data = apply_changes_to_raw_data(
            raw_data, "char1", "rename", new_name="renamed1"
        )

        altered_block = altered_raw_data[0]
        self.assertEqual(altered_block["type"], "renamed1")
        self.assertEqual(altered_block["value"], "Char Block 1")

    @expectedFailure
    def test_struct_nested_rename(self):
        """Rename `simplestruct.char1` to `simplestruct.renamed1`"""

        raw_data = [
            {
                "type": "simplestruct",
                "value": {
                    "char1": "Char Block 1",
                    "char2": "Char Block 2",
                },
            }
        ]
        altered_raw_data = apply_changes_to_raw_data(
            raw_data, "simplestruct.char1", "rename", new_name="renamed1"
        )

        altered_block = altered_raw_data[0]
        self.assertEqual(altered_block["type"], "simplestruct")
        self.assertEqual(
            altered_block["value"],
            {
                "renamed1": "Char Block 1",
                "char2": "Char Block 2",
            },
        )

    @expectedFailure
    def test_stream_nested_rename(self):
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

        altered_block = altered_raw_data[0]
        self.assertEqual(altered_block["type"], "simplestream")

        altered_nested_block = altered_block["value"][0]
        self.assertEqual(altered_nested_block["type"], "renamed1")
        self.assertEqual(altered_nested_block["value"], "Char Block 1")

    @expectedFailure
    def test_struct_stream_nested_rename(self):
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

        altered_block = altered_raw_data[0]
        self.assertEqual(altered_block["type"], "nestedstruct")
        self.assertTrue("stream1" in altered_block["value"])

        altered_nested_block = altered_block["value"]["stream1"][0]
        self.assertEqual(altered_nested_block["type"], "renamed1")
        self.assertEqual(altered_nested_block["value"], "Char Block 1")

    @expectedFailure
    def test_list_stream_nested_rename(self):
        """Rename `nestedlist.char1` to `nestedlist.renamed1`"""

        raw_data = [
            {
                "type": "nestedlist",
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
            "nestedlist.char1",
            "rename",
            new_name="renamed1",
        )

        altered_block = altered_raw_data[0]
        self.assertEqual(altered_block["type"], "nestedlist")

        list_item = altered_block["value"][0]
        self.assertEqual(list_item["type"], "item")

        altered_nested_block = list_item["value"][0]
        self.assertEqual(altered_nested_block["type"], "renamed1")
        self.assertEqual(altered_nested_block["value"], "Char Block 1")


class RenameRawDataFullTestCase(TestCase):
    # TODO test other blocks intact
    pass


class RenameTestCase(TestCase):
    pass
