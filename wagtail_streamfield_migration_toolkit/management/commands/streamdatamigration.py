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
    RenameStreamChildrenOperation,
)


class Command(BaseCommand):
    help = "Under Construction. This just prints out some stuff"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "args",
            metavar="args",
            nargs="*",
            help="Specify the app label(s) to create migrations for.",
        )

    def handle(self, *args, **options):

        loader = MigrationLoader(connection=connection)
        loader.build_graph()
        autodetector = MigrationAutodetector(
            loader.project_state(), ProjectState.from_apps(apps)
        )
        # for now
        migration_name = "foo"

        if not args:
            raise CommandError("You must supply args")
        # will need to determine input format
        app_label = args[0]
        model_label = args[1]
        field_label = args[2]

        # will need one of our StreamDataMigration operations here

        # will need to get relevant args
        migration = Migration("custom", app_label)
        migration_operation = MigrateStreamData(
            app_label,
            model_label,
            field_label,
            [(RenameStreamChildrenOperation(*args[3:]), "")],
        )  # get block path also
        migration.operations = [migration_operation]

        changes = {app_label: [migration]}
        changes = autodetector.arrange_for_graph(
            changes=changes,
            graph=loader.graph,
            migration_name=migration_name,
        )
        # print(changes)

        # we're probably going to have only one value here though
        for app_label, app_migrations in changes.items():
            for migration in app_migrations:
                # check here
                writer = MigrationWriter(migration, True)
                migration_string = writer.as_string()
                print(migration_string)
