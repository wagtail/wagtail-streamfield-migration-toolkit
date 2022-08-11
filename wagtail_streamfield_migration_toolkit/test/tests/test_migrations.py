import json
import datetime
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


class BaseMigrationTest(TestCase):
    model_name = "SampleModel"

    def apply_migration(self, revisions_from=None):
        migration = Migration(
            "test_migration", "wagtail_streamfield_migration_toolkit_test"
        )
        migration_operation = MigrateStreamData(
            "wagtail_streamfield_migration_toolkit_test",
            self.model_name,
            "content",
            [
                (
                    RenameStreamChildrenOperation(
                        old_name="char1", new_name="renamed1"
                    ),
                    "",
                )
            ],
            revisions_from=revisions_from,
        )
        migration.operations = [migration_operation]

        loader = MigrationLoader(connection=connection)
        loader.build_graph()
        project_state = loader.project_state()
        schema_editor = connection.schema_editor(atomic=migration.atomic)
        migration.apply(project_state, schema_editor)


class TestNonPageModelWithoutRevisions(BaseMigrationTest):
    model_name = "SampleModel"

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

    def test_migrate_stream_data(self):
        self.apply_migration()

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


class TestPage(BaseMigrationTest):
    model_name = "SamplePage"

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
            for i in range(5):
                revision = instance.save_revision()
                revision.created_at = datetime.datetime.now() - datetime.timedelta(
                    days=(5 - i)
                )
                if i == 1:
                    instance.live_revision = revision
                    instance.save()
            cls.revisions[instance.id] = list(instance.revisions.all().order_by("id"))

    def test_migrate_stream_data(self):
        self.apply_migration()

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
        self.apply_migration()

        instances = models.SamplePage.objects.all().annotate(
            raw_content=Cast(F("content"), JSONField())
        )

        for instance in instances:
            old_revisions = self.revisions[instance.id]
            for old_revision, new_revision in zip(
                old_revisions, instance.revisions.all().order_by("id")
            ):
                old_content = json.loads(old_revision.content["content"])
                new_content = json.loads(new_revision.content["content"])
                for old_block, new_block in zip(old_content, new_content):
                    self.assertEqual(old_block["id"], new_block["id"])
                    if old_block["type"] == "char1":
                        self.assertEqual(new_block["type"], "renamed1")
                    else:
                        self.assertEqual(old_block["type"], new_block["type"])

    def test_always_migrate_live_and_latest_revisions(self):
        revisions_from = datetime.datetime.now() + datetime.timedelta(days=2)
        self.apply_migration(revisions_from=revisions_from)

        instances = models.SamplePage.objects.all().annotate(
            raw_content=Cast(F("content"), JSONField())
        )

        for instance in instances:
            old_revisions = self.revisions[instance.id]
            for old_revision, new_revision in zip(
                old_revisions, instance.revisions.all().order_by("id")
            ):
                is_latest_or_live = (
                    old_revision.id == instance.live_revision_id
                    or old_revision.id == instance.latest_revision_id
                )
                old_content = json.loads(old_revision.content["content"])
                new_content = json.loads(new_revision.content["content"])
                for old_block, new_block in zip(old_content, new_content):
                    self.assertEqual(old_block["id"], new_block["id"])
                    if is_latest_or_live and old_block["type"] == "char1":
                        self.assertEqual(new_block["type"], "renamed1")
                    else:
                        self.assertEqual(old_block["type"], new_block["type"])

    def test_migrate_revisions_from_date(self):
        revisions_from = datetime.datetime.now() - datetime.timedelta(days=2)
        self.apply_migration(revisions_from=revisions_from)

        instances = models.SamplePage.objects.all().annotate(
            raw_content=Cast(F("content"), JSONField())
        )

        for instance in instances:
            old_revisions = self.revisions[instance.id]
            for old_revision, new_revision in zip(
                old_revisions, instance.revisions.all().order_by("id")
            ):
                is_latest_or_live = (
                    old_revision.id == instance.live_revision_id
                    or old_revision.id == instance.latest_revision_id
                )
                is_after_revisions_from = (
                    old_revision.created_at.timestamp() > revisions_from.timestamp()
                )
                is_altered = is_latest_or_live or is_after_revisions_from
                old_content = json.loads(old_revision.content["content"])
                new_content = json.loads(new_revision.content["content"])
                for old_block, new_block in zip(old_content, new_content):
                    self.assertEqual(old_block["id"], new_block["id"])
                    if is_altered and old_block["type"] == "char1":
                        self.assertEqual(new_block["type"], "renamed1")
                    else:
                        self.assertEqual(old_block["type"], new_block["type"])


