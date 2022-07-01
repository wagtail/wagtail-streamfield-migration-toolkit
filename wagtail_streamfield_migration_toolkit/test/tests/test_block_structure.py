from unittest import expectedFailure
from django.test import SimpleTestCase, TestCase

from .. import factories
from wagtail_streamfield_migration_toolkit.utils import apply_changes_to_raw_data


# TODO add asserts for ids


class TopLevelTest(TestCase):
    """Changes to `char1`"""

    @classmethod
    def setUpTestData(cls):
        raw_data = factories.SampleModelFactory(
            content__0__char1__value="Char Block 1",
            content__1__char2__value="Char Block 2",
            content__2__char1__value="Char Block 1",
        ).content.raw_data
        cls.raw_data = raw_data

    @expectedFailure
    def test_rename(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data, "char1", "rename", new_name="renamed1"
        )

        self.assertEqual(altered_raw_data[0]["type"], "renamed1")
        self.assertEqual(altered_raw_data[2]["type"], "renamed1")

        self.assertEqual(altered_raw_data[0]["value"], "Char Block 1")
        self.assertEqual(altered_raw_data[2]["value"], "Char Block 1")

    def test_rename_rest_intact(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data, "char1", "rename", new_name="renamed1"
        )

        self.assertEqual(altered_raw_data[1]["type"], "char2")

    @expectedFailure
    def test_remove(self):
        altered_raw_data = apply_changes_to_raw_data(self.raw_data, "char1", "remove")

        self.assertEqual(len(altered_raw_data), 1)
        self.assertEqual(altered_raw_data[0]["type"], "char2")

    def test_to_listblock(self):
        pass

    def test_to_streamblock(self):
        pass


class StructNestedTest(TestCase):
    """Changes to `simplestruct.char1`"""

    @classmethod
    def setUpTestData(cls):
        raw_data = factories.SampleModelFactory(
            content__0__char1__value="Char Block 1",
            content__1="simplestruct",
            content__2="simplestruct",
        ).content.raw_data
        cls.raw_data = raw_data

    @expectedFailure
    def test_rename(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data, "simplestruct.char1", "rename", new_name="renamed1"
        )

        self.assertNotIn("char1", altered_raw_data[1]["value"])
        self.assertNotIn("char1", altered_raw_data[2]["value"])
        self.assertIn("renamed1", altered_raw_data[1]["value"])
        self.assertIn("renamed1", altered_raw_data[2]["value"])

    def test_rename_rest_intact(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data, "simplestruct.char1", "rename", new_name="renamed1"
        )

        self.assertEqual(altered_raw_data[0]["type"], "char1")
        self.assertEqual(altered_raw_data[1]["type"], "simplestruct")
        self.assertEqual(altered_raw_data[2]["type"], "simplestruct")

        self.assertIn("char2", altered_raw_data[1]["value"])
        self.assertIn("char2", altered_raw_data[2]["value"])

    @expectedFailure
    def test_remove(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data, "simplestruct.char1", "remove"
        )

        self.assertEqual(len(altered_raw_data[1]["value"]), 1)
        self.assertEqual(len(altered_raw_data[2]["value"]), 1)
        self.assertNotIn("char1", altered_raw_data[1]["value"])
        self.assertNotIn("char1", altered_raw_data[2]["value"])

    def test_remove_rest_intact(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data, "simplestruct.char1", "remove"
        )

        self.assertEqual(len(altered_raw_data), 3)

        self.assertIn("char2", altered_raw_data[1]["value"])
        self.assertIn("char2", altered_raw_data[2]["value"])


class StreamNestedTest(TestCase):
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

    @expectedFailure
    def test_rename(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data, "simplestream.char1", "rename", "renamed1"
        )

        self.assertEqual(altered_raw_data[1]["value"][0]["type"], "renamed1")
        self.assertEqual(altered_raw_data[1]["value"][2]["type"], "renamed1")
        self.assertEqual(altered_raw_data[2]["value"][0]["type"], "renamed1")

    def test_rename_rest_intact(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data, "simplestream.char1", "rename", "renamed1"
        )

        self.assertEqual(altered_raw_data[0]["type"], "char1")
        self.assertEqual(altered_raw_data[1]["type"], "simplestream")
        self.assertEqual(altered_raw_data[2]["type"], "simplestream")

        self.assertEqual(altered_raw_data[1]["value"][1]["type"], "char2")

    @expectedFailure
    def test_remove(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data, "simplestream.char1", "remove"
        )

        self.assertEqual(len(altered_raw_data[1]["value"]), 1)
        self.assertEqual(len(altered_raw_data[2]["value"]), 0)

    @expectedFailure
    def test_remove_rest_intact(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data, "simplestream.char1", "remove"
        )

        self.assertEqual(len(altered_raw_data), 3)

        self.assertEqual(altered_raw_data[1]["value"][0]["type"], "char2")


