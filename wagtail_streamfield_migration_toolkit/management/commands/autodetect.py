from turtle import backward
from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.migrations.autodetector import MigrationAutodetector
from django.db.migrations.loader import MigrationLoader
from django.db.migrations.operations import AlterField
from django.db.migrations.state import ProjectState
from wagtail.fields import StreamField


class Command(BaseCommand):
    help = "Under Construction. This just prints out some stuff"

    def handle(self, *args, **options):

        loader = MigrationLoader(connection=connection)
        loader.build_graph()

        autodetector = MigrationAutodetector(
            loader.project_state(), ProjectState.from_apps(apps)
        )
        autodetector_changes = autodetector.changes(loader.graph)

        # `autodetector_changes` is a dict with (key, value) pairs of (app, migration),
        # so here we iterate through the changes for each app
        for app in autodetector_changes:
            print(autodetector_changes[app])
            
            changed_streamfields = []
            for op in autodetector_changes[app][0].operations:
                # We don't care about other fields, and there are operations like CreateModel
                # which don't have a field
                if isinstance(op, AlterField) and isinstance(op.field, StreamField):
                    print(op)
                    changed_streamfields.append(op)

            if len(changed_streamfields) > 0:
                root_node = loader.graph.root_nodes(app)[0]
                backward_plan = loader.graph.backwards_plan(root_node) 
                
                for op in backward_plan:
                    print(op)

        self.stdout.write(self.style.SUCCESS("Le end"))
