from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.migrations.loader import MigrationLoader
from django.db.migrations import Migration
from django.db.migrations.autodetector import MigrationAutodetector
from django.db.migrations.state import ProjectState
from django.db.migrations.writer import MigrationWriter
from django.apps import apps
from wagtail.blocks import StreamBlock, StructBlock

from wagtail_streamfield_migration_toolkit.migrate_operation import MigrateStreamData
from wagtail_streamfield_migration_toolkit.operations import (
    RemoveStreamChildrenOperation,
    RenameStreamChildrenOperation,
    RemoveStructChildrenOperation,
    RenameStructChildrenOperation,
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
            raise CommandError("Required args missing: path")
        try:
            self.app_label, self.model_label, self.field_label = args[0].split(".")
        except ValueError:
            raise CommandError(
                "You must supply path to StreamField as '<app_name>.<model_name>.<field_name>'"
            )

        loader = MigrationLoader(connection=connection)
        loader.build_graph()
        self.project_state = loader.project_state()

        migration_operations = []
        if self.is_rename:
            migration_operations.append(self.make_rename_operation(*options["rename"]))
        if self.is_remove:
            migration_operations.append(self.make_remove_operation(*options["remove"]))
        if not self.is_rename and not self.is_remove:
            migration_operations.append(self.make_empty_operation())

        # TODO do we generate an empty migration with the imports if no flags?
        # Check if its possible to add comments if so.

        migration = Migration(self.migration_name, self.app_label)
        migration.operations = migration_operations

        autodetector = MigrationAutodetector(
            self.project_state, ProjectState.from_apps(apps)
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
                with open(writer.path, "w", encoding="utf-8") as fh:
                    fh.write(migration_string)

    def make_rename_operation(self, *args):

        try:
            if len(args) == 2:
                old_name, new_name = args
                block_path_str = ""
            else:
                old_name, new_name, block_path_str = args
        except ValueError:
            raise CommandError(
                "Rename operation needs the following arguments: <old_name> <new_name> <?block_path>"
            )

        self.block_path_str = block_path_str
        block_def = self.get_block_def()

        if isinstance(block_def, StreamBlock):
            data_operation = RenameStreamChildrenOperation
        elif isinstance(block_def, StructBlock):
            data_operation = RenameStructChildrenOperation
        else:
            raise CommandError("Invalid Block Structure")

        if not self.migration_name:
            self.migration_name = "rename_{}_to_{}".format(
                self.model_label + "_" + self.field_label + "_" + old_name, new_name
            )
        migration_operation = MigrateStreamData(
            self.app_label,
            self.model_label,
            self.field_label,
            [(data_operation(old_name, new_name), block_path_str)],
        )
        return migration_operation

    def make_remove_operation(self, *args):

        try:
            if len(args) == 1:
                block_name = args[0]
                block_path_str = ""
            else:
                block_name, block_path_str = args
        except ValueError:
            raise CommandError(
                "Remove operation needs the following arguments: <block_name> <?block_path>"
            )

        self.block_path_str = block_path_str
        block_def = self.get_block_def()

        if isinstance(block_def, StreamBlock):
            data_operation = RemoveStreamChildrenOperation
        elif isinstance(block_def, StructBlock):
            data_operation = RemoveStructChildrenOperation
        else:
            raise CommandError("Invalid Block Structure")

        if not self.migration_name:
            self.migration_name = "remove_block_{}".format(
                self.model_label + "_" + self.field_label + "_" + block_name
            )
        migration_operation = MigrateStreamData(
            self.app_label,
            self.model_label,
            self.field_label,
            [(data_operation(block_name), block_path_str)],
        )
        return migration_operation

    def make_empty_operation(self):
        migration_operation = MigrateStreamData(
            self.app_label,
            self.model_label,
            self.field_label,
            [],
        )
        return migration_operation

    def get_block_def(self):

        if self.block_path_str == "":
            block_path = []
        else:
            block_path = self.block_path_str.split(".")
        model = self.project_state.apps.get_model(self.app_label, self.model_label)
        stream_field = getattr(model, self.field_label)
        block_def = stream_field.field.stream_block
        while len(block_path) > 0:
            try:
                # For struct and stream block since they have `child_blocks`
                block_def = block_def.child_blocks[block_path[0]]
            except AttributeError:
                # For list blocks since they have `child_block`
                block_def = block_def.child_block
            except KeyError:
                raise CommandError("Invalid Block Path")
            block_path = block_path[1:]

        return block_def
