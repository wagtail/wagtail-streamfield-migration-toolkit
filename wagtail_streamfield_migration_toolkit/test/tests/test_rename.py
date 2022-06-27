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
    Each test here only includes just the
    """

    # TODO list out all combinations
    # TODO test multiple blocks at once
    # TODO write with wagtail-factories

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
        self.assertEqual(altered_block["type"], "simplestruct")
        self.assertNotIn("char1", altered_block["value"])
        self.assertIn("char2", altered_block["value"])

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

        altered_block = altered_raw_data[0]
        self.assertEqual(altered_block["type"], "simplestream")

        altered_nested_block = altered_block["value"][0]
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

        altered_block = altered_raw_data[0]
        self.assertEqual(altered_block["type"], "nestedstruct")
        self.assertIn("stream1", altered_block["value"])

        altered_nested_block = altered_block["value"]["stream1"][0]
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
        

        altered_block = altered_raw_data[0]
        self.assertEqual(altered_block["type"], "nestedlist_stream")

        list_item = altered_block["value"][0]
        self.assertEqual(list_item["type"], "item")

        altered_nested_block = list_item["value"][0]
        self.assertEqual(altered_nested_block["type"], "renamed1")
        self.assertEqual(altered_nested_block["value"], "Char Block 1")

    # @expectedFailure
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
        

        altered_block = altered_raw_data[0]
        self.assertEqual(altered_block["type"], "nestedlist_struct")

        list_item = altered_block["value"][0]
        self.assertEqual(list_item["type"], "item")

        altered_nested_block = list_item["value"]
        self.assertIn("renamed1", altered_nested_block)
        self.assertNotIn("char1", altered_nested_block)


class RenameRawDataFullTestCase(TestCase):
    # TODO test other blocks intact
    pass


class RenameTestCase(TestCase):
    pass
