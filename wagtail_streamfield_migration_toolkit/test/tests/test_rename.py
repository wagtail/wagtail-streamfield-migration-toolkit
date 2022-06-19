from django.test import TestCase, SimpleTestCase

from wagtail_streamfield_migration_toolkit.utils import get_altered_raw_data
from ..models import SampleModel


class RenameUtilsTestCase(SimpleTestCase):
    @staticmethod
    def make_json_data():
        stream_data = [
            {
                "type": "field1",
                "value": "Simple Rename Value",
            },
            {
                "type": "field2",
                "value": "This shouldn't change",
            },
            {
                "type": "struct1",
                "value": {
                    "struct1field1": "Struct field rename",
                    "struct1field2": "This shouldn't change",
                },
            },
            {
                "type": "stream1",
                "value": [
                    {"type": "stream1field1", "value": "Nested Stream field rename"},
                    {"type": "stream1field2", "value": "This shouldn't change"},
                ],
            },
        ]
        return stream_data


class RenameRawDataTestCase(TestCase):
    """
    Tests without saving or loading from the database.
    This is to test just the changes to the raw json data, without considering the schema changes,
    or anything post save.
    """

    @staticmethod
    def create_sample_page():
        sample_page = SampleModel(
            content=[
                {
                    "type": "field1",
                    "value": "Simple Rename Value",
                },
                {
                    "type": "field2",
                    "value": "This shouldn't change",
                },
                {
                    "type": "struct1",
                    "value": {
                        "struct1field1": "Struct field rename",
                        "struct1field2": "This shouldn't change",
                    },
                },
                {
                    "type": "stream1",
                    "value": [
                        {
                            "type": "stream1field1",
                            "value": "Nested Stream field rename",
                        },
                        {"type": "stream1field2", "value": "This shouldn't change"},
                    ],
                },
            ]
        )
        return sample_page

    def test_simple_rename(self):
        """Rename `field1` to `block1`"""
        sample_page = self.create_sample_page()
        altered_raw_data = get_altered_raw_data(
            sample_page.content.raw_data,
            "field1",
            "block1",
        )

        altered_block = altered_raw_data[0]
        self.assertEqual(altered_block["type"], "block1")
        self.assertEqual(altered_block["value"], "Simple Rename Value")

    def test_other_blocks_intact(self):
        """Make sure that other blocks have not changed"""
        sample_page = self.create_sample_page()
        altered_raw_data = get_altered_raw_data(
            sample_page.content.raw_data,
            "field1",
            "block1",
        )

        altered_block = altered_raw_data[1]
        self.assertEqual(altered_block["type"], "field2")
        self.assertEqual(altered_block["value"], "This shouldn't change")

    def test_struct_rename(self):
        """Rename `struct1.struct1field1` to `struct1.struct1block1`"""
        sample_page = self.create_sample_page()
        altered_raw_data = get_altered_raw_data(
            sample_page.content.raw_data,
            "struct1.struct1field1",
            "struct1block1",
        )

        altered_block = altered_raw_data[2]
        self.assertEqual(altered_block["type"], "struct1")
        self.assertEqual(
            altered_block["value"],
            {
                "struct1block1": "Struct field rename",
                "struct1field2": "This shouldn't change",
            },
        )

    def test_nested_rename(self):
        """Rename `stream1.stream1field1` to `stream1.stream1block1`"""
        sample_page = self.create_sample_page()
        altered_raw_data = get_altered_raw_data(
            sample_page.content._raw_data,
            "stream1.stream1field1",
            "stream1block1",
        )

        altered_block = altered_raw_data[3]
        self.assertEqual(altered_block["type"], "stream1")

        altered_nested_block = altered_block["value"][0]
        self.assertEqual(altered_nested_block["type"], "stream1block1")
        self.assertEqual(altered_nested_block["value"], "Nested Stream field rename")

    def test_nested_rename_other_blocks_intact(self):
        """Make sure other nested blocks haven't changed"""
        sample_page = self.create_sample_page()
        altered_raw_data = get_altered_raw_data(
            sample_page.content.raw_data,
            "stream1.stream1field1",
            "stream1block1",
        )

        unaltered_nested_block = altered_raw_data[3]["value"][1]
        self.assertEqual(unaltered_nested_block["type"], "stream1field2")
        self.assertEqual(unaltered_nested_block["value"], "This shouldn't change")


class RenameTestCase(TestCase):
    pass
