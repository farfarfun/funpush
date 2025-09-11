"""
钉钉自定义机器人消息类型实现

支持的消息类型：
- 文本消息 (text)
- 链接消息 (link)
- Markdown消息 (markdown)
- ActionCard消息 (actionCard)
- FeedCard消息 (feedCard)

参考文档：https://open.dingtalk.com/document/robots/custom-robot-access
"""

from typing import List, Optional, Dict, Any
from urllib.parse import quote

from funpush.base.message import BaseMessage


class DingTalkBaseMessage(BaseMessage):
    """钉钉消息基类

    提供@功能的基础实现，所有钉钉消息类型都应继承此类。
    """

    def __init__(
        self,
        mobiles: Optional[List[str]] = None,
        user_ids: Optional[List[str]] = None,
        at_all: bool = False,
        *args,
        **kwargs,
    ) -> None:
        """
        初始化钉钉消息基类

        Args:
            mobiles: 被@人的手机号列表。注意需要在消息内容里添加@人的手机号，
                    且只有群内成员才可被@，非群内成员手机号会被脱敏
            user_ids: 被@人的用户userid列表。注意需要在消息内容里添加@人的userid
            at_all: 是否@所有人
            *args: 传递给父类的位置参数
            **kwargs: 传递给父类的关键字参数
        """
        super().__init__(*args, **kwargs)
        self.mobiles = mobiles or []
        self.user_ids = user_ids or []
        self.at_all = at_all

        # 参数验证
        self._validate_at_params()

    def _validate_at_params(self) -> None:
        """验证@相关参数

        Raises:
            ValueError: 当参数格式不正确时
        """
        if self.mobiles and not isinstance(self.mobiles, list):
            raise ValueError("mobiles 必须是字符串列表")
        if self.user_ids and not isinstance(self.user_ids, list):
            raise ValueError("user_ids 必须是字符串列表")
        if not isinstance(self.at_all, bool):
            raise ValueError("at_all 必须是布尔值")

    def build_at(self) -> Dict[str, Any]:
        """构建@信息

        Returns:
            包含@信息的字典
        """
        return {
            "atMobiles": self.mobiles,
            "atUserIds": self.user_ids,
            "isAtAll": self.at_all,
        }


class DingTalkTextMessage(DingTalkBaseMessage):
    """钉钉文本消息类

    用于发送纯文本消息，支持@功能。
    """

    def __init__(self, content: str, *args, **kwargs) -> None:
        """
        初始化文本消息

        Args:
            content: 消息内容，支持换行符
            *args: 传递给父类的位置参数
            **kwargs: 传递给父类的关键字参数

        Raises:
            ValueError: 当content为空或不是字符串时
        """
        super().__init__(*args, **kwargs)

        if not content or not isinstance(content, str):
            raise ValueError("消息内容不能为空且必须是字符串")

        self.content = content.strip()

    def build(self, *args, **kwargs) -> Dict[str, Any]:
        """构建文本消息

        Returns:
            符合钉钉API格式的消息字典
        """
        return {
            "msgtype": "text",
            "text": {"content": self.content},
            "at": self.build_at(),
        }


class DingTalkLinkMessage(DingTalkBaseMessage):
    """钉钉链接消息类

    用于发送包含链接的消息，点击后可跳转到指定URL。
    """

    def __init__(
        self,
        title: str,
        text: str,
        message_url: str,
        pic_url: Optional[str] = None,
        *args,
        **kwargs,
    ) -> None:
        """
        初始化链接消息

        Args:
            title: 消息标题
            text: 消息内容，如果太长只会部分展示
            message_url: 点击消息跳转的URL
            pic_url: 图片URL，可选
            *args: 传递给父类的位置参数
            **kwargs: 传递给父类的关键字参数

        Raises:
            ValueError: 当必要参数为空时
        """
        super().__init__(*args, **kwargs)

        if not title or not isinstance(title, str):
            raise ValueError("标题不能为空且必须是字符串")
        if not text or not isinstance(text, str):
            raise ValueError("内容不能为空且必须是字符串")
        if not message_url or not isinstance(message_url, str):
            raise ValueError("链接URL不能为空且必须是字符串")

        self.title = title.strip()
        self.text = text.strip()
        self.message_url = message_url.strip()
        self.pic_url = pic_url.strip() if pic_url else ""

    def build(self, *args, **kwargs) -> Dict[str, Any]:
        """构建链接消息

        Returns:
            符合钉钉API格式的消息字典
        """
        return {
            "msgtype": "link",
            "link": {
                "title": self.title,
                "text": self.text,
                "messageUrl": self.message_url,
                "picUrl": self.pic_url,
            },
        }


