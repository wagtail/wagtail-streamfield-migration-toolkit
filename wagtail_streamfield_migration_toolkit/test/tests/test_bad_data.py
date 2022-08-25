import datetime
from django.test import TestCase
from django.utils import timezone
from wagtail.blocks import StreamValue

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

# TODO situations
#   - existing data and given block path both have a block type which does not exist in the block
#     definition (of the project state when the migration is run)


class TestExceptionRaisedInRawData(TestCase):
    """TODO complete"""

    @classmethod
    def setUpTestData(cls):
        raw_data = factories.SampleModelFactory(
            content__0__char1__value="Char Block 1",
            content__1="nestedstruct",
        ).content.raw_data
        raw_data.append(
            {
                "type": "simplestrum",
                "id": "0001",
                "value": {"char1": "foo", "char2": "foo"},
            }
        )
        raw_data.append(
            {
                "type": "simplestrum",
                "id": "0002",
                "value": {"char1": "foo", "char2": "foo"},
            }
        )
        raw_data[1]["value"]["stream2"] = [
            {"type": "char1", "value": "foo", "id": "0003"}
        ]
        cls.raw_data = raw_data

    def test_rename_invalid_stream_child(self):
        """TODO"""

        with self.assertRaisesMessage(
            InvalidBlockDefError, "No current block def named simplestrum"
        ):
            apply_changes_to_raw_data(
                raw_data=self.raw_data,
                block_path_str="simplestrum",
                operation=RenameStructChildrenOperation(
                    old_name="char1", new_name="renamed1"
                ),
                streamfield=models.SampleModel.content,
            )

    def test_rename_invalid_struct_child(self):
        """TODO"""

        with self.assertRaisesMessage(
            InvalidBlockDefError, "No current block def named stream2"
        ):
            apply_changes_to_raw_data(
                raw_data=self.raw_data,
                block_path_str="nestedstruct.stream2",
                operation=RenameStreamChildrenOperation(
                    old_name="char1", new_name="renamed1"
                ),
                streamfield=models.SampleModel.content,
            )


class TestExceptionRaisedForInstance(TestCase, MigrationTestMixin):
    """TODO complete"""

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
                "type": "simplestrum",
                "id": "0001",
                "value": {"char1": "foo", "char2": "foo"},
            }
        )
        raw_data.append(
            {
                "type": "simplestrum",
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
            InvalidBlockDefError, "No current block def named simplestrum"
        ):
            self.apply_migration(
                operations_and_block_path=[
                    (
                        RenameStructChildrenOperation(
                            old_name="char1", new_name="renamed1"
                        ),
                        "simplestrum",
                    )
                ],
                revisions_from=timezone.now() + datetime.timedelta(days=2),
            )


class TestExceptionRaisedForLatestRevision(TestCase, MigrationTestMixin):
    """TODO complete"""

    model = models.SamplePage

    @classmethod
    def setUpTestData(cls):
        instance = factories.SamplePageFactory(
            content__0__char1__value="Char Block 1",
            content__1="nestedstruct",
        )

        for i in range(4):
            revision = instance.save_revision()
            revision.created_at = datetime.datetime.now() - datetime.timedelta(
                days=(5 - i)
            )
            revision.save()

        raw_data = instance.content.raw_data
        raw_data.append(
            {
                "type": "simplestrum",
                "id": "0001",
                "value": {"char1": "foo", "char2": "foo"},
            }
        )
        raw_data.append(
            {
                "type": "simplestrum",
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
        revision.created_at = datetime.datetime.now()
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
            InvalidBlockDefError, "No current block def named simplestrum"
        ):
            self.apply_migration(
                operations_and_block_path=[
                    (
                        RenameStructChildrenOperation(
                            old_name="char1", new_name="renamed1"
                        ),
                        "simplestrum",
                    )
                ],
                revisions_from=None,
            )
