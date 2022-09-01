import datetime
from django.test import TestCase
from django.utils import timezone
from wagtail.blocks import StreamValue

from wagtail_streamfield_migration_toolkit import migrate_operation

from .test_migrations import MigrationTestMixin
from .. import factories, models
from wagtail_streamfield_migration_toolkit.utils import (
    apply_changes_to_raw_data,
    InvalidBlockDefError,
)
from wagtail_streamfield_migration_toolkit.operations import (
    RenameStructChildrenOperation,
    RenameStreamChildrenOperation,
)


class TestExceptionRaisedInRawData(TestCase):
    """Directly test whether an exception is raised by apply_changes_to_raw_data for invalid defs.

    This would happen in a situation where the user gives a block path which contains a block name
    which is not present in the block definition in the project state at which the migration is
    applied. (There should also be a block in the stream data with the said name for this to happen)
    """

    @classmethod
    def setUpTestData(cls):
        raw_data = factories.SampleModelFactory(
            content__0__char1__value="Char Block 1",
            content__1="nestedstruct",
        ).content.raw_data
        raw_data.append(
            {
                "type": "invalid_name1",
                "id": "0001",
                "value": {"char1": "foo", "char2": "foo"},
            }
        )
        raw_data.append(
            {
                "type": "invalid_name1",
                "id": "0002",
                "value": {"char1": "foo", "char2": "foo"},
            }
        )
        raw_data[1]["value"]["invalid_name2"] = [
            {"type": "char1", "value": "foo", "id": "0003"}
        ]
        cls.raw_data = raw_data

    def test_rename_invalid_stream_child(self):
        """TODO"""

        with self.assertRaisesMessage(
            InvalidBlockDefError, "No current block def named invalid_name1"
        ):
            apply_changes_to_raw_data(
                raw_data=self.raw_data,
                block_path_str="invalid_name1",
                operation=RenameStructChildrenOperation(
                    old_name="char1", new_name="renamed1"
                ),
                streamfield=models.SampleModel.content,
            )

    def test_rename_invalid_struct_child(self):
        """TODO"""

        with self.assertRaisesMessage(
            InvalidBlockDefError, "No current block def named invalid_name2"
        ):
            apply_changes_to_raw_data(
                raw_data=self.raw_data,
                block_path_str="nestedstruct.invalid_name2",
                operation=RenameStreamChildrenOperation(
                    old_name="char1", new_name="renamed1"
                ),
                streamfield=models.SampleModel.content,
            )


class TestExceptionRaisedForInstance(TestCase, MigrationTestMixin):
    """Exception should always be raised when applying migration if it occurs while migrating the
    instance data"""

    model = models.SamplePage

    @classmethod
    def setUpTestData(cls):
        instance = factories.SamplePageFactory(
            content__0__char1__value="Char Block 1",
            content__1="nestedstruct",
        )
        raw_data = instance.content.raw_data
        raw_data.append(
            {
                "type": "invalid_name1",
                "id": "0001",
                "value": {"char1": "foo", "char2": "foo"},
            }
        )
        raw_data.append(
            {
                "type": "invalid_name1",
                "id": "0002",
                "value": {"char1": "foo", "char2": "foo"},
            }
        )
        stream_block = instance.content.stream_block
        instance.content = StreamValue(
            stream_block=stream_block, stream_data=raw_data, is_lazy=True
        )
        instance.save()

    def test_migrate(self):

        with self.assertRaisesMessage(
            InvalidBlockDefError, "No current block def named invalid_name1"
        ):
            self.apply_migration(
                operations_and_block_path=[
                    (
                        RenameStructChildrenOperation(
                            old_name="char1", new_name="renamed1"
                        ),
                        "invalid_name1",
                    )
                ],
                revisions_from=timezone.now() + datetime.timedelta(days=2),
            )


class TestExceptionRaisedForLatestRevision(TestCase, MigrationTestMixin):
    """Exception should always be raised when applying migration if it occurs while migrating the
    latest revision data"""

    model = models.SamplePage

    @classmethod
    def setUpTestData(cls):
        instance = factories.SamplePageFactory(
            content__0__char1__value="Char Block 1",
            content__1="nestedstruct",
        )

        for i in range(4):
            revision = instance.save_revision()
            revision.created_at = timezone.now() - datetime.timedelta(days=(5 - i))
            revision.save()

        raw_data = instance.content.raw_data
        raw_data.append(
            {
                "type": "invalid_name1",
                "id": "0001",
                "value": {"char1": "foo", "char2": "foo"},
            }
        )
        raw_data.append(
            {
                "type": "invalid_name1",
                "id": "0002",
                "value": {"char1": "foo", "char2": "foo"},
            }
        )
        stream_block = instance.content.stream_block
        instance.content = StreamValue(
            stream_block=stream_block, stream_data=raw_data, is_lazy=True
        )
        instance.save()

        revision = instance.save_revision()
        revision.created_at = timezone.now()
        revision.save()

        raw_data = instance.content.raw_data
        raw_data = raw_data[:2]
        stream_block = instance.content.stream_block
        instance.content = StreamValue(
            stream_block=stream_block, stream_data=raw_data, is_lazy=True
        )
        instance.save()

    def test_migrate(self):
        with self.assertRaisesMessage(
            InvalidBlockDefError, "No current block def named invalid_name1"
        ):
            self.apply_migration(
                operations_and_block_path=[
                    (
                        RenameStructChildrenOperation(
                            old_name="char1", new_name="renamed1"
                        ),
                        "invalid_name1",
                    )
                ],
                revisions_from=None,
            )


