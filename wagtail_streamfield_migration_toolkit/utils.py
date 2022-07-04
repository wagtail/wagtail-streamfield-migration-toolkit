from collections import deque
from wagtail.blocks import ListBlock, StreamBlock, StructBlock

from wagtail_streamfield_migration_toolkit.operations import BaseBlockOperation


class BlockTree:
    def __init__(self, streamfield, block_path_str):
        self.stream_block = streamfield.field.stream_block
        self.block_path = self.parse_block_path(block_path_str)
        self.block_path_len = len(self.block_path)

        self.curr_block_def_stack = deque()
        self.curr_path_ind = -1

    def get_block_path_end(self):
        return self.block_path[-1]

    def is_block_in_path(self, block):
        if block["type"] == self.block_path[self.curr_path_ind + 1]:
            return True
        return False

    def is_block_at_path_end(self):
        # this is done without pushing a block onto the stack, so ind+2 is taken
        return self.block_path_len == self.curr_path_ind + 2

    def is_block_child_at_path_end(self):
        # for struct blocks
        return self.block_path_len == self.curr_path_ind + 2

    def get_curr_block_structure_type(self):
        curr_block_def = self.curr_block_def_stack[-1]

        if isinstance(curr_block_def, StreamBlock):
            return StreamBlock
        elif isinstance(curr_block_def, StructBlock):
            return StructBlock
        elif isinstance(curr_block_def, ListBlock):
            return ListBlock

        # TODO handle leaf level block if necessary
        return None

    def parse_block_path(self, block_path_str):
        block_path = block_path_str.split(".")
        block_path = [""] + block_path
        return block_path

    def push_to_curr_block_stack(self, block):

        if block["type"] == "":
            # this is actually the streamfield itself as a block
            block_def = self.stream_block
            self.curr_path_ind = 0
        else:
            curr_block_def = self.curr_block_def_stack[-1]

            # TODO for listblock, it has a single child block in the attribute `child_block`
            # instead.
            if self.is_curr_block_def_list():
                block_def = curr_block_def.child_block
            else:
                block_def = curr_block_def.child_blocks[block["type"]]
                self.curr_path_ind += 1

        self.curr_block_def_stack.append(block_def)

    def pop_from_curr_block_stack(self):
        # TODO add check for empty
        self.curr_block_def_stack.pop()
        if not self.is_curr_block_def_list():
            self.curr_path_ind -= 1

    def is_curr_block_def_list(self):
        if self.curr_path_ind <= 0:
            return False
        return isinstance(self.curr_block_def_stack[-1], ListBlock)


def get_altered_or_unchanged_block(
    block, operation: BaseBlockOperation, block_tree: BlockTree, **kwargs
):
    # TODO complete description

    if (
        not block_tree.is_block_in_path(block)
        and not block_tree.is_curr_block_def_list()
    ):
        return block

    if block_tree.is_block_at_path_end() and not block_tree.is_curr_block_def_list():
        altered_block = operation.apply_to_block(block)
        return altered_block

    block_tree.push_to_curr_block_stack(block)
    block_structure_type = block_tree.get_curr_block_structure_type()

    if block_structure_type == ListBlock:
        # TODO
        altered_block = {
            **block,
            "value": get_altered_or_unchanged_list_blocks(
                block["value"], operation=operation, block_tree=block_tree, **kwargs
            ),
        }

    elif block_structure_type == StructBlock:
        if block_tree.is_block_child_at_path_end():
            # if a struct child is going to be changed
            altered_block = operation.apply_to_struct_child(
                block, block_tree.get_block_path_end()
            )
        else:
            altered_block = {
                **block,
                "value": get_altered_or_unchanged_struct_children(
                    block["value"], operation=operation, block_tree=block_tree, **kwargs
                ),
            }

    elif block_structure_type == StreamBlock:
        altered_block = {
            **block,
            "value": get_altered_or_unchanged_stream_blocks(
                block["value"], operation=operation, block_tree=block_tree, **kwargs
            ),
        }

    else:
        raise ValueError("This is bad + {}".format(block))

    block_tree.pop_from_curr_block_stack()
    return altered_block


def get_altered_or_unchanged_struct_children(struct_value, **kwargs):
    for key in struct_value:
        struct_value[key] = get_altered_or_unchanged_block(
            {"type": key, "value": struct_value[key]}, **kwargs
        )["value"]
    return struct_value


def get_altered_or_unchanged_list_blocks(blocks, block_tree: BlockTree, **kwargs):
    # TODO
    altered_blocks = []
    for block in blocks:
        altered_or_unchanged_block = get_altered_or_unchanged_block(
            block, block_tree=block_tree, **kwargs
        )
        altered_blocks.append(altered_or_unchanged_block)
    return altered_blocks


def get_altered_or_unchanged_stream_blocks(blocks, **kwargs):
    # TODO complete description

    altered_blocks = []
    for block in blocks:
        altered_or_unchanged_block = get_altered_or_unchanged_block(block, **kwargs)
        if altered_or_unchanged_block is not None:
            # for removing blocks
            altered_blocks.append(altered_or_unchanged_block)

    return altered_blocks


def apply_changes_to_raw_data(
    raw_data, block_path_str, operation, streamfield, *args, **kwargs
):
    # TODO complete description
    block_tree = BlockTree(streamfield, block_path_str)

    # TODO this might be better if we are moving top level blocks (there wouldn't be a common
    # outermost block otherwise)
    field_as_block = {}
    field_as_block["type"] = ""
    field_as_block["value"] = raw_data

    altered_raw_data = get_altered_or_unchanged_block(
        field_as_block, block_tree=block_tree, operation=operation, **kwargs
    )

    return altered_raw_data["value"]
