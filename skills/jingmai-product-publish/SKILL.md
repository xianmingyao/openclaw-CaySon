# jingmai-product-publish

京麦商品发布自动化技能，面向 Windows 环境下的京麦客户端商品发布、草稿保存、批量导入、商品抓取、任务跟踪与记忆管理。

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
- 建议优先使用 `uv`；如果本机没有 `uv`，可直接使用 `python`

安装依赖：

```bash
cd E:\workspace\skills\jingmai-product-publish
uv pip install -r requirements.txt
uv run python cli.py --help
```

## CLI 命令

### 环境检查

```bash
uv run python cli.py status
python cli.py status
python cli.py status <task_id>
```

说明：

- 不带 `task_id` 时，检查数据库、Ollama、vLLM、Milvus
- 带 `task_id` 时，输出该任务状态和步骤状态

### 发布商品

```bash
uv run python cli.py publish --config product.json
uv run python cli.py publish --data "{\"title\":\"测试商品\",\"price\":29.9}"
uv run python cli.py publish --config product.json --plan-out data\last-plan.json
```

说明：

- `publish` 是主入口
- 先做 `plan`，再立刻进入 `execute`
- `--plan-out` 会保存完整计划包，便于监控和恢复执行

### 只生成计划

```bash
uv run python cli.py plan "发布一个手机壳商品" --config product.json
uv run python cli.py plan --config product.json
uv run python cli.py plan --config product.json --steps-only
python cli.py plan --config product.json
```

说明：

- 默认输出完整计划包
- `--steps-only` 只输出步骤数组，兼容旧脚本

完整计划包结构：

```json
{
  "task_id": "abc12345",
  "product_data": {},
  "plan": [],
  "total_steps": 0
}
```

### 执行已有计划

```bash
uv run python cli.py execute --config plan.json
uv run python cli.py execute --config plan.json --task-id abc123
uv run python cli.py execute --config plan.json --from-start
python cli.py execute --config plan.json
```

说明：

- 默认行为是断点续跑
- `--from-start` 强制从第 1 步重跑
- 如果计划里所有步骤都已是 `success`，命令会直接退出

### 批量发布

```bash
uv run python cli.py batch --file products.xlsx
uv run python cli.py batch --file products.json
uv run python cli.py batch --dir .\products
uv run python cli.py batch --file products.json --stop-on-error
uv run python cli.py batch --file products.json --plan-out data\plans
```

说明：

- `--file` 支持 `.json`、`.xlsx`、`.xlsm`
- `--dir` 会读取目录下所有 `.json`
- `--stop-on-error` 遇错停止
- `--plan-out` 会为每个商品保存计划包

### 商品抓取

```bash
uv run python cli.py scrape https://item.jd.com/12345678.html
uv run python cli.py scrape --url https://item.jd.com/12345678.html --output product.json
uv run python cli.py scrape https://item.jd.com/12345678.html --no-save
python cli.py scrape --url https://item.jd.com/12345678.html
```

说明：

- 默认会写入 Product 表
- `--no-save` 只抓取，不写库
- `--output` 可保存为本地 JSON

### 思考分析

```bash
uv run python cli.py think --question "当前页面为什么失败"
uv run python cli.py think --screenshot resources\screenshots\shot.png
uv run python cli.py think "当前页面有什么异常"
```

说明：

- 可只传问题、只传截图，或两者一起传

### 动作清单

```bash
uv run python cli.py actions
python cli.py actions
```

说明：

- 列出当前所有已注册 action

### 任务管理

```bash
uv run python cli.py tasks
uv run python cli.py tasks --status running --limit 10
python cli.py tasks --status failed
```

### 商品管理

```bash
uv run python cli.py products --list
uv run python cli.py products --file product.json
python cli.py products --list
```

### 数据库初始化

```bash
uv run python cli.py init-db
uv run python cli.py db init
python cli.py init-db
```

### 记忆管理

```bash
uv run python cli.py memory stats
uv run python cli.py memory search --query "类目选择" --top 5
uv run python cli.py memory cleanup
uv run python cli.py memory create --content "价格字段回读失败" --type short_term --importance 0.8
uv run python cli.py memory clear --confirm
python cli.py memory stats
```

记忆子命令说明：

- `memory stats`: 查看记忆统计
- `memory search`: 搜索记忆
- `memory cleanup`: 清理记忆
- `memory create`: 手工创建记忆
- `memory clear --confirm`: 清空工作记忆

## 当前关键行为

### 1. ActionRegistry 参数约定

- `ActionRegistry.execute()` 使用 `action_name` 作为动作名参数
- 避免与业务动作中的 `name=` 参数冲突

### 2. 执行成功判定

