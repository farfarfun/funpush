import hashlib
import json
import time
from collections import deque
from typing import Optional, Dict, Any, List

import requests
from funutil import getLogger
from funpush.base.client import BaseClient

from .model import DingTalkAccess
from .util import get_sign
from ..base import BaseMessage
from .message import (
    DingTalkTextMessage,
    DingTalkLinkMessage,
    DingTalkMarkdownMessage,
    DingTalkActionCardMessage,
    DingTalkFeedCardMessage,
)


logger = getLogger("funpush")


class DingTalkClient(BaseClient):
    """钉钉机器人客户端，用于发送消息。

    该客户端处理向钉钉群组发送消息，具有以下功能：
    - 消息去重以防止垃圾信息
    - 自动签名生成
    - 可配置延迟的速率限制
    """

    # 类常量
    API_URL = "https://oapi.dingtalk.com/robot/send"
    DEFAULT_HEADERS = {"Content-Type": "application/json"}
    DEFAULT_MAX_CACHE_SIZE = 100
    DEFAULT_SEND_DELAY = 3  # 秒

    def __init__(
        self,
        max_cache_size: int = DEFAULT_MAX_CACHE_SIZE,
        send_delay: float = DEFAULT_SEND_DELAY,
    ):
        """初始化钉钉客户端。

        Args:
            max_cache_size: 用于去重的消息哈希缓存最大数量
            send_delay: 消息发送间隔延迟（秒）
        """
        super().__init__()
        self.secret: Optional[str] = None
        self.access_token: Optional[str] = None
        self.max_cache_size = max_cache_size
        self.send_delay = send_delay
        self._message_cache: deque = deque(maxlen=max_cache_size)

    def login(
        self,
        access_token: Optional[str] = None,
        secret: Optional[str] = None,
        access: Optional[DingTalkAccess] = None,
        *args,
        **kwargs,
    ) -> None:
        """配置客户端凭据。

        Args:
            access_token: 钉钉机器人访问令牌
            secret: 钉钉机器人密钥，用于签名生成
            access: 包含令牌和密钥的 DingTalkAccess 对象

        Raises:
            ValueError: 如果既未提供单独凭据也未提供访问对象
        """
        if access:
            self.secret = access.secret
            self.access_token = access.access_token
        else:
            self.secret = secret
            self.access_token = access_token

        if not self.access_token:
            raise ValueError("钉钉客户端需要访问令牌")
        if not self.secret:
            raise ValueError("钉钉客户端需要密钥")

    def send(self, message: BaseMessage, *args, **kwargs) -> bool:
        """向钉钉发送消息。

        Args:
            message: 要发送的消息对象

        Returns:
            bool: 如果消息发送成功返回 True，如果重复或出错返回 False

        Raises:
            ValueError: 如果客户端配置不正确
            requests.RequestException: 如果 API 请求失败
        """
        if not self.access_token or not self.secret:
            raise ValueError("发送消息前必须先登录客户端")

        try:
            msg_data = message.build()

            # 生成消息哈希用于去重
            message_hash = self._generate_message_hash(msg_data)

            # 检查重复消息
            if self._is_duplicate_message(message_hash):
                logger.info("检测到重复消息，跳过发送")
                return False

            # 添加到缓存
            self._message_cache.append(message_hash)

            # 生成签名和时间戳
            timestamp, signature = get_sign(self.secret)

            # 准备请求
            params = {
                "sign": signature,
                "timestamp": timestamp,
                "access_token": self.access_token,
            }

            # 发送请求
            response = requests.post(
                self.API_URL,
                headers=self.DEFAULT_HEADERS,
                data=json.dumps(msg_data, ensure_ascii=False),
                params=params,
                timeout=30,
            )

            # 检查响应
            response.raise_for_status()
            result = response.json()

            if result.get("errcode", 0) != 0:
                error_msg = result.get("errmsg", "未知错误")
                logger.error(f"钉钉 API 错误: {error_msg}")
                return False

            logger.success("消息发送成功")

            # 速率限制
            if self.send_delay > 0:
                time.sleep(self.send_delay)

            return True

        except requests.RequestException as e:
            logger.error(f"发送消息失败: {e}")
            raise
        except Exception as e:
            logger.error(f"发送消息时发生意外错误: {e}")
            return False

    def _generate_message_hash(self, message_data: Dict[str, Any]) -> str:
        """生成用于消息去重的哈希值。

        Args:
            message_data: 消息数据字典

        Returns:
            str: 消息内容的 SHA256 哈希值
        """
        # 从消息数据和凭据创建确定性字符串
        content = json.dumps(message_data, sort_keys=True, ensure_ascii=False)
        hash_input = f"{content}:{self.secret}:{self.access_token}"
        return hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

    def _is_duplicate_message(self, message_hash: str) -> bool:
        """检查消息哈希是否已存在于缓存中。

        Args:
            message_hash: 要检查的消息哈希

        Returns:
            bool: 如果消息重复返回 True，否则返回 False
        """
        return message_hash in self._message_cache

    def clear_message_cache(self) -> None:
        """清空消息去重缓存。"""
        self._message_cache.clear()
        logger.info("消息缓存已清空")

    def get_cache_size(self) -> int:
        """获取消息缓存的当前大小。

        Returns:
            int: 缓存的消息哈希数量
        """
        return len(self._message_cache)

    # 针对不同消息类型的便捷发送方法

    def send_text(
        self,
        content: str,
        mobiles: Optional[List[str]] = None,
        user_ids: Optional[List[str]] = None,
        at_all: bool = False,
    ) -> bool:
        """发送文本消息

        Args:
            content: 消息内容
            mobiles: 被@人的手机号列表
            user_ids: 被@人的用户ID列表
            at_all: 是否@所有人

        Returns:
            bool: 发送成功返回True，否则返回False
        """
        message = DingTalkTextMessage(
            content=content,
            mobiles=mobiles,
            user_ids=user_ids,
            at_all=at_all,
        )
        return self.send(message)

    def send_link(
        self,
        title: str,
        text: str,
        message_url: str,
        pic_url: Optional[str] = None,
    ) -> bool:
        """发送链接消息

        Args:
            title: 消息标题
            text: 消息内容，如果太长只会部分展示
            message_url: 点击消息跳转的URL
            pic_url: 图片URL，可选

        Returns:
            bool: 发送成功返回True，否则返回False
        """
        message = DingTalkLinkMessage(
            title=title,
            text=text,
            message_url=message_url,
            pic_url=pic_url,
        )
        return self.send(message)

    def send_markdown(
        self,
        title: str,
        text: str,
        mobiles: Optional[List[str]] = None,
        user_ids: Optional[List[str]] = None,
        at_all: bool = False,
    ) -> bool:
        """发送Markdown消息

        Args:
            title: 首屏会话透出的展示内容
            text: Markdown格式的消息内容
            mobiles: 被@人的手机号列表
            user_ids: 被@人的用户ID列表
            at_all: 是否@所有人

        Returns:
            bool: 发送成功返回True，否则返回False
        """
        message = DingTalkMarkdownMessage(
            title=title,
            text=text,
            mobiles=mobiles,
            user_ids=user_ids,
            at_all=at_all,
        )
        return self.send(message)

    def send_action_card(
        self,
        title: str,
        text: str,
        single_title: str,
        single_url: str,
        btn_orientation: int = 0,
    ) -> bool:
        """发送单按钮ActionCard消息

        Args:
            title: 首屏会话透出的展示内容
            text: Markdown格式的消息内容
            single_title: 按钮标题
            single_url: 点击按钮跳转的URL
            btn_orientation: 按钮排列方向，0为竖直排列，1为横向排列

        Returns:
            bool: 发送成功返回True，否则返回False
        """
        message = DingTalkActionCardMessage(
            title=title,
            text=text,
            single_title=single_title,
            single_url=single_url,
            btn_orientation=btn_orientation,
        )
        return self.send(message)

    def send_action_cards(
        self,
        title: str,
        text: str,
        buttons: List[Dict[str, str]],
        btn_orientation: int = 0,
    ) -> bool:
        """发送多按钮ActionCard消息

        Args:
            title: 首屏会话透出的展示内容
            text: Markdown格式的消息内容
            buttons: 按钮列表，每个按钮包含title和actionURL
            btn_orientation: 按钮排列方向，0为竖直排列，1为横向排列

        Returns:
            bool: 发送成功返回True，否则返回False
        """
        message = DingTalkActionCardMessage(
            title=title,
            text=text,
            buttons=buttons,
            btn_orientation=btn_orientation,
        )
        return self.send(message)

    def send_feed_card(
        self,
        links: List[Dict[str, str]],
    ) -> bool:
        """发送FeedCard消息

        Args:
            links: 链接列表，每个链接包含title、messageURL和picURL

        Returns:
            bool: 发送成功返回True，否则返回False
        """
        message = DingTalkFeedCardMessage(links=links)
        return self.send(message)

    def send_feed_card_simple(
        self,
        titles: List[str],
        urls: List[str],
        pics: List[str],
    ) -> bool:
        """发送FeedCard消息（简化版本）

        Args:
            titles: 单条信息文本列表
            urls: 点击单条信息跳转的链接列表
            pics: 单条信息图片URL列表

        Returns:
            bool: 发送成功返回True，否则返回False

        Raises:
            ValueError: 当参数列表长度不匹配时
        """
        if not titles or not urls or not pics:
            raise ValueError("标题、URL和图片列表都不能为空")
        if len(titles) != len(urls) or len(titles) != len(pics):
            raise ValueError("标题、URL和图片列表长度必须相同")

        links = []
        for i in range(len(titles)):
            links.append({"title": titles[i], "messageURL": urls[i], "picURL": pics[i]})

        return self.send_feed_card(links)
