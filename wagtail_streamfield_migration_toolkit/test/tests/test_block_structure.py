from unittest import expectedFailure
from django.test import SimpleTestCase, TestCase

from .. import factories, models
from wagtail_streamfield_migration_toolkit.utils import apply_changes_to_raw_data
from wagtail_streamfield_migration_toolkit.operations import (
    RenameStreamChildrenOperation,
    RenameStructChildrenOperation,
    RemoveStreamChildrenOperation,
    RemoveStructChildrenOperation,
    StreamChildrenToListBlockOperation,
    StreamChildrenToStreamBlockOperation,
)


# TODO add asserts for ids


class FieldChildBlockTest(TestCase):
    """Changes to `char1`"""

    def setUp(self):
        raw_data = factories.SampleModelFactory(
            content__0__char1__value="Char Block 1",
            content__1__char2__value="Char Block 2",
            content__2__char1__value="Char Block 1",
        ).content.raw_data
        self.raw_data = raw_data

    def test_rename(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            None,
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
            None,
            RenameStreamChildrenOperation(old_name="char1", new_name="renamed1"),
            streamfield=models.SampleModel.content,
        )

        self.assertEqual(altered_raw_data[1]["type"], "char2")

    def test_remove(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            None,
            RemoveStreamChildrenOperation(name="char1"),
            streamfield=models.SampleModel.content,
        )

        self.assertEqual(len(altered_raw_data), 1)
        self.assertEqual(altered_raw_data[0]["type"], "char2")

    def test_to_listblock(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "char1",
            StreamChildrenToListBlockOperation(list_block_name="list1"),
            streamfield=models.SampleModel.content,
        )

        self.assertEqual(len(altered_raw_data), 2)
        self.assertEqual(altered_raw_data[0]["type"], "char2")
        self.assertEqual(altered_raw_data[1]["type"], "list1")
        self.assertEqual(len(altered_raw_data[1]["value"]), 2)
        self.assertEqual(altered_raw_data[1]["value"][0]["type"], "item")
        self.assertEqual(altered_raw_data[1]["value"][0]["value"], "Char Block 1")

    def test_combine_to_streamblock(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "char1",
            StreamChildrenToStreamBlockOperation(
                stream_block_name="stream1"
            ),
            streamfield=models.SampleModel.content,
        )

        self.assertEqual(len(altered_raw_data), 2)
        self.assertEqual(altered_raw_data[0]["type"], "char2")
        self.assertEqual(altered_raw_data[1]["type"], "stream1")
        self.assertEqual(len(altered_raw_data[1]["value"]), 2)
        self.assertEqual(altered_raw_data[0]["value"][0]["type"], "char1")
        self.assertEqual(altered_raw_data[0]["value"][1]["type"], "char1")

    def test_combine_to_streamblock_multiple(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "*",
            StreamChildrenToStreamBlockOperation(
                stream_block_name="stream1", block_names=["char1", "char2"]
            ),
            streamfield=models.SampleModel.content,
        )

        self.assertEqual(len(altered_raw_data), 1)
        self.assertEqual(altered_raw_data[0]["type"], "stream1")
        self.assertEqual(len(altered_raw_data[0]["value"]), 3)
        self.assertEqual(altered_raw_data[0]["value"][0]["type"], "char1")
        self.assertEqual(altered_raw_data[0]["value"][1]["type"], "char2")
        self.assertEqual(altered_raw_data[0]["value"][2]["type"], "char1")


class FieldStructChildBlockTest(TestCase):
    """Changes to `simplestruct.char1`"""

    def setUp(self):
        raw_data = factories.SampleModelFactory(
            content__0__char1__value="Char Block 1",
            content__1="simplestruct",
            content__2="simplestruct",
        ).content.raw_data
        self.raw_data = raw_data

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

    def setUp(self):
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
        self.raw_data = raw_data

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


