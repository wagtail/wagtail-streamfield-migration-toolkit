from unittest import expectedFailure
from django.test import SimpleTestCase, TestCase

from wagtail_streamfield_migration_toolkit.utils import apply_changes_to_raw_data
from .. import factories


class RemoveUtilsTestCase(SimpleTestCase):
    pass


class RemoveRawDataIndividualTestCase(TestCase):
    """
    Tests with raw json data for different possible block structures involved in removing.
    Each test here only includes just an instance of the block which is being removed.
    """

    # TODO complete rest with wagtail-factories when available

    @expectedFailure
    def test_simple_remove(self):
        """Remove `char1`"""

        raw_data = factories.SampleModelFactory(
            content__0__char1__value="Char Block 1"
        ).content.raw_data
        altered_raw_data = apply_changes_to_raw_data(raw_data, "char1", "remove")

        self.assertEqual(len(altered_raw_data), 0)

    @expectedFailure
    def test_struct_nested_remove(self):
        """Remove `simplestruct.char1`"""

        raw_data = factories.SampleModelFactory(
            content__0__simplestruct__label="SimpleStruct 1"
        ).content.raw_data
        altered_raw_data = apply_changes_to_raw_data(
            raw_data, "simplestruct.char1", "remove"
        )

        self.assertEqual(len(altered_raw_data[0]["value"]), 1)
        self.assertNotIn("char1", altered_raw_data[0]["value"])

    @expectedFailure
    def test_stream_nested_remove(self):
        """Remove `simplestream.char1`"""

        # TODO use factories when available

        raw_data = [
            {
                "type": "simplestream",
                "value": [{"type": "char1", "value": "Char Block 1"}],
            }
        ]
        altered_raw_data = apply_changes_to_raw_data(
            raw_data, "simplestream.char1", "remove"
        )

        self.assertEqual(len(altered_raw_data[0]["value"]), 0)

    @expectedFailure
    def test_struct_stream_nested_remove(self):
        """Remove `nestedstruct.stream1.char1`"""

        # TODO use factories when available

        raw_data = [
            {
                "type": "nestedstruct",
                "value": {"stream1": [{"type": "char1", "value": "Char Block 1"}]},
            }
        ]
        altered_raw_data = apply_changes_to_raw_data(
            raw_data, "nestedstruct.stream1.char1", "remove"
        )

        nested_block = altered_raw_data[0]["value"]["stream1"]
        self.assertEqual(len(nested_block), 0)

    @expectedFailure
    def test_list_stream_nested_remove(self):
        """Remove `nestedlist_stream.char1`"""

        # TODO use factories when available

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
            raw_data, "nestedlist_stream.char1", "remove"
        )

        nested_block = altered_raw_data[0]["value"]
        self.assertEqual(len(nested_block[0]["value"]), 0)

    @expectedFailure
    def test_list_struct_nested_remove(self):
        "Remove `nestedlist_struct.char1`"

        raw_data = factories.SampleModelFactory(
            content__0__nestedlist_struct__0__label="NestedList Struct 1"
        ).content.raw_data
        altered_raw_data = apply_changes_to_raw_data(
            raw_data, "nestedlist_struct.char1", "remove"
        )

        nested_block = altered_raw_data[0]["value"][0]
        self.assertEqual(len(nested_block["value"]), 1)


class RemoveRawDataMultipleTestCase(TestCase):
    # TODO test multiple blocks at once
    # TODO test other blocks intact

    @expectedFailure
    def test_simple_remove(self):
        """Remove `char1`"""

        raw_data = factories.SampleModelFactory(
            content__0__char1__value="Char Block 1",
            content__1__char2__value="Char Block 2",
            content__2__char1__value="Char Block 1",
        ).content.raw_data
        
        altered_raw_data = apply_changes_to_raw_data(raw_data, "char1", "remove")

        self.assertEqual(len(altered_raw_data), 1)
        self.assertEqual(altered_raw_data[0]["type"], "char2")

    @expectedFailure
    def test_struct_nested_remove(self):
        """Remove `simplestruct.char1`"""

        raw_data = factories.SampleModelFactory(
            content__0__char1__value="Char Block 1",
            content__1__simplestruct__label="SimpleStruct 1",
            content__2__simplestruct__label="SimpleStruct 2",
        ).content.raw_data

        altered_raw_data = apply_changes_to_raw_data(
            raw_data, "simplestruct.char1", "remove"
        )

        self.assertEqual(len(altered_raw_data), 3)
        self.assertEqual(len(altered_raw_data[1]["value"]), 1)
        self.assertEqual(len(altered_raw_data[2]["value"]), 1)
        self.assertNotIn("char1", altered_raw_data[1]["value"])
        self.assertNotIn("char1", altered_raw_data[2]["value"])
        self.assertIn("char2", altered_raw_data[1]["value"])
        self.assertIn("char2", altered_raw_data[2]["value"])

    @expectedFailure
    def test_list_struct_nested_remove(self):
        "Remove `nestedlist_struct.char1`"

        raw_data = factories.SampleModelFactory(
            content__0__char1__value="Char Block 1",
            content__1__nestedlist_struct__0__label="NestedList Struct 1",
            content__1__nestedlist_struct__1__label="NestedList Struct 2",
            content__2__nestedlist_struct__0__label="NestedList Struct 3",
        ).content.raw_data

        altered_raw_data = apply_changes_to_raw_data(
            raw_data, "nestedlist_struct.char1", "remove"
        )

        self.assertEqual(len(altered_raw_data), 3)
        self.assertEqual(len(altered_raw_data[1]["value"]), 2)
        self.assertEqual(len(altered_raw_data[2]["value"]), 1)
        self.assertEqual(len(altered_raw_data[1]["value"][0]["value"]), 1)
        self.assertEqual(len(altered_raw_data[1]["value"][1]["value"]), 1)
        self.assertEqual(len(altered_raw_data[2]["value"][1]["value"]), 1)

        self.assertNotIn("char1", altered_raw_data[1]["value"][0]["value"])
        self.assertNotIn("char1", altered_raw_data[1]["value"][1]["value"])
        self.assertNotIn("char1", altered_raw_data[2]["value"][0]["value"])
        self.assertIn("char2", altered_raw_data[1]["value"][0]["value"])
        self.assertIn("char2", altered_raw_data[1]["value"][1]["value"])
        self.assertIn("char2", altered_raw_data[2]["value"][0]["value"])


class RemoveTestCase(TestCase):
    pass
