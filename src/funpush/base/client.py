from .message import BaseMessage


class BaseClient:
    """推送客户端的最小接口。"""

    def login(self, *args: object, **kwargs: object) -> None:
        """登录推送渠道；具体渠道实现负责定义参数。"""
        raise NotImplementedError

    def send(self, message: BaseMessage, *args: object, **kwargs: object) -> bool:
        """发送消息并返回是否成功。"""
        raise NotImplementedError()
