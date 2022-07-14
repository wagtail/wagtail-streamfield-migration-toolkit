class BaseBlockOperation:
    def __init__(self):
        pass

    def apply(self, block_value, child_block_name):
        raise NotImplementedError


class RenameStreamChildrenOperation(BaseBlockOperation):
    def __init__(self, new_name):
        super().__init__()
        self.new_name = new_name

    def apply(self, block_value, child_block_name):
        mapped_block_value = []
        for child_block in block_value:
            if child_block["type"] == child_block_name:
                mapped_block_value.append({**child_block, "type": self.new_name})
            else:
                mapped_block_value.append(child_block)
        return mapped_block_value


class RenameStructChildrenOperation(BaseBlockOperation):
    def __init__(self, new_name):
        super().__init__()
        self.new_name = new_name

    def apply(self, block_value, child_block_name):
        mapped_block_value = {}
        for key in block_value:
            if key == child_block_name:
                mapped_block_value[self.new_name] = block_value[key]
            else:
                mapped_block_value[key] = block_value[key]
        return mapped_block_value


class RemoveStreamChildrenOperation(BaseBlockOperation):
    def __init__(self):
        super().__init__()

    def apply(self, block_value, child_block_name):
        mapped_block_value = []
        for child_block in block_value:
            if child_block["type"] == child_block_name:
                continue
            else:
                mapped_block_value.append(child_block)
        return mapped_block_value


class RemoveStructChildrenOperation(BaseBlockOperation):
    def __init__(self):
        super().__init__()

    def apply(self, block_value, child_block_name):
        mapped_block_value = {}
        for key in block_value:
            if key == child_block_name:
                continue
            else:
                mapped_block_value[key] = block_value[key]
        return mapped_block_value
