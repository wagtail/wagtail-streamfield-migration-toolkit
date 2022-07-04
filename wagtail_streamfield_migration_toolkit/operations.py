class BaseBlockOperation:
    def __init__(self):
        pass

    def apply_to_block(self, block):
        raise NotImplementedError

    def apply_to_struct_child(self, parent_block, key):
        raise NotImplementedError


class RenameBlockOperation(BaseBlockOperation):
    def __init__(self, new_name):
        self.new_name = new_name
        super().__init__()

    def apply_to_block(self, block):
        return {**block, "type": self.new_name}

    def apply_to_struct_child(self, parent_block, key):
        value = parent_block["value"].pop(key)
        parent_block["value"][self.new_name] = value
        return parent_block


class RemoveBlockOperation(BaseBlockOperation):
    def __init__(self):
        super().__init__()

    def apply_to_block(self, block):
        return None

    def apply_to_struct_child(self, parent_block, key):
        parent_block["value"].pop(key)
        return parent_block
