from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.migrations.autodetector import MigrationAutodetector
from django.db.migrations.loader import MigrationLoader
from django.db.migrations.operations import AlterField
from django.db.migrations.state import ProjectState
from wagtail.fields import StreamField

from wagtail_streamfield_migration_toolkit.autodetect.streamchangedetector import (
    StreamDefChangeDetector,
)


class Command(BaseCommand):
    help = "Under Construction. This just prints out some stuff"

    def handle(self, *args, **options):

        loader = MigrationLoader(connection=connection)
        loader.build_graph()

        # TODO keep variable with project state
        autodetector = MigrationAutodetector(
            loader.project_state(), ProjectState.from_apps(apps)
        )
        autodetector_changes = autodetector.changes(loader.graph)

        # `autodetector_changes` is a dict with (key, value) pairs of (app, migration),
        # so here we iterate through the changes for each app
        for app in autodetector_changes:
            # print(autodetector_changes[app])

            changed_streamfields = []
            for op in autodetector_changes[app][0].operations:
                # We don't care about other fields, and there are operations like CreateModel
                # which don't have a field
                if isinstance(op, AlterField) and isinstance(op.field, StreamField):
                    # print(op)
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
                # we need to compare these two
                # compare_blocks(old_streamblock, new_streamblock, parent_path="")
                comparer = StreamDefChangeDetector(old_streamblock, new_streamblock)
                comparer.create_data_migration_operations()
                # print(comparer.merged_operations_and_block_paths)

        self.stdout.write(self.style.SUCCESS("Le end"))