class FieldStructStreamChildBlockTest(TestCase):
    """Changes to `nestedstruct.simplestream.char1`"""

    def setUp(self):
        raw_data = factories.SampleModelFactory(
            content__0__char1__value="Char Block 1",
            content__1="nestedstruct",
            content__1__nestedstruct__list1__value="a",
            content__2="nestedstruct",
            content__2__nestedstruct__list1__value="a",
        ).content.raw_data

        # TODO until support is available from wagtail-factories, manually add the rest.
        raw_data[1]["value"]["stream1"] = [
            {"type": "char1", "value": "Char Block 1"},
            {"type": "char2", "value": "Char Block 2"},
            {"type": "char1", "value": "Char Block 1"},
        ]
        raw_data[2]["value"]["stream1"] = [
            {"type": "char1", "value": "Char Block 1"},
        ]
        raw_data.append(
            {
                "type": "simplestream",
                "value": [
                    {"type": "char1", "value": "Char Block 1"},
                    {"type": "char2", "value": "Char Block 2"},
                ],
            }
        )

        self.raw_data = raw_data

    def test_rename(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "nestedstruct.stream1",
            RenameStreamChildrenOperation(old_name="char1", new_name="renamed1"),
            streamfield=models.SampleModel.content,
        )

        self.assertEqual(altered_raw_data[1]["value"]["stream1"][0]["type"], "renamed1")
        self.assertEqual(altered_raw_data[1]["value"]["stream1"][2]["type"], "renamed1")
        self.assertEqual(altered_raw_data[2]["value"]["stream1"][0]["type"], "renamed1")

    def test_rename_rest_intact(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "nestedstruct.stream1",
            RenameStreamChildrenOperation(old_name="char1", new_name="renamed1"),
            streamfield=models.SampleModel.content,
        )

        self.assertEqual(altered_raw_data[0]["type"], "char1")
        self.assertEqual(altered_raw_data[1]["type"], "nestedstruct")
        self.assertEqual(altered_raw_data[2]["type"], "nestedstruct")
        self.assertEqual(altered_raw_data[3]["type"], "simplestream")

        self.assertIn("char1", altered_raw_data[1]["value"])
        self.assertIn("stream1", altered_raw_data[1]["value"])
        self.assertIn("struct1", altered_raw_data[1]["value"])
        self.assertIn("list1", altered_raw_data[1]["value"])

        self.assertEqual(altered_raw_data[3]["value"][0]["type"], "char1")
        self.assertEqual(altered_raw_data[3]["value"][1]["type"], "char2")

        self.assertEqual(altered_raw_data[1]["value"]["stream1"][1]["type"], "char2")

    def test_remove(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "nestedstruct.stream1",
            RemoveStreamChildrenOperation(name="char1"),
            streamfield=models.SampleModel.content,
        )

        self.assertEqual(len(altered_raw_data[1]["value"]["stream1"]), 1)
        self.assertEqual(len(altered_raw_data[2]["value"]["stream1"]), 0)

        self.assertNotEqual(altered_raw_data[1]["value"]["stream1"][0]["type"], "char1")

    def test_remove_rest_intact(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "nestedstruct.stream1",
            RemoveStreamChildrenOperation(name="char1"),
            streamfield=models.SampleModel.content,
        )

        self.assertEqual(len(altered_raw_data), 4)
        self.assertEqual(len(altered_raw_data[1]["value"]), 4)
        self.assertEqual(len(altered_raw_data[2]["value"]), 4)
        self.assertEqual(len(altered_raw_data[3]["value"]), 2)

        self.assertEqual("char2", altered_raw_data[1]["value"]["stream1"][0]["type"])


class FieldStructStructChildBlockTest(TestCase):
    """Changes to `nestedstruct.simplestruct.char1`"""

    def setUp(self):
        raw_data = factories.SampleModelFactory(
            content__0__char1__value="Char Block 1",
            content__1="nestedstruct",
            content__1__nestedstruct__list1__value="a",
            content__2="nestedstruct",
            content__2__nestedstruct__list1__value="a",
            content__3="simplestruct",
        ).content.raw_data
        self.raw_data = raw_data

    def test_rename(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "nestedstruct.struct1",
            RenameStructChildrenOperation(old_name="char1", new_name="renamed1"),
            streamfield=models.SampleModel.content,
        )

        self.assertNotIn("char1", altered_raw_data[1]["value"]["struct1"])
        self.assertNotIn("char1", altered_raw_data[2]["value"]["struct1"])
        self.assertIn("renamed1", altered_raw_data[2]["value"]["struct1"])
        self.assertIn("renamed1", altered_raw_data[2]["value"]["struct1"])

    def test_rename_rest_intact(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "nestedstruct.struct1",
            RenameStructChildrenOperation(old_name="char1", new_name="renamed1"),
            streamfield=models.SampleModel.content,
        )

        self.assertEqual(len(altered_raw_data), 4)

        self.assertEqual(altered_raw_data[0]["type"], "char1")
        self.assertEqual(altered_raw_data[1]["type"], "nestedstruct")
        self.assertEqual(altered_raw_data[2]["type"], "nestedstruct")
        self.assertEqual(altered_raw_data[3]["type"], "simplestruct")

        self.assertIn("char1", altered_raw_data[1]["value"])
        self.assertIn("stream1", altered_raw_data[1]["value"])
        self.assertIn("struct1", altered_raw_data[1]["value"])
        self.assertIn("list1", altered_raw_data[1]["value"])

        self.assertIn("char1", altered_raw_data[3]["value"])
        self.assertIn("char2", altered_raw_data[3]["value"])

        self.assertIn("char2", altered_raw_data[1]["value"]["struct1"])
        self.assertIn("char2", altered_raw_data[2]["value"]["struct1"])

    def test_remove(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "nestedstruct.struct1",
            RemoveStructChildrenOperation(name="char1"),
            streamfield=models.SampleModel.content,
        )

        self.assertEqual(len(altered_raw_data[1]["value"]["struct1"]), 1)
        self.assertEqual(len(altered_raw_data[2]["value"]["struct1"]), 1)

        self.assertNotIn("char1", altered_raw_data[1]["value"]["struct1"])
        self.assertNotIn("char1", altered_raw_data[2]["value"]["struct1"])

    def test_remove_rest_intact(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "nestedstruct.struct1",
            RemoveStructChildrenOperation(name="char1"),
            streamfield=models.SampleModel.content,
        )

        self.assertEqual(len(altered_raw_data), 4)
        self.assertEqual(len(altered_raw_data[1]["value"]), 4)
        self.assertEqual(len(altered_raw_data[2]["value"]), 4)
        self.assertEqual(len(altered_raw_data[3]["value"]), 2)

        self.assertIn("char2", altered_raw_data[1]["value"]["struct1"])
        self.assertIn("char2", altered_raw_data[2]["value"]["struct1"])


