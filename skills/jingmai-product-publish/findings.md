# jm_ufo_agent v2 本轮发现

## Design / Gap
- 文档验收 F06 要求 12 个核心字段全部 verified；当前 `DeterministicPlanStrategy.default_fields` 只有 6 个。
- 文档验收 F09/F10/F16 要求字段级、行级、row82 恢复；当前只有 `FieldProgressRepository.list_verified_fields()`，workflow 启动时未读取。
- 文档验收 F12 要求 `python -m jm_ufo_agent run --task-id xxx`；当前 CLI 只有 `dry-run`。
- 文档 NF06 要求 CI grep 阻断未调用 `assert_allowed` 的 `click/fill/submit`；当前只有人工扫描。
- 文档要求 12 张 MySQL 表；当前 DDL 只有 `jm_tasks`、`jm_products`、`jm_field_progress`。

## Code
- `DryRunWorkflow` 是当前本地可测 workflow 枢纽，适合先扩展恢复节点和提交节点。
- `GraphState` 已有 `to_dict()`，但缺少 `from_dict()`，恢复 checkpoint 时不方便。
- `MiniMaxReviewClient` 已有 `/models` preflight 和 `score()`，可以通过一个 adapter strategy 接到 workflow，不在测试里触发真实网络。
- `SQLRepository` 已有 `execute/fetchone/fetchall/dumps_json/loads_json`，可以复用实现新增 repository。

## Safety
- 本轮继续保持真实外部系统全部显式不触碰。
- 真实 UFO backend、京麦窗口识别、京东抓取、图片 VLM 转换必须另起小步并要求人工确认环境。

## Result
- 本轮把当前实现从纯 6 字段 dry-run 骨架推进到“12 字段 + 字段恢复 + 行恢复 + row82 规则 + CLI run + CI 安全扫描”的本地可验证状态。
- 仍未实现真实 UFO/UIA/Win32 backend、真实 WebView OCR/截图闭环、真实京东抓取、真实图片 VLM 转换和真实 MiniMax 网络调用。

## Gap Closure Planning
- 缺陷修复应先补状态机和持久化，再碰真实桌面 backend；否则真实 GUI 失败缺少可恢复证据。
- UFO backend 必须作为 `DesktopBackend` adapter 接入，不能把 v1 ReAct 决策流带回来。
- WebView fallback 是真实保存草稿前的关键阻塞项；没有截图/OCR/读回闭环时不能宣称字段真实 verified。
- 京东抓取、图片下载/VLM、MiniMax 真实调用都涉及外部系统，测试默认必须 fake，真实调用必须环境变量显式开启。
- Rich dashboard 应只读 MySQL/Redis，不应成为业务状态修改入口。
