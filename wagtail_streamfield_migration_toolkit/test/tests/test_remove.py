from unittest import expectedFailure
from django.test import SimpleTestCase, TestCase

from wagtail_streamfield_migration_toolkit.utils import apply_changes_to_raw_data


class RemoveUtilsTestCase(SimpleTestCase):
    pass


class RemoveRawDataIndividualTestCase(SimpleTestCase):
    """
    Tests with raw json data for different possible block structures involved in renaming.
    Each test here only includes just the
    """

    @expectedFailure
    def test_simple_remove(self):
        """Remove `char1`"""

        raw_data = [{"type": "char1", "value": "Char Block 1"}]
        altered_raw_data = apply_changes_to_raw_data(raw_data, "char1", "remove")

        self.assertEqual(len(altered_raw_data), 0)

    @expectedFailure
    def test_struct_nested_remove(self):
        """Remove `simplestruct.char1`"""

        raw_data = [
            {
                "type": "simplestruct",
                "value": {
                    "char1": "Char Block 1",
                    "char2": "Char Block 2",
                },
            }
        ]
        altered_raw_data = apply_changes_to_raw_data(
            raw_data, "simplestruct.char1", "remove"
        )

        self.assertNotIn("char1", altered_raw_data[0]["value"])

    @expectedFailure
    def test_stream_nested_remove(self):
        """Remove `simplestream.char1`"""

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

        raw_data = [
            {
                "type": "nestedstruct",
                "value": {"stream1": [{"type": "char1", "value": "Char Block 1"}]},
            }
        ]
        altered_raw_data = apply_changes_to_raw_data(
            raw_data, "nestedstruct.stream1.char1", "remove"
        )

        nested_block = altered_raw_data[0]["value"]
        self.assertEqual(len(nested_block["stream1"]), 0)

    @expectedFailure
    def test_list_stream_nested_remove(self):
        """Remove `nestedlist.char1`"""

        raw_data = [
            {
                "type": "nestedlist",
                "value": [
                    {
                        "type": "item",
                        "value": [{"type": "char1", "value": "Char Block 1"}],
                    }
                ],
            }
        ]
        altered_raw_data = apply_changes_to_raw_data(
            raw_data, "nestedlist.char1", "remove"
        )

        nested_block = altered_raw_data[0]["value"]
        self.assertEqual(len(nested_block[0]["value"]), 0)


class RemoveRawDataFullTestCase(TestCase):
    # TODO check wagtail_factories
    # TODO test multiple blocks at once
    # TODO test other blocks intact
    pass


class RemoveTestCase(TestCase):
    pass
