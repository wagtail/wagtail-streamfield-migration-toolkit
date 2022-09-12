from wagtail.blocks import StreamBlock, StructBlock

from .questioner import InteractiveDataMigrationQuestioner
from .comparers import block_def_comparer_registry
from ..operations import (
    RenameStreamChildrenOperation,
    RenameStructChildrenOperation,
    RemoveStreamChildrenOperation,
    RemoveStructChildrenOperation,
)


class StreamDefChangeDetector:
    """Compare the old and new StreamField definitions to detect changes.

    For now, this can only detect rename or remove changes.
    """

    SIMILARITY_THRESHOLD = 0.5

    def __init__(self, old_streamblock_def, new_streamblock_def):
        self.old_streamblock_def = old_streamblock_def
        self.new_streamblock_def = new_streamblock_def

        self.questioner = InteractiveDataMigrationQuestioner()

        # to keep track of mappings for which we need to make an operation
        self.rename_changes = []
        self.remove_changes = []
        # self.block_mapping_by_path = {} # TODO do we keep all the mappings?

        self.rename_operations_and_block_paths = []
        self.remove_operations_and_block_paths = []

    def create_data_migration_operations(self):
        # Find the blocks which have been renamed or removed.
        self.find_renamed_or_removed_defs(
            self.old_streamblock_def, self.new_streamblock_def
        )

        # TODO when making operations we need to figure out a way to either order them or to update
        # paths when having multiple rename operations which act on both a child and a parent. It
        # might be sufficient to reverse sort them based on the old path for now though. This may
        # get more complicated if we later include changes that are not limited to rename or remove.
        self.rename_changes.sort(reverse=True, key=lambda x: x[0])
        self.remove_changes.sort(reverse=True, key=lambda x: x[0])

        self.generate_rename_operations()
        self.generate_remove_operations()

        self.merged_operations_and_block_paths = []
        self.merged_operations_and_block_paths.extend(
            self.rename_operations_and_block_paths
        )
        self.merged_operations_and_block_paths.extend(
            self.remove_operations_and_block_paths
        )

    def find_renamed_or_removed_defs(
        self, old_block_def, new_block_def, parent_path=""
    ):
        """Find renamed or removed blocks by recursively mapping old children to new children.

        We do 2 things here,
        1. For each old child block, try to find if there is a new child block that it will be
        mapped to. If found and requires a rename operation, keep track of that. If not found and
        requires a remove operation, keep track of that.
        2. Repeat 1 for each (nested) child block (if any) of the mapped child block.

        When doing 1, if we can't find a mapping with the same name and structure, we will need to
        go through new child blocks, and if they are considerably similar, ask the user whether the
        block was renamed. When checking similarity, we will need to consider name, args (from
        deconstruct) and children/structure.
        """

        if hasattr(old_block_def, "child_blocks"):
            # for StreamBlocks and StructBlocks
            old_child_defs = old_block_def.child_blocks
            new_child_defs = new_block_def.child_blocks
        elif hasattr(old_block_def, "child_block"):
            # ListBlocks have a single `.child_block`
            old_child_defs = {"item": old_block_def.child_block}
            new_child_defs = {"item": new_block_def.child_block}
        else:
            # Non Structural Blocks don't have children
            return

        # To keep track of the block path. We will need this for creating operations and keeping
        # track
        path_suffix = "" if parent_path == "" else "."

        old_child_names = set(old_child_defs.keys())
        new_child_names = set(new_child_defs.keys())
        # child names that are exclusive to the new children
        new_only_child_names = new_child_names - old_child_names

        for old_child_name in old_child_names:
            old_child_path = parent_path + path_suffix + old_child_name
            old_child_def = old_child_defs[old_child_name]
            is_child_mapped = False

            # For now assume that same name means same block (i.e. the old block wasn't deleted
            # and a new block with the same name added)
            if old_child_name in new_child_names:
                new_child_def = new_child_defs[old_child_name]
                # recursion call
                self.find_renamed_or_removed_defs(
                    old_child_def,
                    new_child_def,
                    old_child_path,
                )
                is_child_mapped = True

            else:
                comparer = block_def_comparer_registry.get_block_def_comparer(
                    old_child_def
                )

                # Find out if the block maps to one of the new only children. If it maps, that
                # would mean that the block has been renamed
                # TODO see if we can order by the similarity score.
                for new_only_child_name in new_only_child_names:
                    new_child_path = parent_path + path_suffix + new_only_child_name
                    new_child_def = new_child_defs[new_only_child_name]

                    # compare the blocks and find whether they are similar enough to be mapped
                    similarity_score = comparer.compare(
                        old_def=old_child_def,
                        old_name=old_child_name,
                        new_def=new_child_def,
                        new_name=new_only_child_name,
                    )
                    if similarity_score >= self.SIMILARITY_THRESHOLD:
                        # ask user whether the block was indeed renamed
                        is_renamed = self.questioner.ask_block_rename(
                            old_path=old_child_path, new_path=new_child_path
                        )
                        if is_renamed:
                            is_child_mapped = True
                            self.rename_changes.append(
                                (
                                    old_child_path,
                                    new_only_child_name,
                                    old_block_def,
                                )
                            )
                            new_only_child_names.remove(new_only_child_name)
                            # recursion call
                            self.find_renamed_or_removed_defs(
                                old_block_def=old_child_def,
                                new_block_def=new_child_def,
                                parent_path=old_child_path,
                            )
                            break

            # if there is no block to map this to, check if it has been removed
            if not is_child_mapped:
                is_removed = self.questioner.ask_block_remove(old_path=old_child_path)
                if is_removed:
                    self.remove_changes.append((old_child_path, old_block_def))

    def generate_rename_operations(self):
        """Generate the rename operations for the corresponding block paths"""

        for old_path, new_name, parent_def in self.rename_changes:
            old_name, rest_of_path = old_path.split(".")[-1], ".".join(
                old_path.split(".")[:-1]
            )
            print("RENAME", old_path, "TO", new_name)
            if isinstance(parent_def, StreamBlock):
                rename_operation = RenameStreamChildrenOperation(old_name, new_name)
                self.rename_operations_and_block_paths.append(
                    (rename_operation, rest_of_path)
                )
            elif isinstance(parent_def, StructBlock):
                rename_operation = RenameStructChildrenOperation(old_name, new_name)
                self.rename_operations_and_block_paths.append(
                    (rename_operation, rest_of_path)
                )

    def generate_remove_operations(self):
        """Generate the remove operations for the corresponding block paths"""

        for old_path, parent_def in self.remove_changes:
            old_name, rest_of_path = old_path.split(".")[-1], ".".join(
                old_path.split(".")[:-1]
            )
            print("REMOVE", old_path)
            if isinstance(parent_def, StreamBlock):
                remove_operation = RemoveStreamChildrenOperation(old_name)
                self.remove_operations_and_block_paths.append(
                    (remove_operation, rest_of_path)
                )
            elif isinstance(parent_def, StructBlock):
                remove_operation = RemoveStructChildrenOperation(old_name)
                self.remove_operations_and_block_paths.append(
                    (remove_operation, rest_of_path)
                )
