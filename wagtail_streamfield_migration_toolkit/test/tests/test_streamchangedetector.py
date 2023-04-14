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
from wagtail_streamfield_migration_toolkit.autodetect.questioner import (
    InteractiveDataMigrationQuestioner,
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


def mock_questioner(ret_value, questioner_method):
    def decorator(func):
        func_path = "wagtail_streamfield_migration_toolkit.autodetect.questioner.InteractiveDataMigrationQuestioner.{}".format(
            questioner_method
        )
        with mock.patch(
            func_path,
            return_value=ret_value,
        ) as _mock:
            return _mock

    return decorator


class StreamChangeDetectorTests(TestCase):
    def assertOperationEqual(self, operation1, operation2):
        self.assertEqual(
            operation1.__class__,
            operation2.__class__,
        )
        self.assertEqual(operation1.__dict__, operation2.__dict__)

    def assertOperationsAndPathsEqual(
        self, operations_and_paths, expected_operations_and_paths
    ):
        counter = 0
        with self.subTest(counter=counter):
            self.assertEqual(
                len(expected_operations_and_paths),
                len(operations_and_paths),
            )
            counter += 1

        for (expected_operation, expected_block_path), (operation, block_path) in zip(
            expected_operations_and_paths,
            operations_and_paths,
        ):
            with self.subTest(counter=counter):
                counter += 1
                self.assertEqual(expected_block_path, block_path)
                self.assertOperationEqual(expected_operation, operation)

    def test_same(self):
        """Test that comparing the same block definition produces no operations"""

        comparer = StreamDefChangeDetector(
            BaseStreamBlock(),
            BaseStreamBlock(),
            InteractiveDataMigrationQuestioner(),
        )
        comparer.create_data_migration_operations()

        self.assertEqual(len(comparer.merged_operations_and_block_paths), 0)

    @mock_questioner(ret_value=True, questioner_method="ask_if_block_removed")
    def test_stream_child_removed(self, mock_remove_block_questioner):
        comparer = StreamDefChangeDetector(
            SimpleStreamBlock(),
            SimpleStreamWithRemovedChild(),
            InteractiveDataMigrationQuestioner(),
        )
        comparer.create_data_migration_operations()

        expected_operations_and_block_paths = [
            (RemoveStreamChildrenOperation("char1"), "")
        ]

        self.assertOperationsAndPathsEqual(
            comparer.merged_operations_and_block_paths,
            expected_operations_and_block_paths,
        )

    @mock_questioner(ret_value=True, questioner_method="ask_if_block_renamed")
    def test_stream_child_renamed(self, mock_rename_block_questioner):
        comparer = StreamDefChangeDetector(
            SimpleStreamBlock(),
            SimpleStreamWithRenamedChild(),
            InteractiveDataMigrationQuestioner(),
        )
        comparer.create_data_migration_operations()

        expected_operations_and_block_paths = [
            (RenameStreamChildrenOperation("char1", "renamed_char1"), "")
        ]

        self.assertOperationsAndPathsEqual(
            comparer.merged_operations_and_block_paths,
            expected_operations_and_block_paths,
        )

    @mock_questioner(ret_value=True, questioner_method="ask_if_block_same")
    @mock_questioner(ret_value=True, questioner_method="ask_if_block_renamed")
    def test_nested_struct_child_removed(
        self, mock_same_block_questioner, mock_rename_block_questioner
    ):
        comparer = StreamDefChangeDetector(
            NestedStreamBlock(),
            NestedStreamWithRemovedStructChild(),
            InteractiveDataMigrationQuestioner(),
        )
        comparer.create_data_migration_operations()

        expected_operations_and_block_paths = [
            (RemoveStructChildrenOperation("char1"), "struct1")
        ]

        self.assertOperationsAndPathsEqual(
            comparer.merged_operations_and_block_paths,
            expected_operations_and_block_paths,
        )

    @mock_questioner(ret_value=True, questioner_method="ask_if_block_same")
    @mock_questioner(ret_value=True, questioner_method="ask_if_block_renamed")
    def test_nested_struct_child_renamed(
        self, mock_same_block_questioner, mock_rename_block_questioner
    ):
        comparer = StreamDefChangeDetector(
            NestedStreamBlock(),
            NestedStreamWithRenamedStructChild(),
            InteractiveDataMigrationQuestioner(),
        )
        comparer.create_data_migration_operations()

        expected_operations_and_block_paths = [
            (RenameStructChildrenOperation("char1", "renamed_char1"), "struct1")
        ]

        self.assertOperationsAndPathsEqual(
            comparer.merged_operations_and_block_paths,
            expected_operations_and_block_paths,
        )

    @mock_questioner(ret_value=False, questioner_method="ask_if_block_same")
    @mock_questioner(ret_value=True, questioner_method="ask_if_block_renamed")
    @mock_questioner(ret_value=False, questioner_method="ask_if_block_removed")
    def test_nested_struct_child_renamed_incorrect_input(
        self,
        mock_same_block_questioner,
        mock_rename_block_questioner,
        mock_remove_block_questioner,
    ):
        comparer = StreamDefChangeDetector(
            NestedStreamBlock(),
            NestedStreamWithRenamedStructChild(),
            InteractiveDataMigrationQuestioner(),
        )
        comparer.create_data_migration_operations()

        self.assertEqual(0, len(comparer.merged_operations_and_block_paths))
