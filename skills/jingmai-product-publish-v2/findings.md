# Findings & Decisions

## 2026-05-16 BL-089A Real E2E Findings

- `run-draft-e2e` has a confirmed real Jingmai draft-box pass: `success=true`, `job_id=job-d217feeee80a`, `task_id=task-d7b392c81a07`.
- Final screenshot: `resources/screenshots/window-1187102-20260516-110738-242774.png`.
- The latest draft list row contains the target Excel/JD product title and edit time `2026-05-16 11:07:36`.
- T3 needed two real-world recovery paths:
  - draft list recovery via top-right `发布商品`;
  - category page recovery via recent category shortcut because the category text is rendered inside a WebView Document, not independent UIA controls.
- T6 needed delayed picker confirmation recovery: after Windows file upload succeeds, Jingmai image library can show the uploaded file before the SKU slot is updated, so the workflow must retry picker select/confirm and re-poll the slot.
- Draft save can succeed with incomplete publish-required fields. For draft E2E, T4/T5/transparent-image are best-effort; formal publish must keep strict validation and remains unexecuted without explicit user authorization.
- Current score gate: Gate A (`70/100`) can be considered passed for draft-mode E2E evidence. Remaining gaps for higher scores are formal publish authorization/evidence, screenshot evidence package, runtime event loop/provider manifest, visual reflection, and production persistence/ops.

## Requirements

- 使用 `planning-with-files` 生成项目补完计划清单。
- 使用 gstack/GSD 风格的 `.planning` 文件管理项目开发与完善。
- 基于用户提供的 `55/100` 评分分析，修正旧文档中 `92/100`、`95/100` 的虚高状态。
- 优先处理 P0 阻塞项：主图上传、透明图上传、详情编辑器、保存草稿/发布提交、Reflection 截图校验、Agent 决策层。

## Research Findings

- 现有 `.planning/STATE.md` 写着 `95/100`、`13/14` 完成，但用户评分分析指出真实基线应为 `55/100`。
- graphify 报告显示核心节点集中在 `WindowInfo`、`RuntimeLogRepository`、`JingmaiWorkflowService`、`RealWindowsUIAAdapter`、`WindowManager`、`TaskRunner`，说明后续改造应优先围绕这些模块收敛。
- 旧 `.planning/ROADMAP.md` 把 `GT-009 ~ GT-012` 标为完成，但用户评估指出 T6/T8 多数仍是代码路径或探针，不具备真实页面闭环证据。
- 现有 Reflection 主要是失败签名、重试计数和截图留存，还没有达到视觉模型校验和截图前后差异判断。
- Provider 抽象已有骨架，但距离 SightFlow 风格的 manifest/provider bundle 能力解耦还有明显距离。
- `BL-088-1` 调用链集中在 `JingmaiWorkflowService.run_t6_upload_main_image()` -> `_run_t6_upload_slot()` -> `_complete_local_upload()` -> `RealWindowsUIAAdapter.select_uploaded_image_and_confirm()`。
- 旧实现上传后只立即读取一次槽位，京麦页面异步刷新时容易误判为 `槽位状态变化=失败`。
- 图片空间里新上传图片不一定暴露文件名文本；只按 `file_name/file_stem` 点击会漏掉只有缩略图的情况。
- `RealWindowsUIAAdapter._merge_image_upload_slot_snapshot()` 原先遇到同槽位 `empty + filled` 冲突时总是保留 `empty`，这会把真实上传后的大缩略图误压回空槽。

## Technical Decisions

| Decision | Rationale |
|----------|-----------|
| 重置项目评分基线为 `55/100` | 避免继续基于虚高完成度安排开发 |
| 将 P0 聚焦为“真实产出一次上架” | 业务系统必须先能完成最终动作 |
| 将 Agent 决策层列为架构 P0/P1 交界项 | 没有 observe/decide/act/verify/repeat，UI-TARS 对齐不成立 |
| Reflection 第一阶段先做截图差异和控件状态校验 | 这是接 Ollama 视觉模型前的最小可信验证层 |
| 多 Agent 后置到持久化和视觉校验之后 | 先明确单 Agent 主循环和状态模型，再拆角色更稳 |
| `BL-088-1` 先补异步刷新和缩略图选择回退 | 这两个点直接解释“文件桥接成功但槽位状态变化失败”的高概率路径 |

## Issues Encountered

