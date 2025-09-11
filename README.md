# FunPush

[![PyPI version](https://badge.fury.io/py/funpush.svg)](https://badge.fury.io/py/funpush)
[![Python](https://img.shields.io/pypi/pyversions/funpush.svg)](https://pypi.org/project/funpush/)
[![License](https://img.shields.io/github/license/farfarfun/funpush.svg)](https://github.com/farfarfun/funpush/blob/main/LICENSE)

**一个简单易用的Python消息推送库，支持钉钉、微信等多平台机器人消息发送。**

FunPush 是一个专为各种即时通讯平台设计的消息推送库。目前主要支持钉钉机器人消息推送，未来将扩展支持更多平台。

**关键词：** `消息推送` `钉钉机器人` `Python` `即时通讯` `API` `Webhook` `自动化` `通知` `机器人` `消息发送`

## ✨ 特性

- 🤖 **钉钉机器人支持**：完整支持钉钉机器人的所有消息类型
- 🔒 **类型安全**：完整的类型提示支持，提供更好的开发体验
- 🚀 **消息去重**：内置消息去重机制，防止重复发送
- ⚡ **速率限制**：可配置的发送延迟，避免触发平台限制
- 📝 **丰富的消息类型**：支持文本、链接、Markdown、ActionCard、FeedCard等多种消息格式
- 🛡️ **错误处理**：完善的异常处理和日志记录
- 📚 **详细文档**：完整的中文文档和示例

## 📦 安装

使用 pip 安装：

```bash
pip install funpush
```

## 🚀 快速开始

### 钉钉机器人配置

1. 在钉钉群中添加自定义机器人
2. 获取 Webhook URL 和密钥（如果启用了加签验证）
3. 使用以下代码发送消息：

```python
from funpush import DingTalkClient

# 初始化客户端
client = DingTalkClient()

# 配置钉钉机器人访问信息
access = {
    "access_token": "your_access_token_here",
    "secret": "your_secret_here"  # 可选，如果启用了加签验证
}

# 发送文本消息
client.send_text(
    access=access,
    content="Hello, World! 这是一条测试消息。",
    at_all=False
)
```

## 📖 详细使用说明

### 1. 文本消息

```python
# 发送普通文本消息
client.send_text(
    access=access,
    content="这是一条普通的文本消息"
)

# 发送带@功能的文本消息
client.send_text(
    access=access,
    content="重要通知：请相关人员注意！",
    mobiles=["13800138000"],  # @指定手机号
    user_ids=["user123"],     # @指定用户ID
    at_all=False              # 是否@所有人
)
```

### 2. 链接消息

```python
client.send_link(
    access=access,
    title="重要公告",
    text="点击查看详细内容",
    message_url="https://example.com/announcement",
    pic_url="https://example.com/image.jpg"
)
```

### 3. Markdown 消息

```python
markdown_text = """
# 项目进度报告
## 本周完成
- ✅ 功能A开发完成
- ✅ 单元测试通过
- ✅ 代码审查完成

## 下周计划
- 📋 功能B开发
- 🧪 集成测试
- 🚀 准备发布

**负责人：** @张三
"""

client.send_markdown(
    access=access,
    title="项目进度报告",
    text=markdown_text,
    mobiles=["13800138000"]
)
```

### 4. ActionCard 消息

#### 单按钮 ActionCard

```python
client.send_action_card(
    access=access,
    title="系统升级通知",
    text="系统将于今晚22:00-24:00进行升级维护，请提前做好准备。",
    single_title="查看详情",
    single_url="https://example.com/upgrade-notice"
)
```

#### 多按钮 ActionCard

```python
buttons = [
    {"title": "同意", "actionURL": "https://example.com/approve"},
    {"title": "拒绝", "actionURL": "https://example.com/reject"},
    {"title": "查看详情", "actionURL": "https://example.com/details"}
]

client.send_action_cards(
    access=access,
    title="请假申请审批",
    text="张三申请请假3天，请审批。",
    buttons=buttons
)
```

### 5. FeedCard 消息

```python
# 方式一：使用字典列表
links = [
    {
        "title": "新闻1：技术突破",
        "messageURL": "https://example.com/news1",
        "picURL": "https://example.com/pic1.jpg"
    },
    {
        "title": "新闻2：市场动态", 
        "messageURL": "https://example.com/news2",
        "picURL": "https://example.com/pic2.jpg"
    }
]

client.send_feed_card(access=access, links=links)

# 方式二：使用简化方法
titles = ["新闻1：技术突破", "新闻2：市场动态"]
urls = ["https://example.com/news1", "https://example.com/news2"]
pics = ["https://example.com/pic1.jpg", "https://example.com/pic2.jpg"]

client.send_feed_card_simple(
    access=access,
    titles=titles,
    urls=urls,
    pics=pics
)
```

## ⚙️ 高级配置

### 客户端配置

```python
# 自定义配置
client = DingTalkClient(
    max_cache_size=200,    # 消息去重缓存大小
    send_delay=5.0         # 发送延迟（秒）
)
```

### 错误处理

```python
try:
    success = client.send_text(
        access=access,
        content="测试消息"
    )
    if success:
        print("消息发送成功")
    else:
        print("消息发送失败")
except Exception as e:
    print(f"发送过程中出现错误: {e}")
```

## 🔧 开发指南

### 项目结构

```
funpush/
├── src/
│   └── funpush/
│       ├── __init__.py
│       ├── base/           # 基础类和接口
│       ├── dingtalk/       # 钉钉相关实现
│       │   ├── client.py   # 钉钉客户端
│       │   ├── message.py  # 消息类型定义
│       │   └── util.py     # 工具函数
│       └── wechat/         # 微信相关（开发中）
├── pyproject.toml
└── README.md
```

### 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📋 TODO

- [ ] 微信企业号机器人支持
- [ ] 飞书机器人支持
- [ ] 邮件推送支持
- [ ] 短信推送支持
- [ ] 消息模板功能
- [ ] 异步发送支持

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 👥 作者

- **牛哥** - *项目维护者* - [niuliangtao@qq.com](mailto:niuliangtao@qq.com)
- **farfarfun** - *项目维护者* - [farfarfun@qq.com](mailto:farfarfun@qq.com)

## 🔗 相关链接

- [项目主页](https://github.com/farfarfun/funpush)
- [发布页面](https://github.com/farfarfun/funpush/releases)
- [问题反馈](https://github.com/farfarfun/funpush/issues)
- [PyPI 页面](https://pypi.org/project/funpush/)

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者！

---

如果这个项目对你有帮助，请给我们一个 ⭐️！