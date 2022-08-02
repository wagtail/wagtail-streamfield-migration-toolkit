import json
from django.test import TestCase
from django.db import connection
from django.db.migrations.loader import MigrationLoader
from django.db.migrations import Migration
from django.db.models import JSONField, F
from django.db.models.functions import Cast

from .. import factories, models
from wagtail_streamfield_migration_toolkit.operations import (
    RenameStreamChildrenOperation,
)
from wagtail_streamfield_migration_toolkit.migrate_operation import MigrateStreamData


class TestNonPageModelWithoutRevisions(TestCase):
    @classmethod
    def setUpTestData(cls):
        instances = [None for i in range(3)]
        instances[0] = factories.SampleModelFactory(
            content__0__char1="Test char 1",
            content__1__char1="Test char 2",
            content__2__char2="Test char 3",
            content__3__char2="Test char 4",
        )
        instances[1] = factories.SampleModelFactory(
            content__0__char1="Test char 1",
            content__1__char1="Test char 2",
            content__2__char2="Test char 3",
        )
        instances[2] = factories.SampleModelFactory(
            content__0__char2="Test char 1",
            content__1__char2="Test char 2",
            content__2__char2="Test char 3",
        )

        cls.instances = {
            instance.id: instance.content.raw_data for instance in instances
        }

    class TestMigration(Migration):
        migration_operation = MigrateStreamData(
            "wagtail_streamfield_migration_toolkit_test",
            "SampleModel",
            "content",
            [
                (
                    RenameStreamChildrenOperation(
                        old_name="char1", new_name="renamed1"
                    ),
                    "",
                )
            ],
        )
        operations = [migration_operation]

    def test_migrate_stream_data(self):

        migration = self.TestMigration(
            "test_migration", "wagtail_streamfield_migration_toolkit_test"
        )
        loader = MigrationLoader(connection=connection)
        loader.build_graph()
        project_state = loader.project_state()

        schema_editor = connection.schema_editor(atomic=migration.atomic)
        migration.apply(project_state, schema_editor)

        instances = models.SampleModel.objects.all().annotate(
            raw_content=Cast(F("content"), JSONField())
        )

        for instance in instances:
            prev_content = self.instances[instance.id]
            for old_block, new_block in zip(prev_content, instance.raw_content):
                self.assertEqual(old_block["id"], new_block["id"])
                if old_block["type"] == "char1":
                    self.assertEqual(new_block["type"], "renamed1")
                else:
                    self.assertEqual(old_block["type"], new_block["type"])


class TestPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        instances = [None for i in range(3)]
        instances[0] = factories.SamplePageFactory(
            content__0__char1="Test char 1",
            content__1__char1="Test char 2",
            content__2__char2="Test char 3",
            content__3__char2="Test char 4",
        )
        instances[1] = factories.SamplePageFactory(
            content__0__char1="Test char 1",
            content__1__char1="Test char 2",
            content__2__char2="Test char 3",
        )
        instances[2] = factories.SamplePageFactory(
            content__0__char2="Test char 1",
            content__1__char2="Test char 2",
            content__2__char2="Test char 3",
        )

        cls.instances = {}
        cls.revisions = {}
        for instance in instances:
            cls.instances[instance.id] = instance.content.raw_data
            instance.save_revision()
            instance.save_revision()
            cls.revisions[instance.id] = instance.revisions.all()


    class TestMigration(Migration):
        migration_operation = MigrateStreamData(
            "wagtail_streamfield_migration_toolkit_test",
            "SamplePage",
            "content",
            [
                (
                    RenameStreamChildrenOperation(
                        old_name="char1", new_name="renamed1"
                    ),
                    "",
                )
            ],
        )
        operations = [migration_operation]

    def test_migrate_stream_data(self):

        migration = self.TestMigration(
            "test_migration", "wagtail_streamfield_migration_toolkit_test"
        )
        loader = MigrationLoader(connection=connection)
        loader.build_graph()
        project_state = loader.project_state()

        schema_editor = connection.schema_editor(atomic=migration.atomic)
        migration.apply(project_state, schema_editor)

        instances = models.SamplePage.objects.all().annotate(
            raw_content=Cast(F("content"), JSONField())
        )

        for instance in instances:
            prev_content = self.instances[instance.id]
            for old_block, new_block in zip(prev_content, instance.raw_content):
                self.assertEqual(old_block["id"], new_block["id"])
                if old_block["type"] == "char1":
                    self.assertEqual(new_block["type"], "renamed1")
                else:
                    self.assertEqual(old_block["type"], new_block["type"])

    def test_migrate_revisions(self):
        migration = self.TestMigration(
            "test_migration", "wagtail_streamfield_migration_toolkit_test"
        )
        loader = MigrationLoader(connection=connection)
        loader.build_graph()
        project_state = loader.project_state()

        schema_editor = connection.schema_editor(atomic=migration.atomic)
        migration.apply(project_state, schema_editor)

        instances = models.SamplePage.objects.all().annotate(
            raw_content=Cast(F("content"), JSONField())
        )

        for instance in instances:
            prev_revisions = self.revisions[instance.id]
            for old_revision, new_revision in zip(prev_revisions, instance.revisions.all()):
                old_content = json.loads(old_revision.content['content'])
                new_content = json.loads(old_revision.content['content'])
                for old_block, new_block in zip(old_content, new_content):
                    self.assertEqual(old_block["id"], new_block["id"])
                    if old_block["type"] == "char1":
                        self.assertEqual(new_block["type"], "renamed1")
                    else:
                        self.assertEqual(old_block["type"], new_block["type"])


# TODO for non page model with revisions