def parse_block_path(block_path):
    # TODO complete
    return block_path.split(".")


def apply_rename_to_block(block, new_name):
    new_block = {}
    new_block["type"] = new_name
    new_block["value"] = block["value"]
    return new_block


def apply_rename_to_struct_child(block, old_name, new_name):
    temp = block.pop(old_name)
    block[new_name] = temp
    return block


def apply_rename(block, old_name, new_name):
    # TODO complete
    # TODO add logic for struct
    return apply_rename_to_block(block, new_name)


def get_altered_block(block, block_path, new_name):
    # TODO complete
    altered_block = {}
    if len(block_path) == 1:
        altered_block["type"] = new_name
        altered_block["value"] = block["value"]
    elif isinstance(block["value"], dict):
        # it's a struct block
        # TODO
        altered_block = block
    else:
        # TODO
        altered_block["type"] = block["type"]
        altered_block["value"] = get_altered_or_unchanged_blocks(
            block["value"], block_path[1:], new_name
        )

    return altered_block


def get_altered_or_unchanged_blocks(blocks, block_path, new_name):
    # TODO complete

    altered_blocks = []
    for block in blocks:
        # print('\n', block["type"], block_path[0], '\n')
        if block["type"] != block_path[0]:
            altered_blocks.append(block)
        else:
            altered_block = get_altered_block(block, block_path, new_name)
            altered_blocks.append(altered_block)

    return altered_blocks


def apply_changes_to_raw_data(raw_data, block_path, operation_label, *args, **kwargs):
    # TODO complete description
    # TODO new_name_or_path ?
    # TODO decide if operation wise separate or everything together with operation_label
    # TODO decide bottom up or remove and inject
    parsed_path = parse_block_path(block_path)

    altered_raw_data = get_altered_or_unchanged_blocks(raw_data, parsed_path, new_name)
    # rest_of_blocks, separated_blocks = separate_top_or_child_blocks_to_alter(
    #     raw_data, parsed_path
    # )
    # separated_blocks = apply_operation_to_separated_blocks(
    #     separated_blocks, operation_label, *args, **kwargs
    # )
    # # TODO add function to alter specific path
    # altered_raw_data = insert_separated_blocks_to_rest_of_blocks(
    #     rest_of_blocks, separated_blocks
    # )

    return altered_raw_data


def separate_top_or_child_blocks_to_alter(
    top_or_child_blocks, block_path, specific_path=[]
):
    """
    Returns:
        rest_of_blocks:
        separated_blocks:
    """
    # TODO complete description
    # TODO complete
    separated_blocks = []  # tuple of (block, specific_path)
    rest_of_blocks = []

    # TODO loop logic. Move to a separate function
    for ind, block in enumerate(top_or_child_blocks):
        if block["type"] != block_path[0]:
            rest_of_blocks.append(block)
        elif len(block_path) == 1:
            # TODO this is the block that must be separated
            new_specific_path = specific_path + [(block_path[0], ind)]
            separated_blocks.append((block, new_specific_path))
        elif isinstance(block["value"], dict):
            # TODO if it's a struct block
            # TODO if len(block_path) == 2 then a child in struct must be separated
            # TODO decide in the case of a struct child whether we are removing the entire
            # struct block or just removing the child as a key, value pair like thing
            pass
        # TODO check if condition needed for list blocks also
        else:
            stripped_block = {}
            stripped_block["type"] = block["type"]
            new_specific_path = specific_path + [(block_path[0], ind)]
            (
                n_rest_of_blocks,
                n_separated_blocks,
            ) = separate_top_or_child_blocks_to_alter(
                block["value"], block_path, specific_path=new_specific_path
            )
            separated_blocks.extend(n_separated_blocks)
            stripped_block["value"] = n_rest_of_blocks
            rest_of_blocks.append(n_rest_of_blocks)

    return rest_of_blocks, separated_blocks


def insert_separated_blocks_to_rest_of_blocks(rest_of_blocks, separated_blocks):
    # TODO complete description
    # TODO looping through and recursing each specific path may be terribly inefficient
    for (block, specific_path) in separated_blocks:
        # TODO do this in a separate function which can be called recursively

        if len(specific_path) == 1:
            if isinstance(specific_path[0], tuple):
                (_, ind) = specific_path[0]
                rest_of_blocks.insert(ind, block)
            # TODO if not a tuple. probably for struct blocks

        else:
            # TODO complete
            top_path = specific_path[0]
            if isinstance(top_path, tuple):
                (block_type, ind) = top_path
                parent_block = rest_of_blocks[ind]
                altered_child_blocks = insert_separated_blocks_to_rest_of_blocks(
                    parent_block["value"], [(block, specific_path[1:])]
                )
                parent_block["value"] = altered_child_blocks
                rest_of_blocks[ind] = parent_block
            else:
                pass

    return rest_of_blocks


def apply_operation_to_separated_blocks(
    separated_blocks, operation_label, *args, **kwargs
):
    # TODO complete description
    # TODO decide how to get operation. pass externally, use a dict, use if else
    operation = lambda separated_blocks: separated_blocks
    if operation_label == "rename":
        operation = apply_rename

    for ind, separated_block in enumerate(separated_blocks):
        # TODO complete
        # separated block will be like (block, specific_path)
        old_block = separated_block[0]
        specific_path = separated_block[1]
        if isinstance(specific_path[-1], tuple):
            # if its like (name, index)
            old_name = specific_path[-1][0]
        else:
            old_name = specific_path[-1]
        new_block = operation(separated_block[0], old_name=old_name, **kwargs)
        separated_blocks[ind] = (new_block, specific_path)

    return separated_blocks


def apply_changes_to_specific_paths(separated_blocks, operation_label, *args, **kwargs):
    # TODO complete description
    # TODO complete
    pass