- 动作执行失败是硬失败前提
- 视觉校验只能补强成功，不能把动作失败覆盖成成功

### 3. fill_product_info

- 文本字段写入后会做确定性回读校验
- 价格字段使用数值归一化比较
- 回读顺序：
  1. UIA BuildCache 快路径
  2. 1.5s UIA 硬超时
  3. 同次动作内若 UIA 超时，后续字段直接降级到剪贴板回读
  4. 局部控件过滤优先于整页远处候选

字段结果包含：

- `write_success`
- `verify_success`
- `success`
- `expected`
- `expected_normalized`
- `actual`
- `verification_method`
- `compare_mode`
- `verify_error`
- `verification_failures`

### 4. 截图链路

- 截图保存为真实 PNG
- `take_screenshot()` 已加入 PrintWindow fallback
- 保存路径会经过安全校验

调试大图开关：

```bash
set JINGMAI_DEBUG_SCREENSHOTS=1
```

### 5. 短期记忆元数据

执行器写入短期记忆时会附带：

- `step`
- `action`
- `action_result_success`
- `vision_status`
- `retry_count`
- `error`
- `screenshot`

### 6. 日志编码

- 日志文件使用 `utf-8-sig`
- 标准输出和标准错误会主动重配到 UTF-8
- `warning()` 有显式别名

## 执行模型

参考 DataWhale Hello-Agents 第四章，三种经典范式协同：

```
Plan-and-Solve（plan 命令）
  └─ 生成结构化执行计划 → 写入计划文件
        ↓
ReAct（execute 命令，每步完整循环）
  └─ 对计划中的每一步:
       Act(执行动作) → Screenshot(截图) → Observe(LLM 视觉分析) → Reflect(判断成功/失败)
         ├─ 成功 → 标记步骤完成 → 更新计划文件 → 执行下一步
         └─ 失败 → Reflection 递进重试（最多 3 次）
              ├─ 第 1 次: 直接重试
              ├─ 第 2 次: 等待 2-4s 后重试
              └─ 第 3 次: 强制重定位窗口后重试
              └─ 仍失败 → 中止任务
        ↓
计划文件实时更新（每步完成后持久化状态，支持断点续跑）
```

### 每步验证流程

每执行一个 action 后：

1. **Act**: 调用 ActionRegistry 执行动作
2. **Screenshot**: win32gui 截图 → PIL resize 1120x560 → JPEG q75 → base64
3. **Observe**: LLM 多模态视觉分析截图（Ollama qwen3-vl → vLLM Qwen3.6-VL 降级）
4. **Reflect**: 根据观察结果判定
   - `ok` → 步骤成功 → 更新计划状态为 `success` → 继续
   - `error` → 步骤失败 → 进入递进重试
   - `unknown` → LLM 无法判断 → 信任动作原始结果（非阻断）

### 新增：执行前视觉预检

从 2026-05-08 起，`Executor` 不再只做“动作后截图验收”，而是改成两段式：

1. **Precheck**
   - 动作执行前先截图
   - 用 `Ollama qwen3-vl` 判断当前页面是否适合执行这个步骤
   - 如果当前落在错误标签、错误页面、登录页，直接阻断该次 action，不再盲点
2. **Postcheck**
   - 动作执行后再次截图
   - 用步骤目标和成功线索做 Reflection 验证
   - 只有达到当前步骤目标，才允许进入下一步

这层的目的不是“多跑一次 LLM”，而是把：
- 当前屏幕状态识别
- 当前步骤是否该执行
- 执行后是否达成目标

显式拆开，避免 `fill_product_info` 这类复杂步骤在错误页面继续脚本化点击。

### 验证降级策略

| 层级 | 条件 | 行为 |
|------|------|------|
| 1 | LLM 可用 + 截图成功 | 截图 + LLM 视觉分析 |
| 2 | LLM 不可用或截图失败 | 信任 action_result 的 success 字段 |
| 3 | 高风险窗口漂移 + LLM 无法判断 | 按失败处理 |

### CLI 进度输出示例

```
[1/8] find_window: OK [动作结果兜底]
[2/8] activate_window: OK [动作结果兜底]
[3/8] navigate_to: OK [视觉验证通过]
[4/8] select_category: OK [视觉验证通过]
[5/8] fill_product_info: OK（重试 2 次） [视觉验证通过]
[6/8] save_draft: OK [视觉验证通过]
[7/8] verify_result: OK [视觉验证通过]
[8/8] publish_product: OK [视觉验证通过]
```

## Hello-Agents 范式对齐补充

参考 Hello-Agents 第四章，当前项目应明确对齐 3 个经典范式：

