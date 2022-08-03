from django.test import TestCase

from .. import models
from wagtail_streamfield_migration_toolkit.utils import apply_changes_to_raw_data
from wagtail_streamfield_migration_toolkit.operations import (
    RenameStreamChildrenOperation,
    RenameStructChildrenOperation,
)


class OldListFormatNestedStreamTestCase(TestCase):
    """TODO complete

    recursion process
    """

    @classmethod
    def setUpTestData(cls):
        raw_data = [
            {"type": "char1", "id": "0001", "value": "Char Block 1"},
            {
                "type": "nestedlist_stream",
                "id": "0002",
                "value": [
                    [
                        {"type": "char1", "id": "0003", "value": "Char Block 1"},
                        {"type": "char2", "id": "0004", "value": "Char Block 2"},
                        {"type": "char1", "id": "0005", "value": "Char Block 1"},
                    ],
                    [
                        {"type": "char1", "id": "0006", "value": "Char Block 1"},
                    ],
                ],
            },
            {
                "type": "nestedlist_stream",
                "id": "0007",
                "value": [
                    [
                        {"type": "char1", "id": "0008", "value": "Char Block 1"},
                    ]
                ],
            },
        ]
        cls.raw_data = raw_data

    def test_list_converted_to_new_format(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "nestedlist_stream.item",
            RenameStreamChildrenOperation(old_name="char1", new_name="renamed1"),
            streamfield=models.SampleModel.content,
        )

        for listitem in altered_raw_data[1]["value"]:
            self.assertIsInstance(listitem, dict)
            self.assertIn("type", listitem)
            self.assertIn("value", listitem)
            self.assertEqual(listitem["type"], "item")

        for listitem in altered_raw_data[2]["value"]:
            self.assertIsInstance(listitem, dict)
            self.assertIn("type", listitem)
            self.assertIn("value", listitem)
            self.assertEqual(listitem["type"], "item")

    def test_rename(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "nestedlist_stream.item",
            RenameStreamChildrenOperation(old_name="char1", new_name="renamed1"),
            streamfield=models.SampleModel.content,
        )

        self.assertEqual(
            altered_raw_data[1]["value"][0]["value"][0]["type"], "renamed1"
        )
        self.assertEqual(
            altered_raw_data[1]["value"][0]["value"][2]["type"], "renamed1"
        )
        self.assertEqual(
            altered_raw_data[1]["value"][1]["value"][0]["type"], "renamed1"
        )
        self.assertEqual(
            altered_raw_data[2]["value"][0]["value"][0]["type"], "renamed1"
        )

        self.assertEqual(
            altered_raw_data[1]["value"][0]["value"][0]["id"],
            self.raw_data[1]["value"][0][0]["id"],
        )
        self.assertEqual(
            altered_raw_data[1]["value"][0]["value"][2]["id"],
            self.raw_data[1]["value"][0][2]["id"],
        )
        self.assertEqual(
            altered_raw_data[1]["value"][1]["value"][0]["id"],
            self.raw_data[1]["value"][1][0]["id"],
        )
        self.assertEqual(
            altered_raw_data[2]["value"][0]["value"][0]["id"],
            self.raw_data[2]["value"][0][0]["id"],
        )

        self.assertEqual(
            altered_raw_data[1]["value"][0]["value"][0]["value"],
            self.raw_data[1]["value"][0][0]["value"],
        )
        self.assertEqual(
            altered_raw_data[1]["value"][0]["value"][2]["value"],
            self.raw_data[1]["value"][0][2]["value"],
        )
        self.assertEqual(
            altered_raw_data[1]["value"][1]["value"][0]["value"],
            self.raw_data[1]["value"][1][0]["value"],
        )
        self.assertEqual(
            altered_raw_data[2]["value"][0]["value"][0]["value"],
            self.raw_data[2]["value"][0][0]["value"],
        )

        self.assertEqual(
            altered_raw_data[1]["value"][0]["value"][1],
            self.raw_data[1]["value"][0][1],
        )


class OldListFormatNestedStructTestCase(TestCase):
    """TODO complete

    recursion process
    """

    @classmethod
    def setUpTestData(cls):
        raw_data = [
            {"type": "char1", "id": "0001", "value": "Char Block 1"},
            {
                "type": "nestedlist_struct",
                "id": "0002",
                "value": [
                    {"char1": "Char Block 1", "char2": "Char Block 2"},
                    {"char1": "Char Block 1", "char2": "Char Block 2"},
                ],
            },
            {
                "type": "nestedlist_struct",
                "id": "0007",
                "value": [
                    {"char1": "Char Block 1", "char2": "Char Block 2"},
                ],
            },
        ]
        cls.raw_data = raw_data

    def test_list_converted_to_new_format(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "nestedlist_struct.item",
            RenameStructChildrenOperation(old_name="char1", new_name="renamed1"),
            streamfield=models.SampleModel.content,
        )

        for listitem in altered_raw_data[1]["value"]:
            self.assertIsInstance(listitem, dict)
            self.assertIn("type", listitem)
            self.assertIn("value", listitem)
            self.assertEqual(listitem["type"], "item")

        for listitem in altered_raw_data[2]["value"]:
            self.assertIsInstance(listitem, dict)
            self.assertIn("type", listitem)
            self.assertIn("value", listitem)
            self.assertEqual(listitem["type"], "item")

    def test_rename(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "nestedlist_struct.item",
            RenameStructChildrenOperation(old_name="char1", new_name="renamed1"),
            streamfield=models.SampleModel.content,
        )

        self.assertNotIn("char1", altered_raw_data[1]["value"][0]["value"])
        self.assertNotIn("char1", altered_raw_data[1]["value"][1]["value"])
        self.assertNotIn("char1", altered_raw_data[2]["value"][0]["value"])
        self.assertIn("renamed1", altered_raw_data[1]["value"][0]["value"])
        self.assertIn("renamed1", altered_raw_data[1]["value"][1]["value"])
        self.assertIn("renamed1", altered_raw_data[2]["value"][0]["value"])
        self.assertEqual(
            altered_raw_data[1]["value"][0]["value"]["renamed1"],
            self.raw_data[1]["value"][0]["char1"],
        )
        self.assertEqual(
            altered_raw_data[1]["value"][1]["value"]["renamed1"],
            self.raw_data[1]["value"][1]["char1"],
        )
        self.assertEqual(
            altered_raw_data[2]["value"][0]["value"]["renamed1"],
            self.raw_data[2]["value"][0]["char1"],
        )

        self.assertIn("char2", altered_raw_data[1]["value"][0]["value"])
        self.assertIn("char2", altered_raw_data[1]["value"][1]["value"])
        self.assertIn("char2", altered_raw_data[2]["value"][0]["value"])
        self.assertEqual(
            altered_raw_data[1]["value"][0]["value"]["char2"],
            self.raw_data[1]["value"][0]["char2"],
        )
        self.assertEqual(
            altered_raw_data[1]["value"][1]["value"]["char2"],
            self.raw_data[1]["value"][1]["char2"],
        )
        self.assertEqual(
            altered_raw_data[2]["value"][0]["value"]["char2"],
            self.raw_data[2]["value"][0]["char2"],
        )
