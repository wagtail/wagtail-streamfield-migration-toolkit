from wagtail.images.blocks import ImageChooserBlock


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
        for key in block_value:
            if key == self.old_name:
                mapped_block_value[self.new_name] = block_value[key]
            else:
                mapped_block_value[key] = block_value[key]
        return mapped_block_value


class RemoveStreamChildrenOperation(BaseBlockOperation):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def apply(self, block_value):
        mapped_block_value = []
        for child_block in block_value:
            if child_block["type"] == self.name:
                continue
            else:
                mapped_block_value.append(child_block)
        return mapped_block_value


class RemoveStructChildrenOperation(BaseBlockOperation):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def apply(self, block_value):
        mapped_block_value = {}
        for key in block_value:
            if key == self.name:
                continue
            else:
                mapped_block_value[key] = block_value[key]
        return mapped_block_value


class StreamChildrenToListBlockOperation(BaseBlockOperation):
    def __init__(self, block_names, list_block_name):
        super().__init__()
        self.block_names = block_names
        self.list_block_name = list_block_name
        self.temp_blocks = []

    def apply(self, block_value):
        mapped_block_value = []
        for child_block in block_value:
            if child_block["type"] in self.block_names:
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


class AlterCharBlockValue(BaseBlockOperation):
    def __init__(self, new_value):
        super().__init__()
        self.new_value = new_value

    def apply(self, block_value):
        return self.new_value

# TODO class ApplyMultipleOperation(BaseBlockOperation):