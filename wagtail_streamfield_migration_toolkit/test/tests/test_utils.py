from django.test import TestCase, SimpleTestCase

from wagtail_streamfield_migration_toolkit.utils import parse_block_path

class UtilsTestCase(SimpleTestCase):

    def test_parse_block_path(self):

        top_level_path = "char1"
        self.assertEqual(parse_block_path(top_level_path), ["char1"])

        nested_path = "struct1.struct1_char1"
        self.assertEqual(parse_block_path(nested_path), ["struct1", "struct1_char1"])
        