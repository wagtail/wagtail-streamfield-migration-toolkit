from unittest import mock
from django.test import TestCase
from wagtail.blocks import CharBlock, StreamBlock, StructBlock

from wagtail_streamfield_migration_toolkit.autodetect.streamchangedetector import (
    StreamDefChangeDetector,
)
from wagtail_streamfield_migration_toolkit.operations import (
    RenameStreamChildrenOperation,
    RemoveStreamChildrenOperation,
    RemoveStructChildrenOperation,
    RenameStructChildrenOperation,
)
from ..models import BaseStreamBlock, SimpleStreamBlock, NestedStreamBlock


class SimpleStreamWithRemovedChild(StreamBlock):
    # removed char 1
    char2 = CharBlock()


class SimpleStreamWithRenamedChild(StreamBlock):
    renamed_char1 = CharBlock()
    char2 = CharBlock()


class SimpleStructWithRemovedChild(StructBlock):
    # removed char 1
    char2 = CharBlock()


class SimpleStructWithRenamedChild(StructBlock):
    renamed_char1 = CharBlock()
    char2 = CharBlock()


class NestedStreamWithRemovedStructChild(NestedStreamBlock):
    struct1 = SimpleStructWithRemovedChild()


class NestedStreamWithRenamedStructChild(NestedStreamBlock):
    struct1 = SimpleStructWithRenamedChild()


class StreamChangeDetectorTests(TestCase):
    def assertRemoveOperationEqual(self, operation1, operation2):
        self.assertEqual(
            operation1.__class__,
            operation2.__class__,
        )
        self.assertEqual(operation1.name, operation2.name)

    def assertRenameOperationEqual(self, operation1, operation2):
        self.assertEqual(
            operation1.__class__,
            operation2.__class__,
        )
        self.assertEqual(operation1.old_name, operation2.old_name)
        self.assertEqual(operation1.new_name, operation2.new_name)

    def test_same(self):
        """Test that comparing the same block definition produces no operations"""

        comparer = StreamDefChangeDetector(BaseStreamBlock(), BaseStreamBlock())
        comparer.create_data_migration_operations()

        self.assertEqual(len(comparer.merged_operations_and_block_paths), 0)

    @mock.patch(
        "wagtail_streamfield_migration_toolkit.autodetect.questioner.InteractiveDataMigrationQuestioner.ask_block_remove",
        return_value=True,
    )
    def test_stream_child_removed(self, mock_class):
        comparer = StreamDefChangeDetector(
            SimpleStreamBlock(), SimpleStreamWithRemovedChild()
        )
        comparer.create_data_migration_operations()

        expected_operations_and_block_paths = [
            (RemoveStreamChildrenOperation("char1"), "")
        ]

        self.assertEqual(
            len(expected_operations_and_block_paths),
            len(comparer.merged_operations_and_block_paths),
        )
        for (expected_operation, expected_block_path), (operation, block_path) in zip(
            expected_operations_and_block_paths,
            comparer.merged_operations_and_block_paths,
        ):
            self.assertEqual(expected_block_path, block_path)
            self.assertRemoveOperationEqual(expected_operation, operation)

    @mock.patch(
        "wagtail_streamfield_migration_toolkit.autodetect.questioner.InteractiveDataMigrationQuestioner.ask_block_rename",
        return_value=True,
    )
    def test_stream_child_renamed(self, mock_class):
        comparer = StreamDefChangeDetector(
            SimpleStreamBlock(), SimpleStreamWithRenamedChild()
        )
        comparer.create_data_migration_operations()

        expected_operations_and_block_paths = [
            (RenameStreamChildrenOperation("char1", "renamed_char1"), "")
        ]

        self.assertEqual(
            len(expected_operations_and_block_paths),
            len(comparer.merged_operations_and_block_paths),
        )
        for (expected_operation, expected_block_path), (operation, block_path) in zip(
            expected_operations_and_block_paths,
            comparer.merged_operations_and_block_paths,
        ):
            self.assertEqual(expected_block_path, block_path)
            self.assertRenameOperationEqual(expected_operation, operation)

    @mock.patch(
        "wagtail_streamfield_migration_toolkit.autodetect.questioner.InteractiveDataMigrationQuestioner.ask_block_remove",
        return_value=True,
    )
    def test_nested_struct_child_removed(self, mock_class):
        comparer = StreamDefChangeDetector(
            NestedStreamBlock(), NestedStreamWithRemovedStructChild()
        )
        comparer.create_data_migration_operations()

        expected_operations_and_block_paths = [
            (RemoveStructChildrenOperation("char1"), "struct1")
        ]

        self.assertEqual(
            len(expected_operations_and_block_paths),
            len(comparer.merged_operations_and_block_paths),
        )
        for (expected_operation, expected_block_path), (operation, block_path) in zip(
            expected_operations_and_block_paths,
            comparer.merged_operations_and_block_paths,
        ):
            self.assertEqual(expected_block_path, block_path)
            self.assertRemoveOperationEqual(expected_operation, operation)

    @mock.patch(
        "wagtail_streamfield_migration_toolkit.autodetect.questioner.InteractiveDataMigrationQuestioner.ask_block_rename",
        return_value=True,
    )
    def test_nested_struct_child_renamed(self, mock_class):
        comparer = StreamDefChangeDetector(
            NestedStreamBlock(), NestedStreamWithRenamedStructChild()
        )
        comparer.create_data_migration_operations()

        expected_operations_and_block_paths = [
            (RenameStructChildrenOperation("char1", "renamed_char1"), "struct1")
        ]

        self.assertEqual(
            len(expected_operations_and_block_paths),
            len(comparer.merged_operations_and_block_paths),
        )
        for (expected_operation, expected_block_path), (operation, block_path) in zip(
            expected_operations_and_block_paths,
            comparer.merged_operations_and_block_paths,
        ):
            self.assertEqual(expected_block_path, block_path)
            self.assertRenameOperationEqual(expected_operation, operation)
