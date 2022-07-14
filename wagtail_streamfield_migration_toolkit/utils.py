from collections import deque
from wagtail.blocks import ListBlock, StreamBlock, StructBlock

from wagtail_streamfield_migration_toolkit.operations import BaseBlockOperation


# TODO handle block_defs not existing? we'll do this later
# TODO complete descriptions


def is_block_at_path_start(block_name, block_path):
    return block_name == block_path[0]


def map_block_value(
    block_value, block_def, block_path, operation: BaseBlockOperation, **kwargs
):
    # TODO complete description

    # If the `block_path` length is 1, that means we've reached the end of the block path, that
    # is, the block where we need to apply the operation.
    if len(block_path) == 1:

        # Since StreamBlocks, StructBlocks, and ListBlocks have their children in different
        # formats, we have a different `apply_to_` operation for each. Note that for some
        # operations all of these won't be used. For example rename operation won't use
        # `apply_to_list_block_value`, since list blocks don't have any named direct children.
        if isinstance(block_def, StreamBlock):
            mapped_value = operation.apply_to_stream_block_value(
                block_value, block_path[-1]
            )
        elif isinstance(block_def, ListBlock):
            mapped_value = operation.apply_to_list_block_value(
                block_value, block_path[-1]
            )
        elif isinstance(block_def, StructBlock):
            mapped_value = operation.apply_to_struct_block_value(
                block_value, block_path[-1]
            )
        else:
            raise ValueError("Unexpected Structural Block + {}".format(block_value))

        return mapped_value

    # Again, depending on whether the block is a ListBlock, StructBlock or StreamBlock we call a
    # different function to alter its children.

    if isinstance(block_def, StreamBlock):
        mapped_value = map_stream_block_value(
            block_value,
            operation=operation,
            block_def=block_def,
            block_path=block_path,
            **kwargs
        )

    elif isinstance(block_def, ListBlock):
        mapped_value = map_list_block_value(
            block_value,
            operation=operation,
            block_def=block_def,
            block_path=block_path,
            **kwargs
        )

    elif isinstance(block_def, StructBlock):
        mapped_value = map_struct_block_value(
            block_value,
            operation=operation,
            block_def=block_def,
            block_path=block_path,
            **kwargs
        )

    else:
        # TODO figure out if this is needed and how to do it
        raise ValueError("Unexpected Structural Block + {}".format(block_value))

    return mapped_value


def map_stream_block_value(stream_block_value, block_def, block_path, **kwargs):

    mapped_value = []
    for child_block in stream_block_value:

        # If the block is not at the start of `block_path`, then neither it nor it's children are
        # blocks that we need to change.
        if not is_block_at_path_start(child_block["type"], block_path):
            mapped_value.append(child_block)

        else:
            child_block_def = block_def.child_blocks[child_block["type"]]
            mapped_child_value = map_block_value(
                child_block["value"],
                block_def=child_block_def,
                block_path=block_path[1:],
                **kwargs
            )
            mapped_value.append({**child_block, "value": mapped_child_value})

    return mapped_value


def map_struct_block_value(struct_block_value, block_def, block_path, **kwargs):
    altered_value = {}
    for key in struct_block_value:
        child_value = struct_block_value[key]

        # If the block is not at the start of `block_path`, then neither it nor it's children are
        # blocks that we need to change.
        if not is_block_at_path_start(key, block_path):
            altered_value[key] = child_value

        else:
            child_block_def = block_def.child_blocks[key]
            altered_child_value = map_block_value(
                child_value,
                block_def=child_block_def,
                block_path=block_path[1:],
                **kwargs
            )
            altered_value[key] = altered_child_value

    return altered_value


# TODO listblock item multiple ways, decide final approach
# 1. user passes '...item...' in `block_path_str` itself
#   - ad: can access listblock and immediate child separately for applying operations
#           eg:- to change values. If this is not the case user will have to use an operation which 
#           takes the parent listblocks values and updates all of them. Have to see if it's okay,
#           depending on how other operations have their `apply_to` operations; if it is only at
#           block level then it is problematic: for example, if we're doing a value change and
#           for stream and struct children it is applied directly to the child, while only for
#           lists it is applied to the parent. This may be even more problematic if there is a
#           listblock inside a listblock
#   - dis: this feels a bit ugly? since item isn't a name defined by the user, but internally
#           added for listblocks.
# 2. 'item' is automatically prepended to `block_path` when we come across a list block
#   - dis: user can't access listblock and immediate child separately, refer above
#   - dis: this becomes a little messy with the current way we recurse through blocks, since we 
#   -       can't do this just in one place (we will need to do this in the parent itself)
# TODO if user passes 'item', update descriptions
# Currently going with option 1


def map_list_block_value(list_block_value, block_def, block_path, **kwargs):

    mapped_value = []
    for child_block in list_block_value:

        mapped_child_value = map_block_value(
            child_block["value"],
            block_def=block_def.child_block,
            block_path=block_path[1:],
            **kwargs
        )

        mapped_value.append({**child_block, "value": mapped_child_value})

    return mapped_value


def apply_changes_to_raw_data(
    raw_data, block_path_str, operation, streamfield, **kwargs
):
    """
    Applies changes to raw stream data

    Args:
        raw_data:
            The current stream data (a list of top level blocks)
        block_path_str:
            Should be a '.' separated list of names of the blocks from the top level block to 
            the nested block which is to be changed.

            eg:- 'simplestream.char1' would point to,
                [..., { type: simplestream, value: [..., {type: char1, value: ''}] }]

            NOTE: When the path contains a ListBlock child, 'item' must be added to the block as
            the name of said child.

            eg:- 'list1.item.char1' where the list child is a StructBlock would point to,
                [
                    ...,
                    {
                        type: list1,
                        value: [
                            {
                                type: item,
                                value: { ..., char1: "" }
                            },
                            ...
                        ]
                    }
                ]
        operation:
            A subclass of `operations.BaseBlockOperation`. It will have the `apply_to_` methods
            for applying changes to the parent block of the block type that must be changed.
        streamfield:
            The streamfield for which data is being migrated. This is used to get the definitions
            of the blocks.

    Returns:
        altered_raw_data:
    """

    block_path = block_path_str.split(".")
    block_def = streamfield.field.stream_block

    # TODO map rename convention
    altered_raw_data = map_block_value(
        raw_data,
        block_def=block_def,
        block_path=block_path,
        operation=operation,
        **kwargs
    )

    return altered_raw_data
