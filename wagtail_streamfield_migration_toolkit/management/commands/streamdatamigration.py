from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.migrations.loader import MigrationLoader
from django.db.migrations import Migration
from django.db.migrations.autodetector import MigrationAutodetector
from django.db.migrations.state import ProjectState
from django.db.migrations.writer import MigrationWriter
from django.apps import apps

from wagtail_streamfield_migration_toolkit.migrate_operation import MigrateStreamData
from wagtail_streamfield_migration_toolkit.operations import (
    RemoveStreamChildrenOperation,
    RenameStreamChildrenOperation,
)


class Command(BaseCommand):
    help = "Generates Data Migration for specified operation"

    def add_arguments(self, parser):
        parser.add_argument(
            "args",
            metavar="args",
            nargs="*",
            help="Specify the path of the streamfield to migrate data",
        )
        parser.add_argument("--name", help="Use this name for migration file")
        parser.add_argument(
            "--rename", nargs="*", help="Rename block <path> <old_name> <new_name>"
        )
        parser.add_argument("--remove", nargs="*", help="Remove block <block>")
        # TODO check better ways to take args

    def handle(self, *args, **options):

        self.is_rename = options["rename"] is not None
        self.is_remove = options["remove"] is not None
        self.migration_name = options["name"]

        if not args:
            raise CommandError("Required args missing")
        try:
            self.app_label, self.model_label, self.field_label = args[0].split(".")
        except ValueError:
            raise CommandError(
                "You must supply path to StreamField as '<app_name>.<model_name>.<field_name>'"
            )

        # TODO do we have to add a check for flags being mutually exclusive?
        if self.is_rename:
            migration_operation = self.make_rename_operation(*options["rename"])
        elif self.is_remove:
            migration_operation = self.make_remove_operation(*options["remove"])
            pass
        else:
            # TODO do we generate an empty migration with the imports?
            # Check if its possible to add comments if so.
            migration_operation = None
            pass

        migration = Migration(self.migration_name, self.app_label)
        if migration_operation:
            migration.operations = [migration_operation]

        loader = MigrationLoader(connection=connection)
        loader.build_graph()
        autodetector = MigrationAutodetector(
            loader.project_state(), ProjectState.from_apps(apps)
        )
        changes = {self.app_label: [migration]}
        changes = autodetector.arrange_for_graph(
            changes=changes,
            graph=loader.graph,
            migration_name=self.migration_name,
        )

        # we're probably going to have only one value here though
        for app_label, app_migrations in changes.items():
            for migration in app_migrations:
                # check here
                writer = MigrationWriter(migration, True)
                migration_string = writer.as_string()
                print(migration_string)

    def make_rename_operation(self, *args):

        try:
            if len(args) == 2:
                old_name, new_name = args
                block_path = ""
            else:
                block_path, old_name, new_name = args
        except ValueError:
            raise CommandError(
                "Rename operation needs the following arguments: <block_path> <old_name> <new_name>"
            )
        # TODO go through structure and figure out the relevant parent type and operation

        if not self.migration_name:
            self.migration_name = "rename_{}_to_{}".format(old_name, new_name)
        migration_operation = MigrateStreamData(
            self.app_label,
            self.model_label,
            self.field_label,
            [(RenameStreamChildrenOperation(old_name, new_name), block_path)],
        )
        return migration_operation

    def make_remove_operation(self, *args):

        try:
            if len(args) == 1:
                block_name = args[0]
                block_path = ""
            else:
                block_path, block_name = args
        except ValueError:
            raise CommandError(
                "Remove operation needs the following arguments: <block_path> <block_name>"
            )
        # TODO go through structure and figure out the relevant parent type and operations

        if not self.migration_name:
            self.migration_name = "remove_block_{}".format(block_name)
        migration_operation = MigrateStreamData(
            self.app_label,
            self.model_label,
            self.field_label,
            [(RemoveStreamChildrenOperation(block_name), block_path)],
        )
        return migration_operation
