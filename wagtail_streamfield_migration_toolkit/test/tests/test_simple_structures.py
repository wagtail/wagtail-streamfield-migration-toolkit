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
    """Tests involving changes to top level blocks"""

    @classmethod
    def setUpTestData(cls):
        raw_data = factories.SampleModelFactory(
            content__0__char1__value="Char Block 1",
            content__1__char2__value="Char Block 2",
            content__2__char1__value="Char Block 1",
            content__3__char2__value="Char Block 2",
        ).content.raw_data
        cls.raw_data = raw_data

    def test_rename(self):
        """Rename `char1` blocks to `renamed1`

        Check whether all char1 blocks have been renamed correctly.
        Check whether other blocks are intact.
        """

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

        self.assertEqual(altered_raw_data[1]["type"], "char2")
        self.assertEqual(altered_raw_data[3]["type"], "char2")

    def test_remove(self):
        """Remove all `char1` blocks

        Check whether all `char1` blocks have been removed.
        Check whether other blocks are intact.
        """
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "",
            RemoveStreamChildrenOperation(name="char1"),
            streamfield=models.SampleModel.content,
        )

        self.assertEqual(len(altered_raw_data), 2)
        self.assertEqual(altered_raw_data[0]["type"], "char2")
        self.assertEqual(altered_raw_data[1]["type"], "char2")

    def test_to_listblock(self):
        pass

    def test_to_streamblock(self):
        pass


class FieldStructChildBlockTest(TestCase):
    """Tests involving changes to direct children of a StructBlock

    We use `simplestruct` blocks as the StructBlocks here.
    """

    @classmethod
    def setUpTestData(cls):
        raw_data = factories.SampleModelFactory(
            content__0__char1__value="Char Block 1",
            content__1="simplestruct",
            content__2="simplestruct",
        ).content.raw_data
        cls.raw_data = raw_data

    def test_rename(self):
        """Rename `simplestruct.char1` blocks to `renamed1`

        Check whether all `simplestruct.char1` blocks have been renamed correctly.
        Check whether other children of `simplestruct` are intact.
        Check whether other toplevel blocks with name `char1` are intact.
        """

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

        self.assertIn("char2", altered_raw_data[1]["value"])
        self.assertIn("char2", altered_raw_data[2]["value"])

        self.assertEqual(altered_raw_data[0]["type"], "char1")
        self.assertEqual(altered_raw_data[1]["type"], "simplestruct")
        self.assertEqual(altered_raw_data[2]["type"], "simplestruct")

    def test_remove(self):
        """Remove `simplestruct.char1` blocks

        Check whether all `simplestruct.char1` blocks have been removed.
        Check whether other children of `simplestruct` are intact.
        Check whether other toplevel blocks with name `char1` are intact.
        """

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

        self.assertIn("char2", altered_raw_data[1]["value"])
        self.assertIn("char2", altered_raw_data[2]["value"])

        self.assertEqual(len(altered_raw_data), 3)


class FieldStreamChildBlock(TestCase):
    """Tests involving changes to direct children of a StreamBlock

    We use `simplestream` blocks as the StreamBlocks here.
    """

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
        """Rename `simplestream.char1` blocks to `renamed1`

        Check whether all `simplestream.char1` blocks have been renamed correctly.
        Check whether other children of `simplestream` are intact.
        Check whether other toplevel blocks with name `char1` are intact.
        """

        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "simplestream",
            RenameStreamChildrenOperation(old_name="char1", new_name="renamed1"),
            streamfield=models.SampleModel.content,
        )

        self.assertEqual(altered_raw_data[1]["value"][0]["type"], "renamed1")
        self.assertEqual(altered_raw_data[1]["value"][2]["type"], "renamed1")
        self.assertEqual(altered_raw_data[2]["value"][0]["type"], "renamed1")

        self.assertEqual(altered_raw_data[1]["value"][1]["type"], "char2")

        self.assertEqual(altered_raw_data[0]["type"], "char1")
        self.assertEqual(altered_raw_data[1]["type"], "simplestream")
        self.assertEqual(altered_raw_data[2]["type"], "simplestream")

    def test_remove(self):
        """Remove `simplestream.char1` blocks

        Check whether all `simplestream.char1` blocks have been removed.
        Check whether other children of `simplestream` are intact.
        Check whether other toplevel blocks with name `char1` are intact.
        """

        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "simplestream",
            RemoveStreamChildrenOperation(name="char1"),
            streamfield=models.SampleModel.content,
        )

        self.assertEqual(len(altered_raw_data[1]["value"]), 1)
        self.assertEqual(len(altered_raw_data[2]["value"]), 0)

        self.assertEqual(altered_raw_data[1]["value"][0]["type"], "char2")

        self.assertEqual(len(altered_raw_data), 3)
