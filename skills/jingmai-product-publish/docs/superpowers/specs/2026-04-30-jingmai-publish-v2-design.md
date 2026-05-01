# 京麦商品发布自动化 v2 设计说明

> 日期：2026-04-30  
> 状态：已实现，已按 2026-05-01 修订  
> 范围：`jingmai-product-publish`

## 1. 目标

把原先分散的京麦自动化脚本收拢成可维护的产品化能力：

- 统一 CLI
- 统一 action 注册与执行
- 统一计划生成、执行、验证、重试
- 统一日志、截图、记忆、任务状态

这份文档描述的是当前实现，而不是最初设想。

## 2. 当前架构

核心分层：

- `cli.py`
  - `publish` / `plan` / `execute` / `batch` / `scrape` / `memory` / `status`
- `agents/`
  - `planner.py` 负责计划生成
  - `executor.py` 负责 ReAct 执行
  - `thinker.py` 负责视觉/推理型补充能力
- `actions/`
  - 参数化 action 集合
  - 通过 `ActionRegistry` 统一注册和调用
- `infrastructure/`
  - `locator.py` 负责窗口定位、点击、截图
  - `logger.py` 负责日志
  - `monitor.py` 负责重试与熔断
- `memory/`
  - working / short-term / long-term
- `llm/`
  - Ollama / vLLM / router / manager
- `db.py` + `models.py`
  - 任务、步骤、商品信息持久化

## 3. CLI 语义

### `publish`

完整闭环：

1. 生成计划
2. 执行计划
3. 实时更新计划文件、任务状态、步骤状态

### `plan`

- 只生成计划
- 默认输出完整计划包
- `--steps-only` 兼容旧脚本

### `execute`

- 只执行已有计划
- 默认从第一个非 `success` 步骤恢复
- `--from-start` 强制从头执行

### `batch`

- 对每个商品复用 `publish` 的完整闭环
- 不再走“只规划后粗执行”的旧路径

## 4. ActionRegistry 约定

当前设计要求：

- action 注册器用 `action_name` 表示注册动作名
- 业务 action 自身可以继续使用 `name`、`text`、`page` 之类参数

原因：

- 避免 `ActionRegistry.execute(name, **kwargs)` 与 `click_element(name="编辑")` 发生参数冲突

当前实现：

```python
ActionRegistry.execute(action_name="click_element", name="编辑", locator=...)
```

这项修订已经落地，是本次事故修复的关键点之一。

## 5. 执行模型

执行器采用 ReAct 风格：

1. `Act`
2. `Screenshot`
3. `Observe`
4. `Reflect`

每个步骤支持最多 3 次递进式重试：

1. 直接重试
2. 随机等待 2-4 秒
3. 强制重定位窗口后重试

### 成功判定的硬规则

当前版本明确采用下面的判定顺序：

- `action_result.success == false`
  - 本步骤一定失败
  - 视觉结果不能覆盖动作失败
- `action_result.success == true`
  - 再由视觉结果补强
  - 视觉失败可触发重试
  - 视觉未知时可回退到动作结果

这条规则用于修复此前“动作异常却被视觉判成成功”的问题。

## 6. 视觉验证策略

### 校验优先级

1. 有 LLM + 有截图：多模态分析
2. 无 LLM 或无截图：回退到动作结果
3. 高风险窗口漂移：优先按失败处理

### 高风险窗口漂移

执行器会记录：

- `window_before`
- `window_after`
- `window_diff`

当检测到窗口句柄、标题或上下文异常漂移时：

- `window_diff.risk_level = high`
- 视觉提示词会优先检查“是否跑错窗口/页面”
- 视觉结果若仍是 `unknown`，执行器按失败处理

## 7. 截图链路

### 当前设计

- 截图输出为真实 PNG
- 执行链默认保存适合视觉校验的小图
- 可选保留全尺寸调试图

### 修订原因

旧实现把 `SaveBitmapFile()` 的位图数据直接写进 `.png` 文件名，导致：

- 文件体积固定偏大
- 产物与扩展名不一致
- I/O 成本高
- 下游处理不稳定

### 当前策略

- `locator.take_screenshot(..., for_vision=True)` 输出小图 PNG
- 设置 `JINGMAI_DEBUG_SCREENSHOTS=1` 时，额外保存 `*_full.png`

## 8. 表单写入语义

`fill_product_info` 当前要求：

- 至少存在可填字段
- 所有目标字段都写入成功，才返回 `success=true`
- 任一字段失败时：
  - `success=false`
  - 返回 `failed_fields`
  - 保留 `filled` / `total` 统计

这修复了之前“部分字段失败仍整体成功”的问题。

## 9. 记忆设计

### 三层记忆

- Working：进程内上下文
- Short-term：JSON 文件
- Long-term：Milvus

### 短期记忆写入约定

执行器在每个步骤结束后写入短期记忆，除了摘要文本，还必须带这些元数据：

- `step`
- `action`
- `action_result_success`
- `vision_status`
- `retry_count`
- `error`
- `screenshot`

目的：

- 防止只写“成功/失败”这种无证据结论
- 防止错误结果污染后续 recall

## 10. 日志设计

当前日志要求：

- 文件编码：`utf-8-sig`
- 标准输出：主动重配 UTF-8
- 提供 `warning()` 别名，避免 warning 被降级到 info

日志必须能明确看出：

- 当前步骤
- 动作参数
- 重试次数
- 视觉状态
- 恢复错误
- 高风险窗口漂移

## 11. smart_executor 的定位

`smart_executor.py` 当前视为实验/辅助实现，不是主执行链。

设计约束：

- 不能硬编码窗口句柄
- 只能通过正常窗口发现流程初始化 locator

因此已移除 `hwnd=1377392` 这种写法。

## 12. 数据与计划文件

计划文件承载：

- `task_id`
- `product_data`
- `plan`
- `total_steps`
- 顶层 `status`
- `current_step`
- `risk_stats`
- `recovery_error`

每个步骤可包含：

- `status`
- `retries`
- 运行结果

设计目标是让 `execute`、外部调度和排障都基于同一份事实来源。

## 13. 测试要求

当前必须覆盖的回归测试：

- action 注册器允许业务参数名为 `name`
- 动作失败时不能被视觉成功覆盖
- `fill_product_info` 的失败传播
- 截图输出是真实 PNG
- 失败步骤会写入带证据字段的短期记忆

## 14. 依赖

关键依赖：

- `click`
- `sqlalchemy`
- `pymysql`
- `pywinauto`
- `pywin32`
- `pyautogui`
- `pyperclip`
- `requests`
- `ollama`
- `pymilvus`
- `websocket-client`
- `vllm`
- `Pillow`

## 15. 当前验收标准

- `publish` / `plan` / `execute` / `batch` CLI 正常
- ActionRegistry 不再与业务参数冲突
- 执行器不会把动作失败写成成功
- `fill_product_info` 失败语义正确
- 截图产物是真实 PNG
- 短期记忆带证据元数据
- 日志链 UTF-8 可读
- 全量测试通过

截至本次修订，上述要求已在代码和回归测试中落地。  
