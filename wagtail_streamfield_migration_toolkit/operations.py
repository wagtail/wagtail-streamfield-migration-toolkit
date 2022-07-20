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
        for (key, value) in block_value.items():
            if key == self.old_name:
                mapped_block_value[self.new_name] = value
            else:
                mapped_block_value[key] = value
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
        for (key, value) in block_value.items():
            if key == self.name:
                continue
            else:
                mapped_block_value[key] = value
        return mapped_block_value
