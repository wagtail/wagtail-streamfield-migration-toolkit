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


def questioner_patcher(func, ret_value):
    return mock.patch(
        "wagtail_streamfield_migration_toolkit.autodetect.questioner.InteractiveDataMigrationQuestioner.ask_if_block_removed",
        return_value=ret_value,
    )(func)


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

    # @mock.patch(
    #     "wagtail_streamfield_migration_toolkit.autodetect.questioner.InteractiveDataMigrationQuestioner.ask_if_block_removed",
    #     return_value=True,
    # )
    @questioner_patcher
    def test_stream_child_removed(self, *args, **kwargs):
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

    @mock.patch(
        "wagtail_streamfield_migration_toolkit.autodetect.questioner.InteractiveDataMigrationQuestioner.ask_if_block_renamed",
        return_value=True,
    )
    def test_stream_child_renamed(self, mock1):
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

    @mock.patch(
        "wagtail_streamfield_migration_toolkit.autodetect.questioner.InteractiveDataMigrationQuestioner.ask_if_block_same",
        return_value=True,
    )
    @mock.patch(
        "wagtail_streamfield_migration_toolkit.autodetect.questioner.InteractiveDataMigrationQuestioner.ask_if_block_removed",
        return_value=True,
    )
    def test_nested_struct_child_removed(self, mock1, mock2):
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

    @mock.patch(
        "wagtail_streamfield_migration_toolkit.autodetect.questioner.InteractiveDataMigrationQuestioner.ask_if_block_same",
        return_value=True,
    )
    @mock.patch(
        "wagtail_streamfield_migration_toolkit.autodetect.questioner.InteractiveDataMigrationQuestioner.ask_if_block_renamed",
        return_value=True,
    )
    def test_nested_struct_child_renamed(self, mock1, mock2):
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

    @mock.patch(
        "wagtail_streamfield_migration_toolkit.autodetect.questioner.InteractiveDataMigrationQuestioner.ask_if_block_same",
        return_value=False,
    )
    @mock.patch(
        "wagtail_streamfield_migration_toolkit.autodetect.questioner.InteractiveDataMigrationQuestioner.ask_if_block_renamed",
        return_value=True,
    )
    @mock.patch(
        "wagtail_streamfield_migration_toolkit.autodetect.questioner.InteractiveDataMigrationQuestioner.ask_if_block_removed",
        return_value=False,
    )
    def test_nested_struct_child_renamed_incorrect_input(self, mock1, mock2, mock3):
        comparer = StreamDefChangeDetector(
            NestedStreamBlock(),
            NestedStreamWithRenamedStructChild(),
            InteractiveDataMigrationQuestioner(),
        )
        comparer.create_data_migration_operations()

        self.assertEqual(0, len(comparer.merged_operations_and_block_paths))