- `Plan-and-Solve`
  - 原理：先生成完整计划，再按计划执行
  - 项目对应：
    - `cli.py` 的 `plan` / `publish`
    - `agents/planner.py`
- `ReAct`
  - 原理：`Thought / Action / Observation` 动态循环
  - 项目对应：
    - `agents/executor.py`
    - `agents/base.py`
  - 在本项目里表现为：`Act -> Screenshot -> Observe -> Reflect`
- `Reflection`
  - 原理：`执行 -> 反思 -> 优化`
  - 项目对应：
    - `agents/base.py::reflect`
    - `agents/executor.py` 中的递进式重试

结论：

- 当前项目已经实现 `Plan-and-Solve`
- 当前项目已经实现 `ReAct`
- 当前项目已经实现 `Reflection`
- 但 GUI 执行层过去存在“状态未确认就继续点击”的问题，这属于范式落地不彻底，不是范式缺失

## GUI 状态锚点规范

### 禁止盲点击

- 不允许只靠固定滚动次数 + 固定坐标点击高风险区域
- 不允许在未确认页面状态前直接点击 `SKU`、价格、发布按钮
- 不允许把“鼠标能移动到该坐标”当成“页面已经准备好”

### 先识别状态锚点，再点击

处理 `SKU` / 价格区时，必须先确认可见锚点，再进入点击逻辑。

优先锚点：

- `市场价`
- `京东价`
- `SKU编码`
- `销售属性`

执行顺序：

1. 先滚动到目标区域
2. 截图或读取 UIA / 页面文本，确认锚点已出现
3. 只有锚点出现后，才允许 `hover -> click/doubleClick`
4. 写入后必须立即回读校验

如果锚点未出现：

- 继续滚动
- 重新观察
- 禁止继续点价格坐标

### 鼠标动作约束

- 普通定位动作必须优先使用：
  - `move -> hover -> click`
  - `move -> hover -> doubleClick`
- 普通定位不能实现成按住左键拖拽
- 若必须操作滚动条：
  - 优先点击轨道
  - 若必须拖动，日志中必须显式标注 `scrollbar drag`

### 日志要求

涉及高风险 GUI 动作时，日志至少记录：

- 当前阶段名
- 滚动次数与滚动量
- 识别到的状态锚点
- 实际点击坐标
- 写入结果
- 校验结果

这样出现问题时，才能区分：

- 是页面状态未到位
- 还是坐标命中错误
- 还是控件未获得焦点
- 还是旧 helper / 旧进程仍在执行旧逻辑

## Session1 Helper（关键修复）

### 问题背景
京麦客户端运行在 **Session 1**（用户桌面 session），而自动化脚本运行在 **Session 0**（Windows 服务上下文）。Session 0 发出的键盘事件无法传递到 Session 1 的京麦窗口。

### 解决方案
在 Session 1 中运行一个 Helper 辅助程序，接收来自脚本的命令，在正确的 session 中执行 Win32 操作。

### 使用步骤

**1. 启动 Helper（在你的电脑上双击运行）：**

```
双击文件: E:\workspace\skills\jingmai-product-publish\start_helper.bat
```

或命令行运行：
```bash
cd E:\workspace\skills\jingmai-product-publish
python session1_helper.py
```

**2. 验证 Helper 是否运行：**

```bash
python -c "
from pipe_client import PipeClient
c = PipeClient()
if c._connect():
    print('✅ Helper 已连接')
else:
    print('❌ Helper 未运行，请先启动 start_helper.bat')
"
```

**3. 使用方式（自动，无感）：**

所有自动化操作（点击、粘贴、按键）会自动优先使用 Helper，不需要手动干预。

### Helper 提供的操作

| 操作 | 说明 |
|------|------|
| `click(x, y)` | 点击指定坐标 |
| `paste(text)` | 剪贴板粘贴（最可靠的中文输入） |
| `hotkey(*keys)` | 快捷键，如 Ctrl+V |
| `press(key)` | 单键，如 Enter, Tab |
| `wait(seconds)` | 等待 |
| `find_jingmai()` | 查找京麦窗口 |

### 降级行为

如果 Helper 未运行，脚本会自动降级到 `pyautogui`（可能对 Java AWT 组件无效）。

---

## 故障排查

- `status` 里如果 LLM 不可用，先检查本地或远端模型服务
- 如果 `plan` 成功但任务仍是 `planning/pending`，说明只做了规划，还没执行
- 如果 `execute` 成功但没有任务状态，通常是传入了旧版 steps-only 计划且缺少 `task_id`
- 如果截图产物过多，先检查是否开启了 `JINGMAI_DEBUG_SCREENSHOTS=1`
- 如果怀疑动作被误判，优先查看计划文件步骤状态和短期记忆元数据，而不是只看一句摘要
