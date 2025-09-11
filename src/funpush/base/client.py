from .message import BaseMessage


class BaseClient:
    def __init__(self):
        pass

    def login(self, *args, **kwargs):
        raise NotImplementedError

    def send(self, message: BaseMessage, *args, **kwargs):
        raise NotImplementedError()