class TestExceptionRaisedForLiveRevision(TestCase, MigrationTestMixin):
    """Exception should always be raised when applying migration if it occurs while migrating the
    live revision data"""

    model = models.SamplePage

    @classmethod
    def setUpTestData(cls):
        instance = factories.SamplePageFactory(
            content__0__char1__value="Char Block 1",
            content__1="nestedstruct",
        )

        raw_data = instance.content.raw_data
        raw_data.append(
            {
                "type": "invalid_name1",
                "id": "0001",
                "value": {"char1": "foo", "char2": "foo"},
            }
        )
        raw_data.append(
            {
                "type": "invalid_name1",
                "id": "0002",
                "value": {"char1": "foo", "char2": "foo"},
            }
        )
        stream_block = instance.content.stream_block
        instance.content = StreamValue(
            stream_block=stream_block, stream_data=raw_data, is_lazy=True
        )
        instance.save()

        revision = instance.save_revision()
        revision.created_at = timezone.now() - datetime.timedelta(days=(5))
        revision.save()

        raw_data = instance.content.raw_data
        raw_data = raw_data[:2]
        stream_block = instance.content.stream_block
        instance.content = StreamValue(
            stream_block=stream_block, stream_data=raw_data, is_lazy=True
        )
        instance.live_revision = revision
        instance.save()

        for i in range(1, 5):
            revision = instance.save_revision()
            revision.created_at = timezone.now() - datetime.timedelta(days=(5 - i))
            revision.save()

    def test_migrate(self):
        with self.assertRaisesMessage(
            InvalidBlockDefError, "No current block def named invalid_name1"
        ):
            self.apply_migration(
                operations_and_block_path=[
                    (
                        RenameStructChildrenOperation(
                            old_name="char1", new_name="renamed1"
                        ),
                        "invalid_name1",
                    )
                ],
                revisions_from=None,
            )


class TestExceptionIgnoredForOtherRevisions(TestCase, MigrationTestMixin):
    """Exception should not be be raised when applying migration if it occurs while migrating
    revision data which is not of a live or latest revision. Instead an exception should be logged"""

    model = models.SamplePage

    @classmethod
    def setUpTestData(cls):
        instance = factories.SamplePageFactory(
            content__0__char1__value="Char Block 1",
            content__1="nestedstruct",
        )

        raw_data = instance.content.raw_data
        raw_data.append(
            {
                "type": "invalid_name1",
                "id": "0001",
                "value": {"char1": "foo", "char2": "foo"},
            }
        )
        raw_data.append(
            {
                "type": "invalid_name1",
                "id": "0002",
                "value": {"char1": "foo", "char2": "foo"},
            }
        )
        stream_block = instance.content.stream_block
        instance.content = StreamValue(
            stream_block=stream_block, stream_data=raw_data, is_lazy=True
        )
        instance.save()

        revision = instance.save_revision()
        revision.created_at = timezone.now() - datetime.timedelta(days=(5))
        revision.save()

        raw_data = instance.content.raw_data
        raw_data = raw_data[:2]
        stream_block = instance.content.stream_block
        instance.content = StreamValue(
            stream_block=stream_block, stream_data=raw_data, is_lazy=True
        )
        instance.save()

        for i in range(1, 5):
            revision = instance.save_revision()
            revision.created_at = timezone.now() - datetime.timedelta(days=(5 - i))
            revision.save()

    def test_migrate(self):

        with self.assertLogs(level="ERROR") as cm:

            self.apply_migration(
                operations_and_block_path=[
                    (
                        RenameStructChildrenOperation(
                            old_name="char1", new_name="renamed1"
                        ),
                        "invalid_name1",
                    )
                ],
                revisions_from=None,
            )
            self.assertEqual(
                cm.output[0].splitlines()[0],
                "ERROR:"
                + migrate_operation.__name__
                + ":No current block def named invalid_name1",
            )
