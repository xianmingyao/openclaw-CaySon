# jingmai-product-publish

京麦商品发布自动化技能，面向 Windows 环境下的京麦客户端商品发布、草稿保存、批量导入、商品抓取与任务跟踪。

## 触发词

- 京麦发布
- jingmai publish
- jingmai plan
- jingmai execute
- 京麦自动化
- 批量上架
- 商品采集

## 环境要求

- Windows 10/11
- 已安装并登录京麦客户端
- 建议分辨率 `2560x1392`
- 建议使用 `uv` 管理依赖；若本机没有 `uv`，可直接用 `python`

安装依赖：

```bash
cd E:\workspace\skills\jingmai-product-publish
uv pip install -r requirements.txt
uv run python cli.py --help
```

## 常用命令

环境检查：

```bash
uv run python cli.py status
python cli.py status
```

发布单个商品：

```bash
uv run python cli.py publish --config product.json
uv run python cli.py publish --data "{\"title\":\"测试商品\",\"price\":29.9}"
uv run python cli.py publish --config product.json --plan-out data\last-plan.json
```

只生成计划，不执行：

```bash
uv run python cli.py plan "发布一个手机壳商品" --config product.json
uv run python cli.py plan --config product.json
uv run python cli.py plan --config product.json --steps-only
```

执行已有计划：

```bash
uv run python cli.py execute --config plan.json
uv run python cli.py execute --config plan.json --task-id abc123
uv run python cli.py execute --config plan.json --from-start
```

批量发布：

```bash
uv run python cli.py batch --file products.xlsx
uv run python cli.py batch --file products.json
uv run python cli.py batch --dir .\products
```

商品抓取：

```bash
uv run python cli.py scrape https://item.jd.com/12345678.html
uv run python cli.py scrape --url https://item.jd.com/12345678.html --output product.json
uv run python cli.py scrape https://item.jd.com/12345678.html --no-save
```

任务与商品：

```bash
uv run python cli.py tasks
uv run python cli.py tasks --status running --limit 10
uv run python cli.py products --list
uv run python cli.py products --file product.json
uv run python cli.py status <task_id>
```

记忆与数据库：

```bash
uv run python cli.py memory stats
uv run python cli.py memory search --query "类目选择" --top 5
uv run python cli.py memory cleanup
uv run python cli.py init-db
```

## CLI 说明

- `publish` 是主入口：先生成计划，再立刻执行。
- `plan` 只负责生成计划，不会点击京麦。
- `execute` 只执行已有计划，适合恢复执行、调试、外部调度。
- `batch` 逐条复用 `publish` 的完整闭环，不走旧的“只规划后粗执行”路径。

`plan` 默认输出完整计划包：

```json
{
  "task_id": "abc12345",
  "product_data": {},
  "plan": [],
  "total_steps": 0
}
```

## 当前关键行为

### 1. ActionRegistry 参数约定

- `ActionRegistry.execute()` 使用 `action_name` 作为动作名参数。
- 这避免了与业务动作里的 `name=` 参数冲突。
- `click_element(name="编辑")` 这类动作现在可以正常通过注册器调用。

### 2. 执行成功判定

- 动作执行失败是硬失败前提。
- 视觉校验只能补强成功，不能把动作失败覆盖成成功。
- 如果 `action_result.success = false`，该步骤不会再被记为成功。

### 3. fill_product_info 语义

- `fill_product_info` 不再无条件返回成功。
- 文本字段写入后会做确定性的回读校验。
- 只有目标字段写入成功且回读一致时，字段才算成功。
- 返回值里会带：
  - `filled`
  - `total`
  - `details`
  - `failed_fields`
  - `message`

### 4. 截图链路

- 截图保存为真实 PNG，而不是扩展名为 `.png` 的 BMP 数据。
- `execute` 路径默认保存适合视觉校验的小图。
- 如需保留全尺寸调试图，可设置：

```bash
set JINGMAI_DEBUG_SCREENSHOTS=1
```

- 调试模式下会额外落盘 `*_full.png`。

### 5. 短期记忆元数据

执行器写入短期记忆时，除了步骤摘要，还会附带这些字段：

- `step`
- `action`
- `action_result_success`
- `vision_status`
- `retry_count`
- `error`
- `screenshot`

这样可以避免“只记结论、不记证据”的记忆污染。

### 6. 日志编码

- 日志文件使用 `utf-8-sig`
- 标准输出和标准错误会主动重配为 UTF-8
- `warning()` 有显式别名，不再静默降级成 `info`

### 7. 调试脚本

- `smart_executor.py` 已移除硬编码 `hwnd`
- `check_rect.py` / `check_state.py` 也改为动态找窗

## 执行模型

### Plan-and-Solve

- `publish` / `plan` 先生成结构化执行计划。

### ReAct

每一步按以下顺序执行：

1. `Act`
2. `Screenshot`
3. `Observe`
4. `Reflect`

### Reflection

失败时采用递进式重试，最多 3 次：

1. 直接重试
2. 随机等待 2-4 秒后重试
3. 强制重定位窗口后重试

## 视觉校验降级策略

1. LLM 可用：截图 + 多模态分析
2. LLM 不可用：回退到动作结果
3. 截图失败：记录未验证，但不会把动作失败改成成功

注意：

- 当前版本中，动作失败不会再被视觉结果覆盖。
- `window_diff.risk_level=high` 且视觉无法确认时，会优先按失败处理。

## 计划文件与恢复执行

- `publish --plan-out xxx.json` 会落盘完整计划包。
- `execute --config xxx.json` 可直接恢复执行。
- `execute` 默认从计划文件里第一个非 `success` 步骤继续。
- 如需全量重跑，使用 `--from-start`。

计划文件会在执行中实时更新：

- 每步状态
- 重试次数
- 顶层 `status`
- 风险统计
- 恢复错误信息

## 商品 JSON 示例

```json
{
  "product": {
    "title": "iPhone 15 硅胶手机壳",
    "price": 29.9,
    "category": "手机壳",
    "category_path": "手机/手机配件/手机壳",
    "sku": "CASE-IP15-001",
    "stock": 100,
    "attributes": {
      "材质": "硅胶"
    }
  },
  "images": [
    "D:/images/case1.jpg",
    "D:/images/case2.jpg"
  ]
}
```

## 故障排查

- `status` 中如果 LLM 不可用，先确认本地或远端模型服务是否已启动。
- 如果 `plan` 成功但任务停留在 `planning/pending`，说明只完成了规划，还没执行。
- 如果 `execute` 成功但没有任务状态，通常是传入了旧版 steps-only 计划且没有 `task_id`。
- 如果视觉链路产物过多，先确认是否开启了 `JINGMAI_DEBUG_SCREENSHOTS=1`。
- 如果怀疑动作被误判，优先查看计划文件中的步骤状态和短期记忆元数据，而不是只看一句摘要。
