from django.test import TestCase, SimpleTestCase

# from wagtail_streamfield_migration_toolkit.utils import get_altered_raw_data
from ..models import SampleModel


class RemoveRawDataTestCase(TestCase):
    """
    Tests without saving or loading from the database.
    This is to test just the changes to the raw json data, without considering the schema changes,
    or anything post save.
    """

    def test_simple_remove(self):
        """Remove `char1`"""

        raw_data = [{"type": "char1", "value": "Simple Remove Value"}]
        # TODO figure out how utils will be implemented
        altered_raw_data = raw_data

        self.assertEqual(len(altered_raw_data), 0)

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
        # TODO
        altered_raw_data = raw_data

        self.assertNotIn("struct1_char1", altered_raw_data[0]["value"])

    def test_nested_remove(self):
        """Remove `stream1.stream1_char1` """
        
        raw_data = [{
            "type": "stream1",
            "value": [
                {"type": "stream1_char1", "value": "Nested Stream field remove"}
            ]
        }]
        # TODO
        altered_raw_data = raw_data
        
        self.assertEqual(len(altered_raw_data[0]["value"]), 0)

    @staticmethod
    def create_sample_model():
        # TODO change
        sample_model = SampleModel(
            content=[
                {
                    "type": "char1",
                    "value": "Simple Remove Value",
                },
                {
                    "type": "char2",
                    "value": "This shouldn't change",
                },
                {
                    "type": "struct1",
                    "value": {
                        "struct1_char1": "Struct field remove",
                        "struct1_char2": "This shouldn't change",
                    },
                },
                {
                    "type": "stream1",
                    "value": [
                        {
                            "type": "stream1_char1",
                            "value": "Nested Stream field remove",
                        },
                        {"type": "stream1_char2", "value": "This shouldn't change"},
                    ],
                },
            ]
        )
        return sample_model
