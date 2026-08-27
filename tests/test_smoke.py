"""轻量冒烟测试：验证导入、消息构建、客户端登录/发送流程（网络请求已 mock）。"""
from unittest.mock import MagicMock, patch

import pytest

import funpush
from funpush import DingTalkClient
from funpush.dingtalk.message import (
    DingTalkActionCardMessage,
    DingTalkFeedCardMessage,
    DingTalkLinkMessage,
    DingTalkMarkdownMessage,
    DingTalkTextMessage,
    msg_action_card,
    msg_action_cards,
    msg_feed_card,
    msg_link,
    msg_markdown,
    msg_text,
)
from funpush.dingtalk.model import DingTalkAccess
from funpush.dingtalk.util import get_sign


def test_import_funpush():
    assert funpush.DingTalkClient is DingTalkClient


def test_msg_text_helper():
    data = msg_text("hello", at_all=True)
    assert data == {
        "msgtype": "text",
        "text": {"content": "hello"},
        "at": {"atMobiles": [], "atUserIds": [], "isAtAll": True},
    }


def test_msg_link_helper():
    data = msg_link("标题", "内容", "https://example.com")
    assert data["msgtype"] == "link"
    assert data["link"]["messageUrl"] == "https://example.com"


def test_msg_markdown_helper():
    data = msg_markdown("标题", "**加粗**")
    assert data["msgtype"] == "markdown"


def test_msg_action_card_helper():
    data = msg_action_card("标题", "内容", "按钮", "https://example.com")
    assert data["msgtype"] == "actionCard"
    assert data["actionCard"]["singleTitle"] == "按钮"


def test_msg_action_cards_helper():
    data = msg_action_cards("标题", "内容", ["A", "B"], ["https://a", "https://b"])
    assert len(data["actionCard"]["btns"]) == 2


def test_msg_feed_card_helper():
    data = msg_feed_card(["A"], ["https://a"], ["https://pic"])
    assert data["msgtype"] == "feedCard"
    assert data["feedCard"]["links"][0]["title"] == "A"


def test_text_message_requires_content():
    with pytest.raises(ValueError):
        DingTalkTextMessage("")


def test_link_message_build():
    msg = DingTalkLinkMessage("标题", "内容", "https://example.com", pic_url="https://pic")
    built = msg.build()
    assert built["link"]["picUrl"] == "https://pic"


def test_markdown_message_build():
    msg = DingTalkMarkdownMessage("标题", "内容")
    assert msg.build()["msgtype"] == "markdown"


def test_action_card_requires_button_config():
    with pytest.raises(ValueError):
        DingTalkActionCardMessage("标题", "内容")


def test_feed_card_requires_full_fields():
    with pytest.raises(ValueError):
        DingTalkFeedCardMessage([{"title": "A"}])


def test_get_sign_returns_timestamp_and_signature():
    timestamp, signature = get_sign("my-secret")
    assert timestamp.isdigit()
    assert isinstance(signature, str) and signature


def test_dingtalk_access_model():
    access = DingTalkAccess(access_token="tok", secret="sec")
    assert access.access_token == "tok"
    assert access.secret == "sec"


def test_client_login_requires_token_and_secret():
    client = DingTalkClient()
    with pytest.raises(ValueError):
        client.login(access_token="tok")  # 缺 secret
    with pytest.raises(ValueError):
        client.login(secret="sec")  # 缺 access_token


def test_client_login_with_access_object():
    client = DingTalkClient()
    client.login(access=DingTalkAccess(access_token="tok", secret="sec"))
    assert client.access_token == "tok"
    assert client.secret == "sec"


def test_client_send_requires_login():
    client = DingTalkClient()
    with pytest.raises(ValueError):
        client.send(DingTalkTextMessage("hi"))


@patch("funpush.dingtalk.client.requests.post")
def test_client_send_text_success_mocked(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {"errcode": 0}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    client = DingTalkClient(send_delay=0)
    client.login(access_token="tok", secret="sec")

    assert client.send_text("测试消息") is True
    assert mock_post.called


@patch("funpush.dingtalk.client.requests.post")
def test_client_send_dedup_mocked(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {"errcode": 0}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    client = DingTalkClient(send_delay=0)
    client.login(access_token="tok", secret="sec")

    message = DingTalkTextMessage("重复消息")
    assert client.send(message) is True
    # 相同内容第二次发送应被去重拦截，不再调用底层 API
    assert client.send(message) is False
    assert mock_post.call_count == 1


def test_wechat_module_is_empty_stub():
    # wechat/__init__.py 目前是空文件，尚未实现，这里只确认能正常导入（不算真正功能）
    import funpush.wechat  # noqa: F401
