from django.test import TestCase

from .. import factories, models
from wagtail_streamfield_migration_toolkit.utils import apply_changes_to_raw_data
from wagtail_streamfield_migration_toolkit.operations import (
    RenameStreamChildrenOperation,
    RenameStructChildrenOperation,
    RemoveStreamChildrenOperation,
    RemoveStructChildrenOperation,
)


# TODO add asserts for ids


class FieldChildBlockTest(TestCase):
    """Changes to `char1`"""

    @classmethod
    def setUpTestData(cls):
        raw_data = factories.SampleModelFactory(
            content__0__char1__value="Char Block 1",
            content__1__char2__value="Char Block 2",
            content__2__char1__value="Char Block 1",
        ).content.raw_data
        cls.raw_data = raw_data

    def test_rename(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "",
            RenameStreamChildrenOperation(old_name="char1", new_name="renamed1"),
            streamfield=models.SampleModel.content,
        )

        self.assertEqual(altered_raw_data[0]["type"], "renamed1")
        self.assertEqual(altered_raw_data[2]["type"], "renamed1")

        self.assertEqual(altered_raw_data[0]["value"], "Char Block 1")
        self.assertEqual(altered_raw_data[2]["value"], "Char Block 1")

    def test_rename_rest_intact(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "",
            RenameStreamChildrenOperation(old_name="char1", new_name="renamed1"),
            streamfield=models.SampleModel.content,
        )

        self.assertEqual(altered_raw_data[1]["type"], "char2")

    def test_remove(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "",
            RemoveStreamChildrenOperation(name="char1"),
            streamfield=models.SampleModel.content,
        )

        self.assertEqual(len(altered_raw_data), 1)
        self.assertEqual(altered_raw_data[0]["type"], "char2")

    def test_to_listblock(self):
        pass

    def test_to_streamblock(self):
        pass


class FieldStructChildBlockTest(TestCase):
    """Changes to `simplestruct.char1`"""

    @classmethod
    def setUpTestData(cls):
        raw_data = factories.SampleModelFactory(
            content__0__char1__value="Char Block 1",
            content__1="simplestruct",
            content__2="simplestruct",
        ).content.raw_data
        cls.raw_data = raw_data

    def test_rename(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "simplestruct",
            RenameStructChildrenOperation(old_name="char1", new_name="renamed1"),
            streamfield=models.SampleModel.content,
        )

        self.assertNotIn("char1", altered_raw_data[1]["value"])
        self.assertNotIn("char1", altered_raw_data[2]["value"])
        self.assertIn("renamed1", altered_raw_data[1]["value"])
        self.assertIn("renamed1", altered_raw_data[2]["value"])

    def test_rename_rest_intact(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "simplestruct",
            RenameStructChildrenOperation(old_name="char1", new_name="renamed1"),
            streamfield=models.SampleModel.content,
        )

        self.assertEqual(altered_raw_data[0]["type"], "char1")
        self.assertEqual(altered_raw_data[1]["type"], "simplestruct")
        self.assertEqual(altered_raw_data[2]["type"], "simplestruct")

        self.assertIn("char2", altered_raw_data[1]["value"])
        self.assertIn("char2", altered_raw_data[2]["value"])

    def test_remove(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "simplestruct",
            RemoveStructChildrenOperation(name="char1"),
            streamfield=models.SampleModel.content,
        )

        self.assertEqual(len(altered_raw_data[1]["value"]), 1)
        self.assertEqual(len(altered_raw_data[2]["value"]), 1)
        self.assertNotIn("char1", altered_raw_data[1]["value"])
        self.assertNotIn("char1", altered_raw_data[2]["value"])

    def test_remove_rest_intact(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "simplestruct",
            RemoveStructChildrenOperation(name="char1"),
            streamfield=models.SampleModel.content,
        )

        self.assertEqual(len(altered_raw_data), 3)

        self.assertIn("char2", altered_raw_data[1]["value"])
        self.assertIn("char2", altered_raw_data[2]["value"])


class FieldStreamChildBlock(TestCase):
    """Changes to `simplestream.char1`"""

    @classmethod
    def setUpTestData(cls):
        # TODO until support is available from wagtail-factories, manually write.
        raw_data = [
            {"type": "char1", "value": "Char Block 1"},
            {
                "type": "simplestream",
                "value": [
                    {"type": "char1", "value": "Char Block 1"},
                    {"type": "char2", "value": "Char Block 2"},
                    {"type": "char1", "value": "Char Block 1"},
                ],
            },
            {
                "type": "simplestream",
                "value": [{"type": "char1", "value": "Char Block 1"}],
            },
        ]
        cls.raw_data = raw_data

    def test_rename(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "simplestream",
            RenameStreamChildrenOperation(old_name="char1", new_name="renamed1"),
            streamfield=models.SampleModel.content,
        )

        self.assertEqual(altered_raw_data[1]["value"][0]["type"], "renamed1")
        self.assertEqual(altered_raw_data[1]["value"][2]["type"], "renamed1")
        self.assertEqual(altered_raw_data[2]["value"][0]["type"], "renamed1")

    def test_rename_rest_intact(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "simplestream",
            RenameStreamChildrenOperation(old_name="char1", new_name="renamed1"),
            streamfield=models.SampleModel.content,
        )

        self.assertEqual(altered_raw_data[0]["type"], "char1")
        self.assertEqual(altered_raw_data[1]["type"], "simplestream")
        self.assertEqual(altered_raw_data[2]["type"], "simplestream")

        self.assertEqual(altered_raw_data[1]["value"][1]["type"], "char2")

    def test_remove(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "simplestream",
            RemoveStreamChildrenOperation(name="char1"),
            streamfield=models.SampleModel.content,
        )

        self.assertEqual(len(altered_raw_data[1]["value"]), 1)
        self.assertEqual(len(altered_raw_data[2]["value"]), 0)

    def test_remove_rest_intact(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "simplestream",
            RemoveStreamChildrenOperation(name="char1"),
            streamfield=models.SampleModel.content,
        )

        self.assertEqual(len(altered_raw_data), 3)

        self.assertEqual(altered_raw_data[1]["value"][0]["type"], "char2")
