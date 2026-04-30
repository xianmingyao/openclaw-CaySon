# jingmai

京麦商品发布自动化技能。适用于 Windows 上的京麦客户端商品发布、草稿保存、批量导入、商品抓取与任务状态追踪。

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
- 使用 `uv` 管理依赖

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
```

发布单个商品：

```bash
uv run python cli.py publish --config product.json
uv run python cli.py publish --data "{\"title\":\"测试商品\",\"price\":29.9}"
```

仅规划，不执行：

```bash
uv run python cli.py plan "发布一个手机壳商品" --config product.json
uv run python cli.py plan --config product.json
uv run python cli.py plan --config product.json --steps-only
```

执行已有计划：

```bash
uv run python cli.py execute --config plan.json
uv run python cli.py execute --config plan.json --task-id abc123
```

批量发布：

```bash
uv run python cli.py batch --file products.xlsx
uv run python cli.py batch --file products.json
uv run python cli.py batch --dir .\products
```

采集商品：

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

`plan` 命令默认输出完整计划包：

```json
{
  "task_id": "abc12345",
  "product_data": {},
  "plan": [],
  "total_steps": 0
}
```

说明：

- 默认应保存完整计划包，后续 `execute` 会自动复用其中的 `task_id`
- 如果需要兼容旧脚本，只输出步骤数组，使用 `--steps-only`
- `execute` 同时兼容完整计划包和旧版步骤数组

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

## 当前行为约束

- `ExecutorAgent` 是规则驱动，不依赖 LLM 做每一步执行
- `ThinkerAgent` 依赖 LLM；如果 LLM 不可用，视觉分析会失败
- 点击链路优先使用窗口消息，减少鼠标拖拽选中文本的问题
- 如果点击失败，关键 action 会直接返回失败，不再“假成功”

## 排障

- `status` 里 `LLM (vLLM): FAIL` 通常是远端服务没启动，不是 CLI 本身故障
- 如果 `plan` 后数据库是 `planning/pending`，说明只是生成了计划，还没执行
- 如果 `execute` 成功但没有任务状态，通常是传入了旧版 steps-only 计划且没有 `task_id`
- 如果京麦界面出现大面积蓝色选中，优先检查类目页或输入框点击是否命中了错误区域
