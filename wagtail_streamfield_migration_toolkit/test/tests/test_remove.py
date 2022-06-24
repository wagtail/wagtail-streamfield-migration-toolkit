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

        raw_data = [{"type": "char1", "value": "Simple Remove Value"}]
        altered_raw_data = apply_changes_to_raw_data(raw_data, "char1", "remove")

        self.assertEqual(len(altered_raw_data), 0)

    @expectedFailure
    def test_struct_remove(self):
        """Remove `struct1.struct1_char1`"""

        raw_data = [
            {
                "type": "struct1",
                "value": {
                    "struct1_char1": "Struct field remove",
                    "struct1_char2": "This shouldn't change",
                },
            }
        ]
        altered_raw_data = apply_changes_to_raw_data(
            raw_data, "struct1.struct1_char1", "remove"
        )

        self.assertNotIn("struct1_char1", altered_raw_data[0]["value"])

    @expectedFailure
    def test_simple_nested_remove(self):
        """Remove `stream1.stream1_char1`"""

        raw_data = [
            {
                "type": "stream1",
                "value": [
                    {"type": "stream1_char1", "value": "Nested Stream field remove"}
                ],
            }
        ]
        altered_raw_data = apply_changes_to_raw_data(
            raw_data, "stream1.stream1_char1", "remove"
        )

        self.assertEqual(len(altered_raw_data[0]["value"]), 0)

    # @expectedFailure
    # def test_struct_nested_remove(self):
    #     pass

    # @expectedFailure
    # def test_list_nested_remove(self):
    #     pass


class RemoveRawDataFullTestCase(TestCase):
    # TODO check wagtail_factories
    # TODO test multiple blocks at once
    # TODO test other blocks intact
    pass


class RemoveTestCase(TestCase):
    pass
