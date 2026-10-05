# 更新日志

## [未发布]

### 修复

- 仓库/pyproject description 与 README 统一为当前已实现的钉钉机器人能力，不再暗示已支持微信（farfarfun/todo-list#873）。
- README 许可证徽章链接修正为默认分支 `master`（原指向不存在的 `main` 分支）。
- README 底部「关于 farfarfun」区块补齐 🏠/📦/📧 emoji，与 SPEC.md 固定文本一致。
- README 贡献指南的提交示例改为中文 `<类型>: <做了什么>` 格式。

## [1.0.6]

### 新增

- 增加环境变量方式配置钉钉机器人凭据。

### 修复

- 修正 README 中的发送示例和异常处理行为。

### 变更

- 使用 `farlog` 统一日志记录，并补充 Python 3.10 类型标注。

### 废弃

- 无。
