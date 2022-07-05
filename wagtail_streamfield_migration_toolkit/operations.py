class BaseBlockOperation:
    def __init__(self):
        pass

    def apply_to_stream_child(self, block):
        raise NotImplementedError


class RenameBlockOperation(BaseBlockOperation):
    def __init__(self, new_name):
        self.new_name = new_name
        super().__init__()

        # Not implemented yet


class RemoveBlockOperation(BaseBlockOperation):
    def __init__(self):
        super().__init__()

        # Not implemented yet
