def parse_block_path(block_path):
    # TODO complete
    return block_path.split(".")


def get_altered_block(block, block_path, new_name):
    # TODO complete
    altered_block = {}
    if len(block_path) == 1:
        altered_block["type"] = new_name
        altered_block["value"] = block["value"]
    elif type(block["value"]) == dict:
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


def get_altered_raw_data(raw_data, block_path, new_name):
    # TODO complete
    # TODO new_name_or_path ?
    # TODO decide if operation wise separate or everything together with operation_label
    parsed_path = parse_block_path(block_path)

    altered_raw_data = get_altered_or_unchanged_blocks(raw_data, parsed_path, new_name)

    return altered_raw_data