class DingTalkMarkdownMessage(DingTalkBaseMessage):
    """钉钉Markdown消息类

    用于发送支持Markdown格式的富文本消息。
    """

    def __init__(self, title: str, text: str, *args, **kwargs) -> None:
        """
        初始化Markdown消息

        Args:
            title: 首屏会话透出的展示内容
            text: Markdown格式的消息内容
            *args: 传递给父类的位置参数
            **kwargs: 传递给父类的关键字参数

        Raises:
            ValueError: 当必要参数为空时
        """
        super().__init__(*args, **kwargs)

        if not title or not isinstance(title, str):
            raise ValueError("标题不能为空且必须是字符串")
        if not text or not isinstance(text, str):
            raise ValueError("内容不能为空且必须是字符串")

        self.title = title.strip()
        self.text = text.strip()

    def build(self, *args, **kwargs) -> Dict[str, Any]:
        """构建Markdown消息

        Returns:
            符合钉钉API格式的消息字典
        """
        return {
            "msgtype": "markdown",
            "markdown": {"title": self.title, "text": self.text},
            "at": self.build_at(),
        }


class DingTalkActionCardMessage(DingTalkBaseMessage):
    """钉钉ActionCard消息类

    支持单个按钮和多个按钮两种模式的卡片消息。
    """

    def __init__(
        self,
        title: str,
        text: str,
        single_title: Optional[str] = None,
        single_url: Optional[str] = None,
        buttons: Optional[List[Dict[str, str]]] = None,
        btn_orientation: int = 0,
        *args,
        **kwargs,
    ) -> None:
        """
        初始化ActionCard消息

        Args:
            title: 首屏会话透出的展示内容
            text: Markdown格式的消息内容
            single_title: 单个按钮的标题（与single_url配合使用）
            single_url: 单个按钮的跳转URL
            buttons: 多个按钮列表，每个按钮包含title和actionURL
            btn_orientation: 按钮排列方向，0为竖直排列，1为横向排列
            *args: 传递给父类的位置参数
            **kwargs: 传递给父类的关键字参数

        Raises:
            ValueError: 当参数配置不正确时
        """
        super().__init__(*args, **kwargs)

        if not title or not isinstance(title, str):
            raise ValueError("标题不能为空且必须是字符串")
        if not text or not isinstance(text, str):
            raise ValueError("内容不能为空且必须是字符串")

        # 验证按钮配置
        if single_title and single_url:
            if buttons:
                raise ValueError("不能同时设置单个按钮和多个按钮")
        elif buttons:
            if single_title or single_url:
                raise ValueError("不能同时设置单个按钮和多个按钮")
            if not isinstance(buttons, list) or not buttons:
                raise ValueError("buttons必须是非空列表")
            for btn in buttons:
                if (
                    not isinstance(btn, dict)
                    or "title" not in btn
                    or "actionURL" not in btn
                ):
                    raise ValueError("每个按钮必须包含title和actionURL字段")
        else:
            raise ValueError("必须设置单个按钮或多个按钮")

        if btn_orientation not in [0, 1]:
            raise ValueError("btn_orientation必须是0或1")

        self.title = title.strip()
        self.text = text.strip()
        self.single_title = single_title.strip() if single_title else None
        self.single_url = single_url.strip() if single_url else None
        self.buttons = buttons
        self.btn_orientation = btn_orientation

    def build(self, *args, **kwargs) -> Dict[str, Any]:
        """构建ActionCard消息

        Returns:
            符合钉钉API格式的消息字典
        """
        action_card = {
            "title": self.title,
            "text": self.text,
            "btnOrientation": str(self.btn_orientation),
        }

        if self.single_title and self.single_url:
            # 单个按钮模式
            action_card["singleTitle"] = self.single_title
            action_card["singleURL"] = self.single_url
        elif self.buttons:
            # 多个按钮模式
            action_card["btns"] = self.buttons

        return {
            "msgtype": "actionCard",
            "actionCard": action_card,
        }


