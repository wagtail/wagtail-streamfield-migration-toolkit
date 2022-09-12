from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.migrations.autodetector import MigrationAutodetector
from django.db.migrations.loader import MigrationLoader
from django.db.migrations.state import ProjectState
from django.db.migrations.writer import MigrationWriter
from django.db.migrations import Migration, AlterField
from wagtail.fields import StreamField

from wagtail_streamfield_migration_toolkit.autodetect.streamchangedetector import (
    StreamDefChangeDetector,
)
from wagtail_streamfield_migration_toolkit.migrate_operation import MigrateStreamData


class Command(BaseCommand):
    help = "Autodetect StreamField changes (rename and remove) made since the last project state \
        in migrations"

    def handle(self, *args, **options):

        loader = MigrationLoader(connection=connection)
        loader.build_graph()
        project_state = loader.project_state()
        autodetector = MigrationAutodetector(
            project_state, ProjectState.from_apps(apps)
        )
        autodetector_changes = autodetector.changes(loader.graph)

        stream_data_changes = {}

        # `autodetector_changes` is a dict with (key, value) pairs of (app, migration),
        # so here we iterate through the changes for each app
        for app in autodetector_changes:
            migration_operations = []

            changed_streamfields = []
            for op in autodetector_changes[app][0].operations:
                # We don't care about other fields, and there are operations like CreateModel
                # which don't have a field
                if isinstance(op, AlterField) and isinstance(op.field, StreamField):
                    changed_streamfields.append(op)

            for op in changed_streamfields:
                print("\nCHANGES FOR MODEL " + op.model_name)

                old_streamblock = (
                    loader.project_state()
                    .models.get((app, op.model_name))
                    .fields[op.name]
                    .stream_block
                )
                new_streamblock = op.field.stream_block

                comparer = StreamDefChangeDetector(old_streamblock, new_streamblock)
                comparer.create_data_migration_operations()
                # print(comparer.merged_operations_and_block_paths)

                migration_operation = MigrateStreamData(
                    app_name=app,
                    model_name=op.model_name,
                    field_name=op.name,
                    operations_and_block_paths=comparer.merged_operations_and_block_paths,
                )
                migration_operations.append(migration_operation)

            # TODO migration name? This would be easier to do after we add a suggest_name to our
            # `MigrateStreamData` class
            migration = Migration("stream_data_migration", app)
            migration.operations = migration_operations
            stream_data_changes[app] = [migration]

        stream_data_changes = autodetector.arrange_for_graph(
            changes=stream_data_changes,
            graph=loader.graph,
        )

        for app_label, app_migrations in stream_data_changes.items():
            for migration in app_migrations:
                writer = MigrationWriter(migration, True)
                migration_string = writer.as_string()
                with open(writer.path, "w", encoding="utf-8") as fh:
                    fh.write(migration_string)

        self.stdout.write(self.style.SUCCESS("Successfully wrote migration file/s"))
