# jm_ufo_agent v2 本轮开发计划

## Goal
把当前 48/100 的实现中“本地可验证、不会触碰真实京麦账号或真实窗口”的缺陷先补齐一轮，提升到可继续接真实 UFO backend 的状态。

## Scope
- 补齐 MySQL 12 表 DDL 和对应的轻量 Repository 边界。
- 把 12 个核心字段接入字段规划、完成度评分和字段级恢复。
- 把行级恢复、row82 规则、提交行状态接入 dry-run workflow。
- 给 CLI 增加 `run --task-id xxx` 形态，同时保持默认 dry-run 安全行为。
- 给 MiniMax workflow 增加可注入真实 client 的策略边界，测试只用 fake transport。
- 增加 SafetyPolicy CI 级静态检查脚本和测试。

## Out Of Scope
- 不连接真实京麦账号。
- 不点击真实桌面窗口。
- 不复制或执行 `E:\PY\UFO\ufo` 的真实 UIA/Win32 backend。
- 不调用真实 MiniMax 网络 API。
- 不抓取真实京东页面或下载真实图片。

## Phases
1. [complete] 读取规则、设计文档、图谱和现有代码。
2. [complete] 创建计划文件，并补充发现记录。
3. [complete] 实现 schema/repository/row recovery/field recovery。
4. [complete] 实现 CLI run、MiniMax 可注入策略、安全检查脚本。
5. [complete] 添加和修复测试。
6. [complete] 运行 pytest、静态安全检查、graphify update。
7. [complete] 更新 memory 和进度记录。

## Acceptance
- `python -m pytest` 通过。
- 安全检查脚本能发现未保护的 `click/fill/submit`。
- dry-run 在 12 字段齐全时保存草稿。
- 已 verified 字段从恢复仓库注入后不会重复填。
- row5-row7 已提交且有草稿证据时，下一行自动判定为 row82。
- `python -m jm_ufo_agent run --task-id xxx --row-index 82 --product-json @file` 可用。

## Errors Encountered
| Error | Attempt | Resolution |
|---|---|---|
| `writing-plans` skill 不在当前技能列表 | 1 | 使用最接近的 `planning-with-files` 按文件计划落地 |
| `rg` 不存在 | 1 | 改用 PowerShell `Select-String` / `Get-ChildItem` |
| `uv run python -m pytest` 缺少 pytest | 1 | 使用项目声明的 `uv run --extra test python -m pytest` 通过 |

## Next Gap-Closure Plan

### Goal
把当前 62/100 的本地 dry-run 实现推进到真实京麦保存草稿可小批量验证。

### Phases
1. [pending] LangGraph StateGraph 正式化：18 个节点文件、`build_state_graph()`、checkpointer 路由测试。
2. [pending] Repository 补全：product_assets、step_logs、locator_cache、draft_verifications、vlm_calls、graph checkpoint/pending writes。
3. [pending] UFO/UIA/Win32 backend 适配：窗口枚举、截图、焦点、UIA 树摘要、`UfoDesktopBackend`。
4. [pending] WebView fallback 闭环：真实截图、OCR、坐标、剪贴板、读回、局部截图相似度。
5. [pending] 真实保存草稿链路：保存按钮白名单、跳转/草稿 ID/toast 验证、draft_verifications 落库。
6. [pending] 京东抓取与图片处理：价格/标题/图片、主副图下载、VLM 转换、失败 3 次 halt。
7. [pending] MiniMax 生产评审闭环：真实 transport、preflight、指数退避、review details 落库。
8. [pending] Rich dashboard：只读进度、当前 row/field/node、失败证据展示。
9. [pending] halt 证据标准化：截图、OCR、page signature、window summary、step log。
10. [pending] 分阶段生产验证：mock E2E -> 只观察 -> 单 row -> 10 row -> 全量前 review。

### Plan Doc
- `docs/superpowers/plans/2026-06-09-jm-ufo-agent-v2-gap-closure-plan.md`