class FieldStreamStreamChildBlockTest(TestCase):
    """Changes to `nestedstream.stream1.char1`"""

    def setUp(self):
        raw_data = [
            {"type": "char1", "value": "Char Block 1"},
            {
                "type": "nestedstream",
                "value": [
                    {"type": "char1", "value": "Char Block 1"},
                    {
                        "type": "stream1",
                        "value": [
                            {"type": "char1", "value": "Char Block 1"},
                            {"type": "char2", "value": "Char Block 2"},
                            {"type": "char1", "value": "Char Block 1"},
                        ],
                    },
                    {
                        "type": "stream1",
                        "value": [
                            {"type": "char1", "value": "Char Block 1"},
                        ],
                    },
                ],
            },
            {
                "type": "nestedstream",
                "value": [
                    {
                        "type": "stream1",
                        "value": [
                            {"type": "char1", "value": "Char Block 1"},
                        ],
                    }
                ],
            },
            {
                "type": "simplestream",
                "value": [
                    {"type": "char1", "value": "Char Block 1"},
                ],
            },
        ]
        self.raw_data = raw_data

    def test_rename(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "nestedstream.stream1",
            RenameStreamChildrenOperation(old_name="char1", new_name="renamed1"),
            models.SampleModel.content,
        )

        self.assertEqual(
            altered_raw_data[1]["value"][1]["value"][0]["type"], "renamed1"
        )
        self.assertEqual(
            altered_raw_data[1]["value"][1]["value"][2]["type"], "renamed1"
        )
        self.assertEqual(
            altered_raw_data[1]["value"][2]["value"][0]["type"], "renamed1"
        )
        self.assertEqual(
            altered_raw_data[2]["value"][0]["value"][0]["type"], "renamed1"
        )

    def test_rename_rest_intact(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "nestedstream.stream1",
            RenameStreamChildrenOperation(old_name="char1", new_name="renamed1"),
            models.SampleModel.content,
        )

        self.assertEqual(altered_raw_data[0]["type"], "char1")
        self.assertEqual(altered_raw_data[1]["type"], "nestedstream")
        self.assertEqual(altered_raw_data[2]["type"], "nestedstream")
        self.assertEqual(altered_raw_data[3]["type"], "simplestream")

        self.assertEqual(altered_raw_data[1]["value"][0]["type"], "char1")
        self.assertEqual(altered_raw_data[1]["value"][1]["type"], "stream1")
        self.assertEqual(altered_raw_data[1]["value"][2]["type"], "stream1")
        self.assertEqual(altered_raw_data[2]["value"][0]["type"], "stream1")
        self.assertEqual(altered_raw_data[3]["value"][0]["type"], "char1")

        self.assertEqual(altered_raw_data[1]["value"][1]["value"][1]["type"], "char2")

    def test_remove(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "nestedstream.stream1",
            RemoveStreamChildrenOperation(name="char1"),
            models.SampleModel.content,
        )

        self.assertEqual(len(altered_raw_data[1]["value"][1]["value"]), 1)
        self.assertEqual(len(altered_raw_data[1]["value"][2]["value"]), 0)
        self.assertEqual(len(altered_raw_data[2]["value"][0]["value"]), 0)

    def test_remove_rest_intact(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "nestedstream.stream1",
            RemoveStreamChildrenOperation(name="char1"),
            models.SampleModel.content,
        )

        self.assertEqual(len(altered_raw_data), 4)
        self.assertEqual(len(altered_raw_data[1]["value"]), 3)
        self.assertEqual(len(altered_raw_data[2]["value"]), 1)
        self.assertEqual(len(altered_raw_data[3]["value"]), 1)

        self.assertEqual(altered_raw_data[1]["value"][1]["value"][0]["type"], "char2")


