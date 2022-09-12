from functools import lru_cache
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

    help = "Generate data migrations with the given operations. Note that you can only \
        generate changes for models in a single app at a time."

    def add_arguments(self, parser):
        parser.add_argument("--name", help="Use this name for migration file")
        subparsers = parser.add_subparsers(dest="operation_type")

        rename_parser = subparsers.add_parser(
            "rename", help="rename a block. rename --help to see options"
        )
        rename_parser.add_argument("app_label", help="app name")
        rename_parser.add_argument("old_name", help="name of the block to be renamed")
        rename_parser.add_argument("new_name", help="new name")
        rename_parser.add_argument(
            "paths",
            nargs="+",
            action="extend",
            help="path/s to the block/s which is being operated on: '<model_name>.<field_name>[.<block_path>]' \
                Note that for rename operations the block being operated on is the parent of the block being \
                renamed.",
        )

        remove_parser = subparsers.add_parser(
            "remove", help="remove a block. remove --help to see options"
        )
        remove_parser.add_argument("app_label", help="app name")
        remove_parser.add_argument("block_name", help="name of the block to remove")
        remove_parser.add_argument(
            "paths",
            nargs="+",
            action="extend",
            help="path/s to the block/s which is being operated on: '<model_name>.<field_name>[.<block_path>]' \
                Note that for remove operations the block being operated on is the parent of the block being \
                removed.",
        )

        # TODO support for more operations : TODO alter value

        # TODO determine how to go ahead with multiple blocks AND operations

    def handle(self, *args, **options):

        if options["operation_type"] == "rename":
            self.operation_maker = self.make_rename_operation
        elif options["operation_type"] == "remove":
            self.operation_maker = self.make_remove_operation
        else:
            raise CommandError("Call the command with an operation. see --help")
        self.paths = options["paths"]
        self.migration_name = options["name"]
        self.app_label = options["app_label"]
        self._migration_names = set()

        # get the project state
        loader = MigrationLoader(connection=connection)
        loader.build_graph()
        self.project_state = loader.project_state()

        # Since a single `MigrateStreamData` operation is defined for a specific streamfield,
        # we will keep the intra field operations for each specific streamfield here.
        operations_and_block_paths_by_model_field = {}

        for path in self.paths:
            model_name, field_name, block_path = self.parse_path(path)
            operation_and_block_path = self.operation_maker(
                block_path=block_path,
                model_name=model_name,
                field_name=field_name,
                **options
            )
            key = (model_name, field_name)
            if key in operations_and_block_paths_by_model_field:
                operations_and_block_paths_by_model_field[key].append(
                    operation_and_block_path
                )
            else:
                operations_and_block_paths_by_model_field[key] = [
                    operation_and_block_path
                ]

        migration = Migration(self.migration_name, self.app_label)
        migration.operations = []
        for (
            model_name,
            field_name,
        ), operations_and_block_paths in (
            operations_and_block_paths_by_model_field.items()
        ):
            migration.operations.append(
                MigrateStreamData(
                    app_name=self.app_label,
                    model_name=model_name,
                    field_name=field_name,
                    operations_and_block_paths=operations_and_block_paths,
                )
            )

        # If the user doesn't give a name for the migration file, generate one based on the
        # operations used.
        if not self.migration_name:
            self.migration_name = "_".join(self._migration_names)[:40]

        elif not self.migration_name.isidentifier():
            raise CommandError("The migration name must be a valid Python identifier.")

        autodetector = MigrationAutodetector(
            self.project_state, ProjectState.from_apps(apps)
        )
        changes = {self.app_label: [migration]}
        changes = autodetector.arrange_for_graph(
            changes=changes,
            graph=loader.graph,
            migration_name=self.migration_name,
        )

        # we're going to have only one value here though
        for app_label, app_migrations in changes.items():
            for migration in app_migrations:
                writer = MigrationWriter(migration, True)
                migration_string = writer.as_string()
                with open(writer.path, "w", encoding="utf-8") as fh:
                    fh.write(migration_string)

    def make_rename_operation(
        self, block_path, model_name, field_name, old_name, new_name, **options
    ):

        block_def = self.get_block_def(
            model_name=model_name, field_name=field_name, block_path=block_path
        )

        if isinstance(block_def, StreamBlock):
            data_operation = RenameStreamChildrenOperation
        elif isinstance(block_def, StructBlock):
            data_operation = RenameStructChildrenOperation
        else:
            raise CommandError(
                "Invalid block structure {} for rename operation.".format(block_def)
            )

        self._migration_names.add(
            "rename_{}_{}_{}_to_{}".format(model_name, field_name, old_name, new_name)
        )
        return (data_operation(old_name, new_name), block_path)

    def make_remove_operation(
        self, block_path, model_name, field_name, block_name, **options
    ):

        block_def = self.get_block_def(
            model_name=model_name, field_name=field_name, block_path=block_path
        )

        if isinstance(block_def, StreamBlock):
            data_operation = RemoveStreamChildrenOperation
        elif isinstance(block_def, StructBlock):
            data_operation = RemoveStructChildrenOperation
        else:
            raise CommandError("Invalid Block Structure")

        self._migration_names.add(
            "remove_{}_{}_{}".format(model_name, field_name, block_name)
        )
        return (data_operation(block_name), block_path)

    def parse_path(self, path):
        try:
            path = path.split(".")
            model_name = path[0]
            field_name = path[1]
            block_path = ".".join(path[2:])
            return model_name, field_name, block_path
        except IndexError:
            raise CommandError(
                "You must supply path to block as '<model_name>.<field_name>.?<block_path>'"
            )

    @lru_cache
    def get_stream_block_def(self, model_name, field_name):
        try:
            model = self.project_state.apps.get_model(self.app_label, model_name)
            stream_field = getattr(model, field_name)
            return stream_field.field.stream_block
        except LookupError as e:
            raise CommandError(e.args)
        except AttributeError:
            raise CommandError(
                "Model {} has no field named {}".format(model_name, field_name)
            )

    def get_block_def(self, model_name, field_name, block_path):

        if block_path == "":
            block_path = []
        else:
            block_path = block_path.split(".")

        block_def = self.get_stream_block_def(model_name, field_name)
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
