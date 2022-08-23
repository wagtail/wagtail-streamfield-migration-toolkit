from django.test import TestCase
from wagtail.blocks import (
    CharBlock,
    IntegerBlock,
    # DateBlock,
    # StreamBlock,
    StructBlock,
    # ListBlock,
)

# from wagtail.snippets.blocks import SnippetChooserBlock

from wagtail_streamfield_migration_toolkit.autodetect.comparers import (
    StreamOrStructBlockDefComparer,
    # DefaultBlockDefComparer,
)


class NameBlockWithInitials(StructBlock):
    first_name = CharBlock()
    last_name = CharBlock()
    initials = CharBlock()


class NameBlockWithoutInitials(StructBlock):
    first_name = CharBlock()
    last_name = CharBlock()


class PersonalDetails(StructBlock):
    name = CharBlock()
    age = IntegerBlock()


class TestStructBlocks(TestCase):
    def test_similar(self):
        similar = StreamOrStructBlockDefComparer.compare(
            NameBlockWithInitials(), NameBlockWithoutInitials()
        )
        self.assertTrue(similar)

        similar = StreamOrStructBlockDefComparer.compare(
            NameBlockWithoutInitials(), NameBlockWithInitials()
        )
        self.assertTrue(similar)

    def test_dissimilar(self):
        similar = StreamOrStructBlockDefComparer.compare(
            NameBlockWithInitials(), PersonalDetails()
        )
        self.assertFalse(similar)

        similar = StreamOrStructBlockDefComparer.compare(
            PersonalDetails(), NameBlockWithInitials()
        )
        self.assertFalse(similar)
