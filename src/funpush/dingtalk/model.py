class DingTalkAccess:
    """钉钉访问凭据容器。"""

    def __init__(
        self,
        access_token: str | None = None,
        secret: str | None = None,
        *args: object,
        **kwargs: object,
    ) -> None:
        """保存 access token 和签名密钥。"""
        self.access_token = access_token
        self.secret = secret
