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

    @expectedFailure
    def test_simple_rename(self):
        """Rename `char1` to `charblock1`"""

        raw_data = [{"type": "char1", "value": "Simple Rename Value"}]
        altered_raw_data = apply_changes_to_raw_data(
            raw_data, "char1", "rename", new_name="charblock1"
        )

        altered_block = altered_raw_data[0]
        self.assertEqual(altered_block["type"], "charblock1")
        self.assertEqual(altered_block["value"], "Simple Rename Value")

    @expectedFailure
    def test_struct_rename(self):
        """Rename `struct1.struct1_char1` to `struct1.struct1_charblock1`"""

        raw_data = [
            {
                "type": "struct1",
                "value": {
                    "struct1_char1": "Struct field rename",
                    "struct1_char2": "This shouldn't change",
                },
            }
        ]
        altered_raw_data = apply_changes_to_raw_data(
            raw_data, "struct1.struct1_char1", "rename", new_name="struct1_charblock1"
        )

        altered_block = altered_raw_data[0]
        self.assertEqual(altered_block["type"], "struct1")
        self.assertEqual(
            altered_block["value"],
            {
                "struct1_charblock1": "Struct field rename",
                "struct1_char2": "This shouldn't change",
            },
        )

    @expectedFailure
    def test_simple_nested_rename(self):
        """Rename `stream1.stream1_char1` to `stream1.stream1_charblock1`"""

        raw_data = [
            {
                "type": "stream1",
                "value": [
                    {"type": "stream1_char1", "value": "Nested Stream field rename"}
                ],
            }
        ]
        altered_raw_data = apply_changes_to_raw_data(
            raw_data, "stream1.stream1_char1", "rename", new_name="stream1_charblock1"
        )

        altered_block = altered_raw_data[0]
        self.assertEqual(altered_block["type"], "stream1")

        altered_nested_block = altered_block["value"][0]
        self.assertEqual(altered_nested_block["type"], "stream1_charblock1")
        self.assertEqual(altered_nested_block["value"], "Nested Stream field rename")

    @expectedFailure
    def test_struct_nested_rename(self):
        """Rename `struct1.struct1_stream1.struct1_stream1_char1` to `struct1.struct1_stream1.renamed1`"""

        raw_data = [
            {
                "type": "struct1",
                "value": {
                    "struct1_stream1": [
                        {"type": "struct1_stream1_char1", "value": "Rename this"}
                    ]
                },
            }
        ]
        altered_raw_data = apply_changes_to_raw_data(
            raw_data,
            "struct1.struct1_stream1.struct1_stream1_char1",
            "rename",
            new_name="renamed1",
        )

        altered_block = altered_raw_data[0]
        self.assertEqual(altered_block["type"], "struct1")
        self.assertTrue("struct1_stream1" in altered_block["value"])

        altered_nested_block = altered_block["value"]["struct1_stream1"][0]
        self.assertEqual(altered_nested_block["type"], "renamed1")
        self.assertEqual(altered_nested_block["value"], "Rename this")
        
    @expectedFailure
    def test_list_nested_rename(self):
        """Rename `list1.stream1_char1` to `list1.renamed1`"""

        raw_data = [
            {
                "type": "list1",
                "value": [
                    {
                        "type": "item",
                        "value": [{"type": "stream1_char1", "value": "Rename this"}],
                    }
                ],
            }
        ]
        altered_raw_data = apply_changes_to_raw_data(
            raw_data,
            "list1.stream1_char1",
            "rename",
            new_name="renamed1",
        )

        altered_block = altered_raw_data[0]
        self.assertEqual(altered_block["type"], "list1")

        list_item = altered_block["value"][0]
        self.assertEqual(list_item["type"], "item")

        altered_nested_block = list_item["value"][0]
        self.assertEqual(altered_nested_block["type"], "renamed1")
        self.assertEqual(altered_nested_block["value"], "Rename this")


class RenameRawDataFullTestCase(TestCase):
    # TODO check wagtail_factories
    # TODO test multiple blocks at once
    # TODO test other blocks intact
    pass


class RenameTestCase(TestCase):
    pass
