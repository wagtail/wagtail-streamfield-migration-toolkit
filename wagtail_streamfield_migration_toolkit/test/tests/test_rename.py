from django.test import TestCase, SimpleTestCase

from wagtail_streamfield_migration_toolkit.utils import apply_changes_to_raw_data
from ..models import SampleModel


class RenameUtilsTestCase(SimpleTestCase):
    pass


class RenameRawDataTestCase(TestCase):
    """
    Tests without saving or loading from the database.
    This is to test just the changes to the raw json data, without considering the schema changes,
    or anything post save.
    """

    # TODO check multiple blocks in one
    # TODO list out all combinations

    def test_simple_rename(self):
        """Rename `char1` to `charblock1`"""

        raw_data = [{"type": "char1", "value": "Simple Rename Value"}]
        altered_raw_data = apply_changes_to_raw_data(
            raw_data, "char1", "rename", new_name="charblock1"
        )

        altered_block = altered_raw_data[0]
        self.assertEqual(altered_block["type"], "charblock1")
        self.assertEqual(altered_block["value"], "Simple Rename Value")

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

    def test_list_nested_rename(self):
        pass

    @staticmethod
    def create_sample_model():
        sample_model = SampleModel(
            content=[
                {
                    "type": "char1",
                    "value": "Simple Rename Value",
                },
                {
                    "type": "char2",
                    "value": "This shouldn't change",
                },
                {
                    "type": "struct1",
                    "value": {
                        "struct1_char1": "Struct field rename",
                        "struct1_char2": "This shouldn't change",
                    },
                },
                {
                    "type": "stream1",
                    "value": [
                        {
                            "type": "stream1_char1",
                            "value": "Nested Stream field rename",
                        },
                        {"type": "stream1_char2", "value": "This shouldn't change"},
                    ],
                },
            ]
        )
        return sample_model

    def test_simple_rename_other_blocks_intact(self):
        """Make sure that other blocks have not changed"""
        sample_model = self.create_sample_model()
        altered_raw_data = apply_changes_to_raw_data(
            sample_model.content.raw_data,
            "char1",
            "rename",
            new_name="charblock1",
        )

        altered_block = altered_raw_data[1]
        self.assertEqual(altered_block["type"], "char2")
        self.assertEqual(altered_block["value"], "This shouldn't change")

    def test_nested_rename_other_blocks_intact(self):
        """Make sure other nested blocks haven't changed"""
        sample_model = self.create_sample_model()
        altered_raw_data = apply_changes_to_raw_data(
            sample_model.content.raw_data,
            "stream1.stream1_char1",
            "rename",
            new_name="stream1_charblock1",
        )

        unaltered_nested_block = altered_raw_data[3]["value"][1]
        self.assertEqual(unaltered_nested_block["type"], "stream1_char2")
        self.assertEqual(unaltered_nested_block["value"], "This shouldn't change")


class RenameTestCase(TestCase):
    pass