class DingTalkFeedCardMessage(DingTalkBaseMessage):
    """钉钉FeedCard消息类

    用于发送多条信息的卡片消息，每条信息包含标题、链接和图片。
    """

    def __init__(self, links: List[Dict[str, str]], *args, **kwargs) -> None:
        """
        初始化FeedCard消息

        Args:
            links: 链接列表，每个链接包含title、messageURL和picURL
            *args: 传递给父类的位置参数
            **kwargs: 传递给父类的关键字参数

        Raises:
            ValueError: 当参数格式不正确时
        """
        super().__init__(*args, **kwargs)

        if not links or not isinstance(links, list):
            raise ValueError("links必须是非空列表")

        for link in links:
            if not isinstance(link, dict):
                raise ValueError("每个链接必须是字典")
            required_fields = ["title", "messageURL", "picURL"]
            for field in required_fields:
                if field not in link or not link[field]:
                    raise ValueError(f"每个链接必须包含非空的{field}字段")

        self.links = links

    def build(self, *args, **kwargs) -> Dict[str, Any]:
        """构建FeedCard消息

        Returns:
            符合钉钉API格式的消息字典
        """
        return {"msgtype": "feedCard", "feedCard": {"links": self.links}}


def msg_text(
    content: str,
    mobiles: Optional[List[str]] = None,
    user_ids: Optional[List[str]] = None,
    at_all: bool = False,
) -> Dict[str, Any]:
    """创建文本消息

    Args:
        content: 消息内容
        mobiles: 被@人的手机号列表
        user_ids: 被@人的用户ID列表
        at_all: 是否@所有人

    Returns:
        符合钉钉API格式的消息字典
    """
    return DingTalkTextMessage(
        content, mobiles=mobiles, user_ids=user_ids, at_all=at_all
    ).build()


def msg_link(
    title: str, text: str, message_url: str, pic_url: Optional[str] = None
) -> Dict[str, Any]:
    """创建链接消息

    Args:
        title: 消息标题
        text: 消息内容，如果太长只会部分展示
        message_url: 点击消息跳转的URL，移动端在钉钉客户端内打开，PC端默认侧边栏打开
        pic_url: 图片URL，可选

    Returns:
        符合钉钉API格式的消息字典
    """
    return DingTalkLinkMessage(title, text, message_url, pic_url).build()


def msg_markdown(
    title: str,
    text: str,
    mobiles: Optional[List[str]] = None,
    user_ids: Optional[List[str]] = None,
    at_all: bool = False,
) -> Dict[str, Any]:
    """创建Markdown消息

    Args:
        title: 首屏会话透出的展示内容
        text: Markdown格式的消息内容
        mobiles: 被@人的手机号列表
        user_ids: 被@人的用户ID列表
        at_all: 是否@所有人

    Returns:
        符合钉钉API格式的消息字典
    """
    return DingTalkMarkdownMessage(
        title, text, mobiles=mobiles, user_ids=user_ids, at_all=at_all
    ).build()


def msg_action_card(
    title: str, text: str, single_title: str, single_url: str, btn_orientation: int = 0
) -> Dict[str, Any]:
    """创建单按钮ActionCard消息

    Args:
        title: 首屏会话透出的展示内容
        text: Markdown格式的消息内容
        single_title: 按钮标题
        single_url: 点击按钮跳转的URL
        btn_orientation: 按钮排列方向，0为竖直排列，1为横向排列

    Returns:
        符合钉钉API格式的消息字典
    """
    return DingTalkActionCardMessage(
        title=title,
        text=text,
        single_title=single_title,
        single_url=single_url,
        btn_orientation=btn_orientation,
    ).build()


def msg_action_cards(
    title: str, text: str, titles: List[str], urls: List[str], btn_orientation: int = 0
) -> Dict[str, Any]:
    """创建多按钮ActionCard消息

    Args:
        title: 首屏会话透出的展示内容
        text: Markdown格式的消息内容
        titles: 按钮标题列表
        urls: 按钮跳转URL列表
        btn_orientation: 按钮排列方向，0为竖直排列，1为横向排列

    Returns:
        符合钉钉API格式的消息字典

    Raises:
        ValueError: 当参数不匹配时
    """
    if not titles or not urls:
        raise ValueError("按钮标题和URL列表不能为空")
    if len(titles) != len(urls):
        raise ValueError("按钮标题和URL列表长度必须相同")

    buttons = []
    for i in range(len(titles)):
        buttons.append(
            {
                "title": titles[i],
                "actionURL": f"dingtalk://dingtalkclient/page/link?url={quote(urls[i])}&pc_slide=false",
            }
        )

    return DingTalkActionCardMessage(
        title=title, text=text, buttons=buttons, btn_orientation=btn_orientation
    ).build()


def msg_feed_card(
    titles: List[str], urls: List[str], pics: List[str]
) -> Dict[str, Any]:
    """创建FeedCard消息

    Args:
        titles: 单条信息文本列表
        urls: 点击单条信息跳转的链接列表
        pics: 单条信息图片URL列表

    Returns:
        符合钉钉API格式的消息字典

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

    return DingTalkFeedCardMessage(links).build()
