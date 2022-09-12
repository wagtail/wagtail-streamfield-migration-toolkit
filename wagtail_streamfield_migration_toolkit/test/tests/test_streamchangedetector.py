from unittest import mock
from django.test import TestCase
from wagtail.blocks import CharBlock, StreamBlock

from wagtail_streamfield_migration_toolkit.autodetect.streamchangedetector import (
    StreamDefChangeDetector,
)
from wagtail_streamfield_migration_toolkit.operations import (
    RenameStreamChildrenOperation,
    RemoveStreamChildrenOperation,
)
from ..models import (
    BaseStreamBlock,
    SimpleStreamBlock,
)


class SimpleStreamWithRemovedChild(StreamBlock):
    # removed char 1
    char2 = CharBlock()


class SimpleStreamWithRenamedChild(StreamBlock):
    renamed_char1 = CharBlock()
    char2 = CharBlock()


class StreamChangeDetectorTests(TestCase):
    def assertRemoveOperationEqual(
        self, operation_and_block_path1, operation_and_block_path2
    ):
        self.assertEqual(operation_and_block_path1[1], operation_and_block_path2[1])
        self.assertEqual(
            operation_and_block_path1[0].__class__,
            operation_and_block_path2[0].__class__,
        )
        self.assertEqual(
            operation_and_block_path1[0].name, operation_and_block_path2[0].name
        )

    def assertRenameOperationEqual(
        self, operation_and_block_path1, operation_and_block_path2
    ):
        self.assertEqual(operation_and_block_path1[1], operation_and_block_path2[1])
        self.assertEqual(
            operation_and_block_path1[0].__class__,
            operation_and_block_path2[0].__class__,
        )
        self.assertEqual(
            operation_and_block_path1[0].old_name, operation_and_block_path2[0].old_name
        )
        self.assertEqual(
            operation_and_block_path1[0].new_name, operation_and_block_path2[0].new_name
        )

    def test_same(self):
        """Test the same block definition"""

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
        for expected_value, value in zip(
            expected_operations_and_block_paths,
            comparer.merged_operations_and_block_paths,
        ):
            self.assertRemoveOperationEqual(expected_value, value)

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
        for expected_value, value in zip(
            expected_operations_and_block_paths,
            comparer.merged_operations_and_block_paths,
        ):
            self.assertRenameOperationEqual(expected_value, value)