class TestNonPageModelWithRevisions(BaseMigrationTest):
    model_name = "SampleModelWithRevisions"

    @classmethod
    def setUpTestData(cls):
        instances = [None for i in range(3)]
        instances[0] = factories.SampleModelWithRevisionsFactory(
            content__0__char1="Test char 1",
            content__1__char1="Test char 2",
            content__2__char2="Test char 3",
            content__3__char2="Test char 4",
        )
        instances[1] = factories.SampleModelWithRevisionsFactory(
            content__0__char1="Test char 1",
            content__1__char1="Test char 2",
            content__2__char2="Test char 3",
        )
        instances[2] = factories.SampleModelWithRevisionsFactory(
            content__0__char2="Test char 1",
            content__1__char2="Test char 2",
            content__2__char2="Test char 3",
        )

        cls.instances = {}
        cls.revisions = {}
        for instance in instances:
            cls.instances[instance.id] = instance.content.raw_data
            for i in range(5):
                revision = instance.save_revision()
                revision.created_at = datetime.datetime.now() - datetime.timedelta(
                    days=(5 - i)
                )
                if i == 1:
                    instance.live_revision = revision
                    instance.save()
            cls.revisions[instance.id] = list(instance.revisions.all().order_by("id"))

    def test_migrate_stream_data(self):
        self.apply_migration()

        instances = models.SampleModelWithRevisions.objects.all().annotate(
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
        self.apply_migration()

        instances = models.SampleModelWithRevisions.objects.all().annotate(
            raw_content=Cast(F("content"), JSONField())
        )

        for instance in instances:
            old_revisions = self.revisions[instance.id]
            for old_revision, new_revision in zip(
                old_revisions, instance.revisions.all().order_by("id")
            ):
                old_content = json.loads(old_revision.content["content"])
                new_content = json.loads(new_revision.content["content"])
                for old_block, new_block in zip(old_content, new_content):
                    self.assertEqual(old_block["id"], new_block["id"])
                    if old_block["type"] == "char1":
                        self.assertEqual(new_block["type"], "renamed1")
                    else:
                        self.assertEqual(old_block["type"], new_block["type"])

    def test_always_migrate_live_and_latest_revisions(self):
        revisions_from = datetime.datetime.now() + datetime.timedelta(days=2)
        self.apply_migration(revisions_from=revisions_from)

        instances = models.SampleModelWithRevisions.objects.all().annotate(
            raw_content=Cast(F("content"), JSONField())
        )

        for instance in instances:
            old_revisions = self.revisions[instance.id]
            for old_revision, new_revision in zip(
                old_revisions, instance.revisions.all().order_by("id")
            ):
                is_latest_or_live = (
                    old_revision.id == instance.live_revision_id
                    or old_revision.id == instance.latest_revision_id
                )
                old_content = json.loads(old_revision.content["content"])
                new_content = json.loads(new_revision.content["content"])
                for old_block, new_block in zip(old_content, new_content):
                    self.assertEqual(old_block["id"], new_block["id"])
                    if is_latest_or_live and old_block["type"] == "char1":
                        self.assertEqual(new_block["type"], "renamed1")
                    else:
                        self.assertEqual(old_block["type"], new_block["type"])

    def test_migrate_revisions_from_date(self):
        revisions_from = datetime.datetime.now() - datetime.timedelta(days=2)
        self.apply_migration(revisions_from=revisions_from)

        instances = models.SampleModelWithRevisions.objects.all().annotate(
            raw_content=Cast(F("content"), JSONField())
        )

        for instance in instances:
            old_revisions = self.revisions[instance.id]
            for old_revision, new_revision in zip(
                old_revisions, instance.revisions.all().order_by("id")
            ):
                is_latest_or_live = (
                    old_revision.id == instance.live_revision_id
                    or old_revision.id == instance.latest_revision_id
                )
                is_after_revisions_from = (
                    old_revision.created_at.timestamp() > revisions_from.timestamp()
                )
                is_altered = is_latest_or_live or is_after_revisions_from
                old_content = json.loads(old_revision.content["content"])
                new_content = json.loads(new_revision.content["content"])
                for old_block, new_block in zip(old_content, new_content):
                    self.assertEqual(old_block["id"], new_block["id"])
                    if is_altered and old_block["type"] == "char1":
                        self.assertEqual(new_block["type"], "renamed1")
                    else:
                        self.assertEqual(old_block["type"], new_block["type"])


# TODO check how this would work with wagtail 3.0
