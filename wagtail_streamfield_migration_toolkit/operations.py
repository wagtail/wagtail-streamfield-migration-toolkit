class BaseBlockOperation:
    def __init__(self):
        pass

    def apply_to_stream_block_value(self, block_value, child_block_name):
        raise NotImplementedError

    def apply_to_list_block_value(self, block_value, child_block_name):
        raise NotImplementedError

    def apply_to_struct_block_value(self, block_value, child_block_name):
        raise NotImplementedError


# TODO have separate classes for each parent block type
class RenameBlockOperation(BaseBlockOperation):
    def __init__(self, new_name):
        self.new_name = new_name
        super().__init__()

    def apply_to_stream_block_value(self, block_value, child_block_name):
        mapped_block_value = []
        for child_block in block_value:
            if child_block["type"] == child_block_name:
                mapped_block_value.append({**child_block, "type": self.new_name})
            else:
                mapped_block_value.append(child_block)
        return mapped_block_value

    # Note that `apply_to_list_block_value` should not be called at all for this operation

    def apply_to_struct_block_value(self, block_value, child_block_name):
        mapped_block_value = {}
        for key in block_value:
            if key == child_block_name:
                mapped_block_value[self.new_name] = block_value[key]
            else:
                mapped_block_value[key] = block_value[key]
        return mapped_block_value


class RemoveBlockOperation(BaseBlockOperation):
    def __init__(self):
        super().__init__()

    def apply_to_stream_block_value(self, block_value, child_block_name):
        mapped_block_value = []
        for child_block in block_value:
            if child_block["type"] == child_block_name:
                continue
            else:
                mapped_block_value.append(child_block)
        return mapped_block_value

    # Note that `apply_to_list_block_value` should not be called at all for this operation

    def apply_to_struct_block_value(self, block_value, child_block_name):
        mapped_block_value = {}
        for key in block_value:
            if key == child_block_name:
                continue
            else:
                mapped_block_value[key] = block_value[key]
        return mapped_block_value