class FieldStreamStructChildBlockTest(TestCase):
    "Changes to `nestedstream.simplestruct.char1`"

    def setUp(self):
        # TODO rewrite with wagtail_factories when available
        raw_data = [
            {"type": "char1", "value": "Char Block 1"},
            {
                "type": "nestedstream",
                "value": [
                    {"type": "char1", "value": "Char Block 1"},
                    {
                        "type": "struct1",
                        "value": {"char1": "Char Block 1", "char2": "Char Block 2"},
                    },
                    {
                        "type": "struct1",
                        "value": {"char1": "Char Block 1", "char2": "Char Block 2"},
                    },
                ],
            },
            {
                "type": "nestedstream",
                "value": [
                    {
                        "type": "struct1",
                        "value": {"char1": "Char Block 1", "char2": "Char Block 2"},
                    }
                ],
            },
            {
                "type": "simplestream",
                "value": [
                    {"type": "char1", "value": "Char Block 1"},
                ],
            },
        ]
        self.raw_data = raw_data

    def test_rename(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "nestedstream.struct1",
            RenameStructChildrenOperation(old_name="char1", new_name="renamed1"),
            models.SampleModel.content,
        )

        self.assertNotIn("char1", altered_raw_data[1]["value"][1]["value"])
        self.assertNotIn("char1", altered_raw_data[1]["value"][2]["value"])
        self.assertNotIn("char1", altered_raw_data[2]["value"][0]["value"])
        self.assertIn("renamed1", altered_raw_data[1]["value"][1]["value"])
        self.assertIn("renamed1", altered_raw_data[1]["value"][2]["value"])
        self.assertIn("renamed1", altered_raw_data[2]["value"][0]["value"])

    def test_rename_rest_intact(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "nestedstream.struct1",
            RenameStructChildrenOperation(old_name="char1", new_name="renamed1"),
            models.SampleModel.content,
        )

        self.assertEqual(altered_raw_data[0]["type"], "char1")
        self.assertEqual(altered_raw_data[1]["type"], "nestedstream")
        self.assertEqual(altered_raw_data[2]["type"], "nestedstream")
        self.assertEqual(altered_raw_data[3]["type"], "simplestream")

        self.assertEqual(altered_raw_data[1]["value"][0]["type"], "char1")
        self.assertEqual(altered_raw_data[3]["value"][0]["type"], "char1")

        self.assertIn("char2", altered_raw_data[1]["value"][1]["value"])
        self.assertIn("char2", altered_raw_data[1]["value"][2]["value"])
        self.assertIn("char2", altered_raw_data[2]["value"][0]["value"])

    def test_remove(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "nestedstream.struct1",
            RemoveStructChildrenOperation(name="char1"),
            models.SampleModel.content,
        )

        self.assertEqual(len(altered_raw_data[1]["value"][1]["value"]), 1)
        self.assertEqual(len(altered_raw_data[1]["value"][2]["value"]), 1)
        self.assertEqual(len(altered_raw_data[2]["value"][0]["value"]), 1)
        self.assertNotIn("char1", altered_raw_data[1]["value"][1]["value"])
        self.assertNotIn("char1", altered_raw_data[1]["value"][2]["value"])
        self.assertNotIn("char1", altered_raw_data[2]["value"][0]["value"])

    def test_remove_rest_intact(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "nestedstream.struct1",
            RemoveStructChildrenOperation(name="char1"),
            models.SampleModel.content,
        )

        self.assertEqual(len(altered_raw_data), 4)
        self.assertEqual(len(altered_raw_data[1]["value"]), 3)
        self.assertEqual(len(altered_raw_data[2]["value"]), 1)
        self.assertEqual(len(altered_raw_data[3]["value"]), 1)

        self.assertEqual(len(altered_raw_data[1]["value"][1]["value"]), 1)
        self.assertEqual(len(altered_raw_data[1]["value"][2]["value"]), 1)
        self.assertEqual(len(altered_raw_data[2]["value"][0]["value"]), 1)

        self.assertIn("char2", altered_raw_data[1]["value"][1]["value"])
        self.assertIn("char2", altered_raw_data[1]["value"][2]["value"])
        self.assertIn("char2", altered_raw_data[2]["value"][0]["value"])


