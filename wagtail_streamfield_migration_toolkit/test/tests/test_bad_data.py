from unittest import expectedFailure
from django.test import TestCase

from .. import factories, models
from wagtail_streamfield_migration_toolkit.utils import apply_changes_to_raw_data
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

    @expectedFailure
    def test_rename_invalid_stream_child(self):
        """TODO"""

        apply_changes_to_raw_data(
            raw_data=self.raw_data,
            block_path_str="simplestrum",
            operation=RenameStructChildrenOperation(
                old_name="char1", new_name="renamed1"
            ),
            streamfield=models.SampleModel.content,
        )

    @expectedFailure
    def test_rename_invalid_struct_child(self):
        """TODO"""

        apply_changes_to_raw_data(
            raw_data=self.raw_data,
            block_path_str="nestedstruct.stream2",
            operation=RenameStreamChildrenOperation(
                old_name="char1", new_name="renamed1"
            ),
            streamfield=models.SampleModel.content,
        )
