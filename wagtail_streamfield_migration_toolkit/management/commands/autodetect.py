from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.migrations.autodetector import MigrationAutodetector
from django.db.migrations.loader import MigrationLoader
from django.db.migrations.operations import AlterField
from django.db.migrations.state import ProjectState
from wagtail.fields import StreamField

from wagtail_streamfield_migration_toolkit.autodetect_utils import (
    StreamDefinitionComparer,
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
                print("Changes for model " + op.model_name)

                old_streamblock = (
                    loader.project_state()
                    .models.get((app, op.model_name))
                    .fields[op.name]
                    .stream_block
                )
                new_streamblock = op.field.stream_block
                # we need to compare these two
                # compare_blocks(old_streamblock, new_streamblock, parent_path="")
                comparer = StreamDefinitionComparer(old_streamblock, new_streamblock)
                comparer.compare_block_defs()

        self.stdout.write(self.style.SUCCESS("Le end"))


# def compare_blocks(old_streamblock, new_streamblock, parent_path):
#     # Will need to check for other parameters

#     has_diff = False
#     path_suffix = "" if parent_path == "" else "."

#     old_names = set(old_streamblock.child_blocks.keys())
#     new_names = set(new_streamblock.child_blocks.keys())
#     common_names = old_names.intersection(new_names)
#     old_only_names = old_names - common_names
#     new_only_names = new_names - common_names

#     if not old_names == new_names:
#         has_diff = True

#     for name in common_names:
#         old_child_block = old_streamblock.child_blocks[name]
#         new_child_block = new_streamblock.child_blocks[name]
#         # Should probably compare label, required etc. in a separate function
#         if not old_child_block.label == new_child_block.label:
#             print(
#                 old_child_block.label,
#                 new_child_block.label,
#             )

#         if isinstance(old_child_block, StreamBlock) or isinstance(
#             old_child_block, StructBlock
#         ):
#             changed = compare_blocks(
#                 old_child_block, new_child_block, parent_path + path_suffix + name
#             )
#             has_diff = has_diff or changed
#             if changed:
#                 pass
#                 # do something?
#         elif isinstance(old_child_block, ListBlock):
#             # compare child block
#             pass

#             # changed = compare_blocks()
#             # has_diff = has_diff or changed
#             # if changed:
#             #     pass
#             #     # do something?

#     for name in old_only_names:
#         print(parent_path + path_suffix + name, " -> ", new_only_names, None)

#     return has_diff