class FieldListStreamChildBlockTest(TestCase):
    "Changes to `nestedlist_stream.item.char1`"

    def setUp(self):
        # TODO rewrite with wagtail_factories when available
        raw_data = [
            {"type": "char1", "value": "Char Block 1"},
            {
                "type": "nestedlist_stream",
                "value": [
                    {
                        "type": "item",
                        "value": [
                            {"type": "char1", "value": "Char Block 1"},
                            {"type": "char2", "value": "Char Block 2"},
                            {"type": "char1", "value": "Char Block 1"},
                        ],
                    },
                    {
                        "type": "item",
                        "value": [{"type": "char1", "value": "Char Block 1"}],
                    },
                ],
            },
            {
                "type": "nestedlist_stream",
                "value": [
                    {
                        "type": "item",
                        "value": [{"type": "char1", "value": "Char Block 1"}],
                    }
                ],
            },
            {
                "type": "simplestream",
                "value": [
                    {"type": "char1", "value": "Char Block 1"},
                    {"type": "char2", "value": "Char Block 2"},
                ],
            },
        ]
        self.raw_data = raw_data

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

    def test_rename_rest_intact(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "nestedlist_stream.item",
            RenameStreamChildrenOperation(old_name="char1", new_name="renamed1"),
            streamfield=models.SampleModel.content,
        )

        self.assertEqual(altered_raw_data[0]["type"], "char1")
        self.assertEqual(altered_raw_data[1]["type"], "nestedlist_stream")
        self.assertEqual(altered_raw_data[2]["type"], "nestedlist_stream")
        self.assertEqual(altered_raw_data[3]["type"], "simplestream")

        self.assertEqual(altered_raw_data[1]["value"][0]["value"][1]["type"], "char2")
        self.assertEqual(altered_raw_data[3]["value"][0]["type"], "char1")
        self.assertEqual(altered_raw_data[3]["value"][1]["type"], "char2")

    def test_remove(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "nestedlist_stream.item",
            RemoveStreamChildrenOperation(name="char1"),
            streamfield=models.SampleModel.content,
        )

        self.assertEqual(len(altered_raw_data[1]["value"][0]["value"]), 1)
        self.assertEqual(len(altered_raw_data[1]["value"][1]["value"]), 0)
        self.assertEqual(len(altered_raw_data[2]["value"][0]["value"]), 0)

    def test_remove_rest_intact(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "nestedlist_stream.item",
            RemoveStreamChildrenOperation(name="char1"),
            streamfield=models.SampleModel.content,
        )

        self.assertEqual(len(altered_raw_data), 4)
        self.assertEqual(len(altered_raw_data[1]["value"]), 2)
        self.assertEqual(len(altered_raw_data[2]["value"]), 1)
        self.assertEqual(len(altered_raw_data[3]["value"]), 2)

        self.assertEqual(altered_raw_data[1]["value"][0]["value"][0]["type"], "char2")


class FieldListStructChildBlockTest(TestCase):
    """Changes to `nestedlist_struct.item.char1`"""

    def setUp(self):
        raw_data = factories.SampleModelFactory(
            content__0__char1__value="Char Block 1",
            content__1__nestedlist_struct__0__label="Nested List Struct 1",
            content__1__nestedlist_struct__1__label="Nested List Struct 2",
            content__2__nestedlist_struct__0__label="Nested List Struct 3",
            content__3__simplestruct__label="Simple Struct 1",
        ).content.raw_data
        self.raw_data = raw_data

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

    def test_rename_rest_intact(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data,
            "nestedlist_struct.item",
            RenameStructChildrenOperation(old_name="char1", new_name="renamed1"),
            streamfield=models.SampleModel.content,
        )

        self.assertEqual(altered_raw_data[0]["type"], "char1")
        self.assertEqual(altered_raw_data[1]["type"], "nestedlist_struct")
        self.assertEqual(altered_raw_data[2]["type"], "nestedlist_struct")
        self.assertEqual(altered_raw_data[3]["type"], "simplestruct")

        self.assertIn("char1", altered_raw_data[3]["value"])
        self.assertIn("char2", altered_raw_data[3]["value"])

        self.assertIn("char2", altered_raw_data[1]["value"][0]["value"])
        self.assertIn("char2", altered_raw_data[1]["value"][1]["value"])
        self.assertIn("char2", altered_raw_data[2]["value"][0]["value"])
