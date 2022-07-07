from collections import deque
from wagtail.blocks import ListBlock, StreamBlock, StructBlock

from wagtail_streamfield_migration_toolkit.operations import BaseBlockOperation


# TODO handle block_defs not existing? we'll do this later
# TODO complete descriptions
# TODO see if a BlockPath Class will be helpful for operations involving moving blocks


def is_block_at_path_start(block, block_path):
    return block["type"] == block_path[0]


def get_block_structure_type(block_def):
    # Returns whether a block is a StreamBlock, StructBlock or ListBlock.
    # To be used only for blocks with children.

    if isinstance(block_def, StreamBlock):
        return StreamBlock
    elif isinstance(block_def, StructBlock):
        return StructBlock
    elif isinstance(block_def, ListBlock):
        return ListBlock

    # TODO check if handling this is necessary
    return None


def parse_block_path(block_path_str):
    block_path = block_path_str.split(".")
    return block_path


def get_altered_or_unchanged_block(
    block, block_def, block_path, operation: BaseBlockOperation, **kwargs
):
    # TODO complete description

    # If the block is not in the `block_path`, then neither it nor it's children are going to
    # be changed.
    if not is_block_at_path_start(block, block_path):
        return block

    elif len(block_path) == 1:
        altered_block = operation.apply_to_block(block)

    block_structure_type = get_block_structure_type(block_def)

    if block_structure_type == ListBlock:
        altered_block = {
            **block,
            "value": get_altered_or_unchanged_list_blocks(
                block["value"],
                operation=operation,
                block_def=block_def,
                block_path=block_path,
                **kwargs
            ),
        }

    elif block_structure_type == StructBlock:
        altered_block = {
            **block,
            "value": get_altered_or_unchanged_struct_blocks(
                block["value"],
                operation=operation,
                block_def=block_def,
                block_path=block_path,
                **kwargs
            ),
        }

    elif block_structure_type == StreamBlock:
        altered_block = {
            **block,
            "value": get_altered_or_unchanged_stream_blocks(
                block["value"],
                operation=operation,
                block_def=block_def,
                block_path=block_path,
                **kwargs
            ),
        }

    else:
        # TODO figure out if this is needed and how to do it
        raise ValueError("This is bad + {}".format(block))

    return altered_block


def get_altered_or_unchanged_struct_blocks(
    struct_value, block_def, block_path, **kwargs
):
    altered_value = {}
    for key in struct_value:
        # we actually remove the key, value pair from the dict here
        value = struct_value[key]
        child_block_def = block_def.child_blocks[key]

        # Here we pass the key, value pair in the same format as a normal block, that is,
        # { type: key, value: value }
        altered_block = get_altered_or_unchanged_block(
            {"type": key, "value": value},
            block_def=child_block_def,
            block_path=block_path[1:],
            **kwargs
        )

        # if the return value is none, then it's a remove operation and we don't need to add
        # the key, value pair again. Otherwise, we add the returned blocks type and value as the
        # new key, value pair to the dictionary
        if altered_block is not None:
            altered_value[altered_block["type"]] = altered_block["value"]
    return altered_value


# TODO listblock item multiple ways, decide final approach
# 1. user passes '...item...' in `block_path_str` itself
#   - ad: can access listblock and immediate child separately for applying operations
#           eg:- to change values. In this case user will have to use an operation which takes
#           the parent listblocks values and updates all of them. Have to see if it's okay,
#           depending on how other operations have their `apply_to` operations; if it is only at
#           block level then it is problematic: for example, if we're doing a value change and
#           for stream and struct children it is applied directly to the child, while only for
#           lists it is applied to the parent.
#   - dis: this feels a bit ugly? since item isn't a name defined by the user, but internally
#           added for listblocks.
# 2. 'item' is automatically prepended to `block_path` in `get_altered_or_unchanged_list_blocks`
#   - dis: user can't access listblock and immediate child separately, refer above
# TODO if user passes 'item', update descriptions
# Currently going with option 2


def get_altered_or_unchanged_list_blocks(blocks, block_def, block_path, **kwargs):
    # At this point our current block path is like ['list1', 'nestedchild1', ...]
    # However the actual blocks look like,
    # { type: list1, values: [{ type: item, value: { nestedchild1: '', ... } }, ...] }
    #
    # Note that 'item' is not there in the block path. (Since `type: item` is an internal detail
    # added in ListBlocks, not a name given by the user.)
    #
    # If we pass `block_path[1:]` now, it will look like ['nestedchild1', ...],
    # where 'nestedchild1' is actually the child of the list item, not the immediate list child.
    # To make up for this, we prepend 'item' to `block_path[1:]` so it will look like
    # ['item', 'nestedchild1']

    altered_blocks = []
    for block in blocks:

        altered_or_unchanged_block = get_altered_or_unchanged_block(
            block,
            block_def=block_def.child_block,
            block_path=["item"] + block_path[1:],
            **kwargs
        )

        altered_blocks.append(altered_or_unchanged_block)
    return altered_blocks


def get_altered_or_unchanged_stream_blocks(blocks, block_def, block_path, **kwargs):

    altered_blocks = []
    for block in blocks:
        child_block_def = block_def.child_blocks[block["type"]]
        altered_or_unchanged_block = get_altered_or_unchanged_block(
            block, block_def=child_block_def, block_path=block_path[1:], **kwargs
        )

        # if the return value is None, then it's a removed block
        if altered_or_unchanged_block is not None:
            altered_blocks.append(altered_or_unchanged_block)
    return altered_blocks


def apply_changes_to_raw_data(
    raw_data, block_path_str, operation, streamfield, **kwargs
):
    """
    Applies changes to raw stream data

    Args:
        raw_data:
            The current stream data (a list of top level blocks)
        block_path_str:
            Currently `block_path_str` should be a '.' separated list of names of the blocks from
            the top level block to the nested block which is subject to the operation.

            eg:- 'simplestream.char1' would point to,
                [..., { type: simplestream, value: [..., {type: char1, value: ''}] }]
        operation:
            A subclass of `operations.BaseBlockOperation`. It will have the `apply_to` method
            for applying changes to a block.
        streamfield:
            The streamfield for which data is being migrated. This is used to get the definitions
            of the blocks.

    Returns:
        altered_raw_data:
    """

    block_path = parse_block_path(block_path_str)
    block_def = streamfield.field.stream_block

    # TODO this might be better if we are moving top level blocks (there wouldn't be a common
    # outermost block otherwise)
    field_as_block = {}
    field_as_block["type"] = ""
    field_as_block["value"] = raw_data
    block_path = [""] + block_path

    altered_raw_data = get_altered_or_unchanged_block(
        field_as_block,
        block_def=block_def,
        block_path=block_path,
        operation=operation,
        **kwargs
    )

    return altered_raw_data["value"]
