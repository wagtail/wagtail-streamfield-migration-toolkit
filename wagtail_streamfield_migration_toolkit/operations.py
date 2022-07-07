class BaseBlockOperation:
    def __init__(self):
        pass

    def apply_to_block(self, block):
        raise NotImplementedError


class RenameBlockOperation(BaseBlockOperation):
    def __init__(self, new_name):
        self.new_name = new_name
        super().__init__()

    def apply_to_block(self, block):
        return {**block, "type": self.new_name}


class RemoveBlockOperation(BaseBlockOperation):
    def __init__(self):
        super().__init__()

    def apply_to_block(self, block):
        return None
