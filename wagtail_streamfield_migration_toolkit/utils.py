from collections import deque
from wagtail.blocks import ListBlock, StreamBlock, StructBlock

from wagtail_streamfield_migration_toolkit.operations import BaseBlockOperation


# TODO complete descriptions
# TODO see if a BlockPath Class will be helpful for operations involving moving blocks


def is_block_in_path(block, block_path):
    return block["type"] == block_path[0]


def get_block_structure_type(block_def):
    # for blocks with children, returns whether it is a StreamBlock, StructBlock or ListBlock

    if isinstance(block_def, StreamBlock):
        return StreamBlock
    elif isinstance(block_def, StructBlock):
        return StructBlock
    elif isinstance(block_def, ListBlock):
        return ListBlock

    # TODO check if handling this is necessary
    return None


def parse_block_path(block_path_str):
    # currently block_path_str should be a '.' separated list of names of the blocks from
    # the top level block to the nested block which is subject to the operation
    # eg:- `simplestream.char1`
    block_path = block_path_str.split(".")
    return block_path


def get_altered_or_unchanged_block(
    block,
    block_def,
    block_path,
    operation: BaseBlockOperation,
    is_list_child=False,
    **kwargs
):
    """
    TODO complete description
    """

    block_structure_type = get_block_structure_type(block_def)

    if not is_block_in_path(block, block_path) and not is_list_child:
        return block

    elif len(block_path) == 1:
        altered_block = operation.apply_to_block(block)

    elif block_structure_type == ListBlock:
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

    for key in struct_value.copy():
        # we actually remove the key, value pair from the dict here
        value = struct_value.pop(key)
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
            struct_value[altered_block["type"]] = altered_block["value"]
    return struct_value


def get_altered_or_unchanged_list_blocks(blocks, block_def, block_path, **kwargs):
    altered_blocks = []
    for block in blocks:
        altered_or_unchanged_block = get_altered_or_unchanged_block(
            block,
            block_def=block_def.child_block,
            block_path=block_path,
            is_list_child=True,
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

        # if the return value is None, then it's a remove operation
        if altered_or_unchanged_block is not None:
            altered_blocks.append(altered_or_unchanged_block)
    return altered_blocks


def apply_changes_to_raw_data(
    raw_data, block_path_str, operation, streamfield, **kwargs
):
    """
    TODO complete description
    """

    # block_path_str looks like `simplestream.char1`
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
