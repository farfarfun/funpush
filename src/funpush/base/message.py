class BaseMessage:
    """推送消息的最小接口。"""

    def build(self) -> dict[str, object]:
        """构造渠道 API 所需的消息字典。"""
        raise NotImplementedError()