| Issue | Resolution |
|-------|------------|
| 旧项目管理文件口径过于乐观 | 用本次评分分析重建 backlog、roadmap 和 state |
| `planning-with-files` 技能文件存在，但未在当前可用技能清单中显式列出 | 已按本地 `SKILL.md` 手动使用 |
| gstack 技能本体偏浏览器 QA，项目中已有 `.planning` 作为 GSD/gstack 管理承载 | 保留 `.planning` 为项目管理事实源，必要时后续用 gstack 做 Web/可视化验证 |
| 本机没有 `rg` 命令 | 已降级使用 PowerShell `Select-String` 和 graphify 查询 |
| gstack browse 二进制存在但 `status` 启动失败 | `browse.exe status` 报错 `Cannot find server.ts. Set BROWSE_SERVER_SCRIPT env or run from the browse source tree.`；本轮不依赖浏览器 QA，后续需要修复 gstack 安装后再用于截图证据索引或 Web 控制台验证 |
| `BL-089A` 草稿 E2E 需要本地图片路径 | 当前导入准备链路尚未自动把 JD 图片下载成本地文件；`run-draft-e2e` 先要求显式传入 `--main-image-path` 和 `--transparent-image-path`，自动图片本地化并入后续数据准备质量补齐 |
| `BL-089A` 真实首跑被数据库初始化阻塞 | 配置库缺少 `upload_jobs` 表；CLI 已改为结构化 `database_error`，远端建表需用户确认后执行 `python cli.py init-db --root .` |
| 旧版 `publish_tasks` 表与当前 ORM 不兼容 | `create_all()` 不迁移已有表；已在 `init_database()` 增加 MySQL 旧表补列迁移 |
| T4 固定动态 ID 在当前类目会串字段 | `jd-id-*` 前缀/后缀随类目变化，固定 ID 把类型/品牌写进价格字段；已改为标签优先定位 |
| 当前类目无 SKU 表格字段 | `t5-first-row` 固定 SKU 行 ID 找不到候选；草稿 E2E 已移除 SKU/T5 必经步骤，T5 保留为独立验收项 |
| 当前类目主图上传失败 | `t6-main-image` 触发模式为 `text_fallback`，文件写入失败；需要补当前页面上传入口/文件对话框处理 |

## 100 分规划发现

- “平稳 100 分”必须拆成证据门禁，而不是直接把文档状态改成 100。
- 当前最短提分路径不是继续加外围能力，而是先做 `Phase A: 55 -> 70`，即把已突破的 T6/T8/T5/T7 能力串成 Excel 单行到京麦草稿箱的 E2E 证据包。
- SightFlow 一比一复刻缺口主要集中在四处：runtime event queue、provider manifest/bundle、VLM 视觉坐标、结构化事件输出。
- UI-TARS 对齐缺口主要集中在三处：Agent/Operator/Loop 分层不彻底、固定 `observe -> decide -> act -> verify -> repeat` 尚未进入主流程、截图/状态观察不是所有动作的一等公民。
- 生产化缺口集中在 Redis 锁/事件流、Milvus 失败记忆、日志截图清理、飞书实时入口、端到端 UAT。
- 新增规划文件：`100_SCORE_RECOVERY_PLAN.md`。
- `BL-089A` 的代码入口已完成并通过测试，但不能标记为 DONE；真实首轮已进入桌面并完成 T3/T4，当前阻塞在 T6 主图上传与 T8 草稿确认。

## Resources

- `IMPLEMENTATION_PLAN.md`
- `IMPLEMENTATION_PROGRESS.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/BACKLOG.md`
- `.planning/STATE.md`
- `graphify-out/GRAPH_REPORT.md`
- `jingmai_publish/services/task_runner.py`
- `jingmai_publish/runtime/kernel.py`
- `jingmai_publish/runtime/providers.py`
- `jingmai_publish/desktop/uia_adapter.py`

## Visual/Browser Findings

- 本阶段尚未打开京麦桌面执行实机验证。
- 下一阶段进入 P0 闭环时，必须把每次上传、详情写入、保存草稿/发布的 before/after 截图和页面状态写入 `progress.md`。
- 当前尚未执行真实京麦桌面上传；本轮只完成代码层修复和自动化测试。
- 真实执行 `t6-main-image` 已通过：`page_state=main_image_uploaded`，页面文档出现“已成功回填至SKU主图，并保存至图片空间”。
- 成功证据截图：`resources/screenshots/window-1187102-20260515-235148-851391.png`。
- 真实执行 `t6-transparent-image` 已通过：`page_state=transparent_image_uploaded`，透图槽位已经出现图片，命令入口可识别已填充并幂等成功。
- 成功证据截图：`resources/screenshots/window-1187102-20260516-002306-522579.png`。
- 用户截图指出图片预览遮罩需要点击右上角叉号取消；已沉淀为 `close_image_preview_overlay()`，上传前自动尝试关闭。

## BL-088-3 Detail Editor Findings

- `t6-detail-editor` originally failed because generic focused-control typing did not focus the WebView rich-text editor reliably.
- Direct coordinate probing proved the editable body accepts clipboard paste after clicking the left side of the code-editor body.
- The workflow now prefers the `代码编辑` anchor, clicks the editor body, pastes via clipboard, and verifies the inserted probe from document text.
- Real validation passed with `page_state=detail_content_written`; evidence screenshot: `resources/screenshots/window-1187102-20260516-005034-202135.png`.
- 用户截图指出 Windows 文件对话框大图标模式会把 `transparent-probe.png` 显示成换行文本；文件项匹配已改为去空白/换行后比较，再点击文件项并提交。
