class BaseMessage:
    def __init__(self, *args, **kwargs):
        pass

    def build(self):
        raise NotImplementedError()
