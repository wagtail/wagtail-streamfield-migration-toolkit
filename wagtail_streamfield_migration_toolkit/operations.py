class BaseBlockOperation:
    def __init__(self):
        pass

    def apply(self, block_value):
        raise NotImplementedError


class RenameStreamChildrenOperation(BaseBlockOperation):
    def __init__(self, old_name, new_name):
        super().__init__()
        self.old_name = old_name
        self.new_name = new_name

    def apply(self, block_value):
        mapped_block_value = []
        for child_block in block_value:
            if child_block["type"] == self.old_name:
                mapped_block_value.append({**child_block, "type": self.new_name})
            else:
                mapped_block_value.append(child_block)
        return mapped_block_value


class RenameStructChildrenOperation(BaseBlockOperation):
    def __init__(self, old_name, new_name):
        super().__init__()
        self.old_name = old_name
        self.new_name = new_name

    def apply(self, block_value):
        mapped_block_value = {}
        for child_key, child_value in block_value.items():
            if child_key == self.old_name:
                mapped_block_value[self.new_name] = child_value
            else:
                mapped_block_value[child_key] = child_value
        return mapped_block_value


class RemoveStreamChildrenOperation(BaseBlockOperation):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def apply(self, block_value):
        return [
            child_block
            for child_block in block_value
            if child_block["type"] != self.name
        ]


class RemoveStructChildrenOperation(BaseBlockOperation):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def apply(self, block_value):
        return {
            child_key: child_value
            for child_key, child_value in block_value.items()
            if child_key != self.name
        }


class StreamChildrenToListBlockOperation(BaseBlockOperation):
    def __init__(self, block_name, list_block_name):
        super().__init__()
        self.block_name = block_name
        self.list_block_name = list_block_name
        self.temp_blocks = []

    def apply(self, block_value):
        mapped_block_value = []
        for child_block in block_value:
            if child_block["type"] == self.block_name:
                self.temp_blocks.append(child_block)
            else:
                mapped_block_value.append(child_block)

        self.map_temp_blocks_to_list_items()
        new_list_block = {"type": self.list_block_name, "value": self.temp_blocks}
        mapped_block_value.append(new_list_block)
        return mapped_block_value

    def map_temp_blocks_to_list_items(self):
        new_temp_blocks = []
        for block in self.temp_blocks:
            new_temp_blocks.append({**block, "type": "item"})
        self.temp_blocks = new_temp_blocks


class StreamChildrenToStreamBlockOperation(BaseBlockOperation):
    def __init__(self, block_names, stream_block_name):
        super().__init__()
        self.block_names = block_names
        self.stream_block_name = stream_block_name

    def apply(self, block_value):
        mapped_block_value = []
        stream_value = []

        for child_block in block_value:
            if child_block["type"] in self.block_names:
                stream_value.append(child_block)
            else:
                mapped_block_value.append(child_block)

        new_stream_block = {"type": self.stream_block_name, "value": stream_value}
        mapped_block_value.append(new_stream_block)
        return mapped_block_value


class AlterBlockValueOperation(BaseBlockOperation):
    def __init__(self, new_value):
        super().__init__()
        self.new_value = new_value

    def apply(self, block_value):
        return self.new_value


class StreamChildrenToStructBlockOperation(BaseBlockOperation):
    def __init__(self, block_name, struct_block_name):
        super().__init__()
        self.block_name = block_name
        self.struct_block_name = struct_block_name

    def apply(self, block_value):
        mapped_block_value = []
        for child_block in block_value:
            if child_block["type"] == self.block_name:
                mapped_block_value.append(
                    {
                        **child_block,
                        "type": self.struct_block_name,
                        "value": {self.block_name: child_block["value"]},
                    }
                )
            else:
                mapped_block_value.append(child_block)
        return mapped_block_value


# Note: to remember old list format
class ListChildrenToStructBlockOperation(BaseBlockOperation):
    def __init__(self, block_name):
        super().__init__()
        self.block_name = block_name

    def apply(self, block_value):
        mapped_block_value = []
        for child_block in block_value:
            mapped_block_value.append(
                {**child_block, "value": {self.block_name: child_block["value"]}}
            )
        return mapped_block_value
