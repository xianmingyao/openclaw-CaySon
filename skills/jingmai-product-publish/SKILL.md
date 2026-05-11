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
uv run python cli.py publish --config product.json --workflow-policy doc_strict
```

说明：

- `publish` 是主入口
- 先做 `plan`，再立刻进入 `execute`
- `--plan-out` 会保存完整计划包，便于监控和恢复执行
- `--workflow-policy doc_strict` 会强制解析 `京麦上架流程.docx` 正文并生成计划，不走自由 LLM 规划

### 只生成计划

```bash
uv run python cli.py plan "发布一个手机壳商品" --config product.json
uv run python cli.py plan --config product.json
uv run python cli.py plan --config product.json --steps-only
uv run python cli.py plan --config product.json --workflow-policy doc_strict
python cli.py plan --config product.json
```

说明：

- 默认输出完整计划包
- `--steps-only` 只输出步骤数组，兼容旧脚本
- `--workflow-policy doc_strict` 会输出带 `workflow_source / workflow_section / workflow_requirement / workflow_excerpt / workflow_paragraphs` 的文档驱动计划

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

### live-run（默认跑湖南上架表格）

```bash
uv run python cli.py live-run
uv run python cli.py live-run --file "湖南上架表格.xlsx"
uv run python cli.py live-run --file "湖南上架表格.xlsx" --resume
python cli.py live-run --file "湖南上架表格.xlsx"
```

说明：

- `live-run` 默认使用 `doc_strict` 计划策略
- 启动前会先截图分析当前京麦屏幕状态，再进入 `Plan-and-Solve`
- 每步都执行 `precheck -> act -> postcheck/reflection`
- 当 `precheck` / `action` / `postcheck` 检测到偏差时，会先走“偏差类型 -> 恢复 action -> 再验证”的恢复矩阵
- 单步最多重试 3 次，仍失败则立即停止当前商品
- 默认停在首个失败商品，避免被桌面环境反复拖死

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
- 抓取顺序为：缓存 HTML → `Playwright` → `OpenCLI browser` → JD API → HTML 解析
- 详情图会下载到本地，并把本地路径写入数据库字段

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

### 1.1 MySQL 连接策略

- 现在支持从 `.env` 自动拼接 `MYSQL_URL`
- 当存在以下变量时会自动启用 MySQL：
  - `MYSQL_HOST`
  - `MYSQL_PORT`
  - `MYSQL_USER`
  - `MYSQL_PASSWORD`
  - `MYSQL_DATABASE`
  - `MYSQL_CHARSET`
  - `MYSQL_POOL_SIZE`
  - `MYSQL_MAX_OVERFLOW`
- 如果 MySQL 连接失败，仍会降级到本地 SQLite

### 1.2 Excel 判型与来源元数据

- `.xlsx/.xlsm` 现在会给每个商品写入：
  - `publish_mode`: `single` / `batch`
  - `source_meta.source_file`
  - `source_meta.sheet_name`
  - `source_meta.row_index`
  - `source_meta.item_index`
  - `source_meta.total_items`
  - `source_meta.workflow_doc`
- `湖南上架表格.xlsx` 当前会被判定为 `single`
- 若同一表中解析出多条有效商品行，则自动切为 `batch`

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

### 4.1 文档驱动计划模板

从本轮修复开始，`Planner` 支持 `workflow_policy=doc_strict`：

- 跳过自由 LLM 规划
- 先解析 `京麦上架流程.docx` 正文段落，再从真实段落生成步骤
- 默认步骤顺序为：
  1. `find_window`
  2. `activate_window`
  3. `navigate_to`
  4. `select_category`
  5. `fill_product_info`
  6. `fill_product_description`
  7. `publish_product`
  8. `verify_result`

每个步骤额外携带：

- `workflow_source`
- `workflow_section`
- `workflow_requirement`
- `workflow_excerpt`
- `workflow_paragraphs`

用于后续排障时明确“当前动作在文档流程中的位置”，而不是只看 action 名。

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

### 新增：live-run 包装入口

`live-run` 不是新的执行器，而是对现有执行模型的强约束包装：

1. 先读取 Excel
2. 自动判断 `single / batch`
3. 强制使用 `doc_strict` 计划
4. 调 `Planner._capture_screen_context()` 做截图分析
5. 执行 `Plan-and-Solve -> ReAct -> Reflection`
6. 每商品失败即停

这样做的目的是把“真实上架运行”与普通 `batch` 区分开，减少误把半成品策略用到桌面 live 流程里。

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

## 当前完成度评估与缺口清单

评估日期：`2026-05-11`

当前针对“读取 Excel → 区分单品/批量 → 抓取京东商品 → 图片本地化 → MySQL 持久化 → 按京麦流程执行上架 → 截图视觉校验 → 失败最多重试 3 次”的整体能力，评估分数为：

- **78 / 100**

### 分项评分

- Excel 读取与单品/批量识别：`18/20`
- JD 抓取与图片本地化：`16/20`
- MySQL 持久化：`14/15`
- 文档驱动规划：`10/15`
- Ollama 视觉执行闭环：`14/20`
- 真实可上线实战稳定性：`6/10`

### 已完成的关键能力

- 已支持读取 `.xlsx` / `.xlsm` 并区分 `single` / `batch`
- 已为商品写入 `publish_mode` 与 `source_meta`
- 已支持 `Playwright -> OpenCLI -> API -> HTML` 的京东抓取链路
- 已支持下载详情图到本地，并将本地路径写入数据库字段 `detail_images`
- 已支持通过 `MYSQL_HOST / MYSQL_PORT / MYSQL_USER / MYSQL_PASSWORD / MYSQL_DATABASE` 自动拼接 MySQL 连接
- 已具备 `Plan-and-Solve -> ReAct -> Reflection` 的执行主循环
- 已提供 `live-run` 命令，默认可直接跑 `湖南上架表格.xlsx`

### 当前扣分最多的半完成项

- **文档驱动规划已升级到 docx 正文解析驱动**
  - 当前做法是先读取 `京麦上架流程.docx` 的正文段落
  - 再从真实段落中提取操作路径、类目步骤、商品信息段、规格描述段、最终发布段
  - 目前已经不是单纯的固定中文模板，但仍未做到“执行时逐条反查文档合规性”

- **Ollama 视觉能力当前本质上仍是截图级别**
  - 已支持截图视觉预检与执行后复核
  - 但“图像视频辅助识别”中的视频帧分析、录屏分析链路尚未真正实现

- **`live-run` 目前是现有执行器的包装入口**
  - 优点是能复用现有的计划、断点续跑、视觉校验、重试逻辑
  - 缺点是它还不是一个为桌面实操专门抽象出来的独立运行器
  - 因此鲁棒性上仍继承原 `batch/publish/executor` 的限制

- **执行器已具备第一版偏差恢复矩阵，但仍可继续细化**
  - 当前已经支持把 `precheck / action / postcheck / window shift` 失败归类
  - 当前已经支持按偏差类型执行恢复动作，例如 `recover_locator / force_relocate / navigate_to / select_category / wait`
  - 当前已经支持恢复后再次执行视觉预检确认状态是否回正
  - 当前已经支持按页面态细分恢复策略，例如 `登录页 / 商品列表页 / 类目页 / 商品信息页 / 规格描述页 / 发布确认页`
  - 但恢复动作仍未覆盖所有京麦页面分支、弹窗分支、异常状态分支

### 尚未完成，或没有证据证明已完成

- **没有真实端到端实跑闭环证据**
  - 代码中已有 `live-run`
  - 但这不等于已经在真实京麦桌面环境中稳定完成了 `湖南上架表格.xlsx` 的完整上架

- **没有文档级别的步骤合规校验**
  - 当前步骤会带 `workflow_section`
  - 当前步骤会带 `workflow_requirement`
  - 当前步骤会带 `workflow_source`
  - 当前步骤会带 `workflow_excerpt`
  - 当前步骤会带 `workflow_paragraphs`
  - 但执行时不会反查“当前执行结果是否符合 docx 的具体条款”

- **偏差恢复矩阵已实现到页面级，但异常分支覆盖仍不完整**
  - 当前已经形成“偏差类型 -> 页面态 -> 恢复 action -> 再验证”的明确恢复矩阵
  - 但还没有覆盖所有京麦页面分支、弹窗分支、异常状态分支

- **批量场景与单品场景还没有完全分治**
  - 当前只是打上 `publish_mode`
  - 还没有形成“批量专用计划模板 / 批量失败回滚 / 批量草稿策略”等独立流程

- **数据库持久化还不够细**
  - 当前已保存商品、任务、步骤、图片路径、来源元数据
  - 但还缺少抓取来源优先级、图片下载状态、重试轨迹、最终发布回执等细粒度落库

- **OpenCLI 兜底尚未抽象成 provider 层**
  - 当前能调用 `E:\PY\opencli` 进行浏览器兜底抓取
  - 但实现仍偏向命令拼接调用，尚未沉淀成统一 provider abstraction

### 当前最关键的后续开发优先级

1. 把 `京麦上架流程.docx` 从“路径引用 + 模板映射”升级成“真正解析文档并驱动 planner”
2. 跑一次真实 `湖南上架表格.xlsx` 的端到端桌面验证，拿到成功/失败证据
3. 把批量模式和单品模式拆成不同的业务计划模板
4. 细化数据库落库，补齐抓取轨迹、图片状态、发布回执
5. 继续补页面级异常恢复库，覆盖更多弹窗、审核页、异常页和边缘分支

### 使用预期边界

- 这个 skill **已经具备开发态可运行能力**
- 这个 skill **还不能宣称已达到稳定生产可无人值守上架**
- 在未完成上述缺口前，所有 `live-run` 结果都应视为“受环境、登录态、窗口状态、视觉模型状态影响的桌面自动化实验结果”

## 故障排查

- `status` 里如果 LLM 不可用，先检查本地或远端模型服务
- 如果 `plan` 成功但任务仍是 `planning/pending`，说明只做了规划，还没执行
- 如果 `execute` 成功但没有任务状态，通常是传入了旧版 steps-only 计划且缺少 `task_id`
- 如果截图产物过多，先检查是否开启了 `JINGMAI_DEBUG_SCREENSHOTS=1`
- 如果怀疑动作被误判，优先查看计划文件步骤状态和短期记忆元数据，而不是只看一句摘要