class StructStreamNestedTest(TestCase):
    """Changes to `nestedstruct.simplestream.char1`"""

    @classmethod
    def setUpTestData(cls):
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

        cls.raw_data = raw_data

    @expectedFailure
    def test_rename(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data, "nestedstruct.stream1.char1", "rename", new_name="renamed1"
        )

        self.assertEqual(altered_raw_data[1]["value"]["stream1"][0]["type"], "renamed1")
        self.assertEqual(altered_raw_data[1]["value"]["stream1"][2]["type"], "renamed1")
        self.assertEqual(altered_raw_data[2]["value"]["stream1"][0]["type"], "renamed1")

    def test_rename_rest_intact(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data, "nestedstruct.stream1.char1", "rename", new_name="renamed1"
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

    @expectedFailure
    def test_remove(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data, "nestedstruct.stream1.char1", "remove"
        )

        self.assertEqual(len(altered_raw_data[1]["value"]["stream1"]), 1)
        self.assertEqual(len(altered_raw_data[2]["value"]["stream1"]), 0)

        self.assertNotEqual(altered_raw_data[1]["value"]["stream1"][0]["type"], "char1")

    @expectedFailure
    def test_remove_rest_intact(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data, "nestedstruct.stream1.char1", "remove"
        )

        self.assertEqual(len(altered_raw_data), 4)
        self.assertEqual(len(altered_raw_data[1]["value"]), 4)
        self.assertEqual(len(altered_raw_data[2]["value"]), 4)
        self.assertEqual(len(altered_raw_data[3]["value"]), 2)

        self.assertEqual("char2", altered_raw_data[1]["value"]["stream1"][0]["type"])


class StructStructNestedTest(TestCase):
    """Changes to `nestedstruct.simplestruct.char1`"""

    @classmethod
    def setUpTestData(cls):
        raw_data = factories.SampleModelFactory(
            content__0__char1__value="Char Block 1",
            content__1="nestedstruct",
            content__1__nestedstruct__list1__value="a",
            content__2="nestedstruct",
            content__2__nestedstruct__list1__value="a",
            content__3="simplestruct",
        ).content.raw_data
        cls.raw_data = raw_data

    @expectedFailure
    def test_rename(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data, "nestedstruct.struct1.char1", "rename", new_name="renamed1"
        )

        self.assertNotIn("char1", altered_raw_data[1]["value"]["struct1"]["value"])
        self.assertNotIn("char1", altered_raw_data[2]["value"]["struct1"]["value"])
        self.assertIn("renamed1", altered_raw_data[2]["value"]["struct1"]["value"])
        self.assertIn("renamed1", altered_raw_data[2]["value"]["struct1"]["value"])

    def test_rename_rest_intact(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data, "nestedstruct.struct1.char1", "rename", new_name="renamed1"
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

    @expectedFailure
    def test_remove(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data, "nestedstruct.struct1.char1", "remove"
        )

        self.assertEqual(len(altered_raw_data[1]["value"]["struct1"]), 1)
        self.assertEqual(len(altered_raw_data[2]["value"]["struct1"]), 1)

        self.assertNotIn("char1", altered_raw_data[1]["value"]["struct1"])
        self.assertNotIn("char1", altered_raw_data[2]["value"]["struct1"])

    def test_remove_rest_intact(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data, "nestedstruct.struct1.char1", "remove"
        )

        self.assertEqual(len(altered_raw_data), 4)
        self.assertEqual(len(altered_raw_data[1]["value"]), 4)
        self.assertEqual(len(altered_raw_data[2]["value"]), 4)
        self.assertEqual(len(altered_raw_data[3]["value"]), 2)

        self.assertIn("char2", altered_raw_data[1]["value"]["struct1"])
        self.assertIn("char2", altered_raw_data[2]["value"]["struct1"])


class StreamStreamNestedTest(TestCase):
    pass


class StreamStructNestedTest(TestCase):
    pass


class ListStreamNestedTest(TestCase):
    pass


class ListStructNestedTest(TestCase):
    """Changes to `nestedlist_struct.char1`"""

    @classmethod
    def setUpTestData(cls):
        raw_data = factories.SampleModelFactory(
            content__0__char1__value="Char Block 1",
            content__1__nestedlist_struct__0__label="Nested List Struct 1",
            content__1__nestedlist_struct__1__label="Nested List Struct 2",
            content__2__nestedlist_struct__0__label="Nested List Struct 3",
            content__3__simplestruct__label="Simple Struct 1",
        ).content.raw_data
        cls.raw_data = raw_data

    @expectedFailure
    def test_rename(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data, "nestedlist_struct.char1", "rename", "renamed1"
        )

        self.assertNotIn("char1", altered_raw_data[1]["value"][0]["value"])
        self.assertNotIn("char1", altered_raw_data[1]["value"][1]["value"])
        self.assertNotIn("char1", altered_raw_data[2]["value"][0]["value"])

        self.assertIn("renamed1", altered_raw_data[1]["value"][0]["value"])
        self.assertIn("renamed1", altered_raw_data[1]["value"][1]["value"])
        self.assertIn("renamed1", altered_raw_data[2]["value"][0]["value"])

    def test_rename_rest_intact(self):
        altered_raw_data = apply_changes_to_raw_data(
            self.raw_data, "nestedlist_struct.char1", "rename", "renamed1"
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
