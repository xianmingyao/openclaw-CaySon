---
name: jingmai-product-publish
description: |
  京麦商品发布自动化技能。做什么：通过 Windows 桌面自动化完成京麦客户端商品发布、草稿保存、Excel批量导入、京东商品抓取、任务跟踪。何时用：用户提到「京麦发布」「批量上架」「jingmai」时触发。uv 管理依赖，一条命令安装。
---

## 触发词

- 京麦发布 / jingmai publish / jingmai / 京麦自动化 / 批量上架

## 对话式工作流

> Agent 根据用户意图匹配执行路径。每个箭头表示一个阶段，完成后暂停等待确认。

```
用户："帮我设置京麦环境"
  └─→ [1] 检查 uv → 安装依赖 → 安装 Chromium → check-config
       → 展示配置摘要 → ⏸ 用户确认
       → [2] init-db → ⏸ 用户确认数据库类型
       → ✅ 环境就绪

用户："导入这个 Excel 到京麦草稿"
  └─→ [1] 确认环境已就绪（否则先走上面流程）
       → [2] 扫描 Excel 结构（表头行号/合并单元格/模板行）
       → [3] **执行预处理脚本**（必做！）→ 生成 _cleaned.xlsx
       → [4] 展示商品摘要（数量/类目/耗时/缺失字段）→ ⏸ 用户确认
       → [5] run-import --mode draft → 实时进度 → ✅ 导入完成

用户："把草稿正式发布"
  └─→ [1] 展示待发布商品摘要 → ⏸ 用户输入 yes 确认
       → [2] run-desktop-check --step t8-publish-product --confirm-publish
       → [3] check-evidence 展示截图证据 → ✅ 发布完成

用户："京麦出问题了 / 报错了 / 没反应"
  └─→ [1] 收集症状 → 匹配「故障排查」表
       → [2] 按优先级尝试解决方案 → 每步验证 → ✅ 问题解决或升级
```

## 快速开始

### 环境安装（uv 管理）

| 步骤 | 命令 | 说明 |
|------|------|------|
| 1. 安装 uv | `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 \| iex"` | 仅首次需要；已有 uv 则跳过 |
| 2. 安装依赖 | `uv sync --dev` | 自动创建 `.venv`，安装所有依赖 |
| 3. 安装浏览器 | `uv run playwright install chromium` | Playwright 需要 Chromium 浏览器 |
| 4. 验证安装 | `uv run jingmai-publish check-config --root .` | 确认环境配置正确 |

```bash
# 完整安装流程（在项目目录执行）
cd E:\workspace\skills\jingmai-product-publish

# 步骤1：安装 uv（如果还没有）
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 步骤2：安装所有依赖
uv sync --dev

# 步骤3：安装 Playwright 浏览器
uv run playwright install chromium

# 步骤4：验证安装
uv run jingmai-publish check-config --root .
```

**环境要求：**
- Windows 10/11
- 已安装并登录京麦客户端
- 建议分辨率 `2560x1392`

## Excel 格式规范

> 导入前必须按此规范校验 Excel，避免解析失败。

### 结构要求

| 要求 | 说明 |
|------|------|
| 工作表名称 | **必须命名为 `上架模板`**（代码硬编码 `sheet_name="上架模板"`，名称不匹配会导致 `KeyError`）。预处理脚本也需确保处理后 sheet 名为 `上架模板` |
| 表头行 | 代码硬编码读取第3行为表头、第4行起为数据。**导入前必须预处理**，将真实表头对齐到第3行（见下方预处理脚本） |
| 第1列（A列） | 必须是**纯数字**上架序号（1, 2, 3…），含"模板"等文字会导致 `int('模板')` 崩溃 |
| 无合并单元格 | 数据区域内禁止合并单元格，否则 openpyxl 读到的值为 None |
| 无空行 | 数据之间不允许有空行，遇到空行即停止解析 |
| 其他 sheet | 其他 sheet（如"资质要求""参考链接"）不会自动导入，但不会影响主 sheet 解析 |

> **实测案例**：`4.28机械臂上架.xlsx` 第1行标题+第2行提示+第3行表头+第4行模板示例，直接导入报错 `invalid literal for int() with base 10: '模板'`。经预处理脚本清理后导入成功。

### 字段→列映射（硬编码）

导入代码按列索引读取（`raw_row[0]`…`raw_row[14]`），列位置固定不可调：

| Excel 列 | 索引 | 字段名 | 说明 | 缺失时 |
|------|------|------|------|--------|
| A | `[0]` | 上架序号 | **纯数字**（1, 2, 3…） | **阻断**—`int()` 崩溃 |
| B | `[1]` | 适用业务 | 可选文本 | 无影响 |
| C | `[2]` | **商品名称** | 对应京东开票内容 | **阻断**—无法导入 |
| D | `[3]` | 品牌 | 可选 | 无影响 |
| E | `[4]` | 型号 | 可选 | 无影响 |
| F | `[5]` | 长度(mm) | 数字或空 | 无影响 |
| G | `[6]` | 宽度(mm) | 数字或空 | 无影响 |
| H | `[7]` | 高度(mm) | 数字或空 | 无影响 |
| I | `[8]` | 重量(kg) | 数字或空 | 无影响 |
| J | `[9]` | 单位 | 可选文本（默认"个"） | 无影响 |
| K | `[10]` | **京东挂网价** | 纯数字，下单金额 | **阻断**—无法导入 |
| L | `[11]` | **京东链接** | `https://item.jd.com/` 格式 | **阻断**—无法导入 |
| M | `[12]` | 商品资质 | PDF/图片路径，嵌入单元格 | ⚠️ 警告—可导入但京麦审核不通过 |
| N | `[13]` | 商品摘要 | 可选文本 | 无影响 |
| O | `[14]` | 备注 | 可选文本 | 无影响 |

> **关键规则**：A列必须纯数字、C列+J列+L列不可为空。其他列可为空。

### 格式预处理（导入前必须执行）

> **重要**：导入工具硬编码读取第3行为表头、第4行起为数据。微信/邮件传输的 Excel 几乎都有标题行和提示行，**必须先执行以下预处理脚本再导入**。

**Agent 执行流程：**

```bash
# Step 1: 扫描 Excel 结构（只读，不修改）
uv run python -c "
import openpyxl, sys
wb = openpyxl.load_workbook(sys.argv[1], read_only=True, data_only=True)
ws = wb.active
print(f'Sheet: {ws.title} (requires: 上架模板), Rows: {ws.max_row}, Cols: {ws.max_column}')
print(f'All sheets: {wb.sheetnames}')
for i, row in enumerate(ws.iter_rows(min_row=1, max_row=min(6, ws.max_row), values_only=True), 1):
    vals = [str(v)[:40] if v else '-' for v in row[:15]]
    print(f'Row {i}: {vals}')
" "D:\path\to\file.xlsx"
```

```bash
# Step 2: 执行预处理（生成清理后的文件）
uv run python -c "
import openpyxl, sys
src = sys.argv[1]
dst = src.replace('.xlsx', '_cleaned.xlsx')
wb = openpyxl.load_workbook(src)
ws = wb.active

# 2.0 确保 sheet 名为「上架模板」（excel_ingest 硬编码 sheet_name='上架模板'）
target_name = '上架模板'
if ws.title != target_name:
    # 如果已存在同名 sheet，先删除（保留当前 ws，只删旧的）
    if target_name in wb.sheetnames:
        del wb[target_name]
    ws.title = target_name
    print(f'Sheet renamed: \"{wb.active.title}\" -> \"{target_name}\"')
else:
    print(f'Sheet name OK: \"{ws.title}\"')

# 2.1 找到真实表头行（含「商品名称」+「京东挂网价」的行）
# 注意：不用 values_only=True，因为需要 Cell.row 属性获取行号
header_row = None
for row in ws.iter_rows(min_row=1, max_row=min(10, ws.max_row)):
    vals = [str(cell.value) if cell.value else '' for cell in row]
    if any('商品名称' in v for v in vals) and any('京东挂网价' in v for v in vals):
        header_row = row[0].row
        break

# Fallback: 找不到则用硬编码行号
if header_row is None:
    print('WARNING: 未检测到表头行，使用默认值第3行')
    header_row = 3  # 可调整

# 2.2 解除所有合并单元格（取左上角值填充）
for merge_range in list(ws.merged_cells.ranges):
    top_left = ws.cell(merge_range.min_row, merge_range.min_col).value
    ws.unmerge_cells(str(merge_range))
    for r in range(merge_range.min_row, merge_range.max_row + 1):
        for c in range(merge_range.min_col, merge_range.max_col + 1):
            ws.cell(r, c).value = top_left

# 2.3 清空表头上方的所有行（不清除行号，保持表头在原位置，因为 excel_ingest 硬编码从第3行读取表头）
if header_row > 1:
    for r in range(1, header_row):
        for c in range(1, ws.max_column + 1):
            ws.cell(r, c).value = None

# 2.4 删除模板示例行（第1列包含非数字如「模板」的行）
rows_to_delete = []
for row in ws.iter_rows(min_row=header_row + 1, max_row=ws.max_row):
    val_a = row[0].value
    if val_a is not None:
        try:
            int(val_a)
        except (ValueError, TypeError):
            rows_to_delete.append(row[0].row)

# 从下往上删除，避免行号偏移
for r in reversed(rows_to_delete):
    ws.delete_rows(r, 1)

wb.save(dst)
print(f'Cleaned: {dst}')
print(f'Sheet name: {ws.title}')
print(f'Header row: {header_row}')
print(f'Data rows: {ws.max_row - header_row}')
" "D:\path\to\file.xlsx"

# Step 3: 用清理后的文件导入
uv run jingmai-publish run-import --excel "D:\path\to\file_cleaned.xlsx" --mode draft --root .
```

**预处理做了什么：**
1. 重命名 sheet 为 `上架模板`（代码硬编码读取此名称，否则导入报 `KeyError`）
2. 扫描前10行找到含「商品名称」+「京东挂网价」的真实表头行
3. 解除所有合并单元格（取左上角值填充）
4. 清空表头上方的标题行、提示行（保留行号，避免表头位置偏移，因为导入代码硬编码从第3行读取）
5. 删除第1列（A列）非纯数字的模板示例行
6. 保存为 `原文件名_cleaned.xlsx`

### 解析摘要模板

> 在检查点2展示，用户确认前必须输出。

```
## Excel 解析摘要
| 项目 | 内容 |
|------|------|
| 文件 | {文件名}（{工作表数}个sheet，仅导入第1个） |
| 表头行 | 第{行号}行 |
| 有效数据 | {N} 条 |
| ⚠️ 缺失字段 | {字段名: 行号列表} |
| ⚠️ 跳过行 | 第{行号}行（原因：{空行/模板行}） |

### 待导入商品
| # | 名称 | 价格 | 链接 | 资质 | 数量 |
|---|------|------|------|------|------|
```

## 配置

项目通过 `.env` 文件管理配置。首次使用前需在项目根目录创建 `.env` 文件：

```bash
# ── 数据库（MySQL 连接失败自动降级到 SQLite，可不填）──
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=jingmai_agent
# MYSQL_CHARSET=utf8mb4        # 可选，默认 utf8mb4
# MYSQL_POOL_SIZE=10            # 可选，连接池大小
# MYSQL_MAX_OVERFLOW=20         # 可选，连接池溢出上限

# ── Redis（用于任务队列缓存）──
# REDIS_URL=redis://127.0.0.1:6379/0    # 可选，有默认值

# ── 飞书集成 ──
# FEISHU_APP_ID=
# FEISHU_APP_SECRET=
# FEISHU_VERIFY_TOKEN=          # 可选，事件订阅验证
# FEISHU_ENCRYPT_KEY=           # 可选，消息加密密钥

# ── Ollama Vision（截图分析用）──
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_MODEL=qwen3-vl:8b
# VISION_ENABLED=true            # 可选，默认 true
# LLM_TIMEOUT=120                # 可选，默认 120s

# ── vLLM（可选替代 Ollama）──
# VLLM_BASE_URL=http://localhost:8000/v1
# VLLM_MODEL=qwen3-vl:8b

# ── Milvus 向量数据库（可选，记忆检索用）──
# MILVUS_HOST=127.0.0.1
# MILVUS_PORT=19530
# MILVUS_COLLECTION=jingmai_agent_memory

# ── 其他 ──
# DEBUG=true                     # 可选，调试模式
# SCREENSHOT_ENABLED=true        # 可选，默认 true
# LOG_RETENTION_DAYS=3           # 可选，日志保留天数
```

配置验证通过后，初始化数据库：

```bash
uv run jingmai-publish init-db --root .
```

## CLI 命令

> 所有命令均通过 `uv run jingmai-publish <子命令>` 执行。也可用 `python cli.py <子命令>` 在已激活的 venv 中运行。

### 环境检查

```bash
uv run jingmai-publish check-config --root .
```

### 初始化数据库

```bash
uv run jingmai-publish init-db --root .
```

### 导入商品（草稿模式）

```bash
uv run jingmai-publish run-import --excel ".\湖南上架表格.xlsx" --mode draft --root .
```

### 桌面执行检查

```bash
uv run jingmai-publish run-desktop-check --step both --debug --root .
```

### 正式发布（有人工守卫）

```bash
uv run jingmai-publish run-desktop-check --step t8-publish-product --confirm-publish --root .
```

### 检查证据

```bash
uv run jingmai-publish check-evidence --root .
```

### 清理运行时日志

```bash
uv run jingmai-publish cleanup-runtime-logs --root .
```

### E2E 草稿测试（单行→京麦桌面）

```bash
uv run jingmai-publish run-draft-e2e --excel ".\file_cleaned.xlsx" --item-index 0 --main-image-path ".\img\main.png" --transparent-image-path ".\img\trans.png" --root .
```

### 本地路径消息触发

```bash
uv run jingmai-publish run-local-path-task --path-file ".\message.json" --mode draft --root .
```

### 飞书事件触发

```bash
uv run jingmai-publish run-feishu-path-task --payload-file ".\feishu_event.json" --mode draft --root .
```

## 执行模型

```
Plan-and-Solve（文档驱动规划）
  └─ 解析京麦上架流程.docx正文 → 生成带workflow元数据的步骤
        ↓
ReAct（每步完整循环）
  └─ Precheck(截图预检) → Act(执行动作) → Screenshot(截图) → Observe(LLM视觉分析) → Postcheck(截图复核)
        ↓
Reflection（递进式重试，最多3次）
```

**关键设计：**
- **Precheck + Postcheck** — 执行前后截图对比，偏差自动恢复
- **页面态恢复策略** — 覆盖登录/商品列表/类目/商品信息/规格/发布确认 6 种页面
- **发布守卫** — `t8-publish-product` 步骤需 `--confirm-publish` 明确授权，防止误发布
- **自动降级** — MySQL 连接失败自动切换到 SQLite

## 检查点（Checkpoints）

> 每个关键操作前 Agent 必须暂停，等待用户确认后再继续。不可自主跳过。

| 阶段 | 检查点 | 确认方式 | 不通过时 |
|------|--------|---------|---------|
| 环境初始化 | `check-config` 通过后，展示配置摘要 | 用户确认"环境OK" | 修正 `.env` 后重新验证 |
| 数据库初始化 | `init-db` 执行前，确认数据库类型（MySQL/SQLite） | 用户确认"初始化" | 检查数据库连接后重试 |
| Excel 预处理 | **导入前必做**：扫描 Excel 结构 → 执行预处理脚本 → 生成 `_cleaned.xlsx` | 展示预处理日志（删除行数/表头位置/数据行数） | 检查原始 Excel 格式，调整脚本参数后重新预处理 |
| Excel 导入 | 解析后展示：商品数量、类目分布、预计耗时、**缺失字段清单**（必填项为空→阻断，可选项为空→警告） | 用户确认"开始导入" | 补全缺失字段或修正 Excel 格式后重新解析 |
| 正式发布 | 展示待发布商品摘要（数量/类目/价格区间），**含资质完整性检查** | 用户输入 `yes` 或传 `--confirm-publish` | 返回草稿模式，不执行发布 |
| 批量操作 | 展示操作计划（步骤数/预计耗时/风险点）+ **依赖项就绪检查** | 用户确认"执行" | 调整参数或补全依赖后重新规划 |

## 调试选项

```bash
--verbose          # 详细输出
--log-file logs/cli-debug.log  # 日志文件
```

## Session1 Helper

京麦客户端运行在 Session 1（用户桌面会话），而脚本运行在 Session 0（服务会话）或其他非交互会话时，发出的操作无法传递到京麦窗口。

> **为什么有两个目录？** `jingmai-product-publish`（本目录）是发布主流程，`jingmai-product-publish-v2`（Session1 Helper 所在目录）负责桌面自动化桥接。两个项目配合使用，缺一不可。

**启动 Helper：**
```bash
# 在 Session1 Helper 项目目录执行（注意：是 v2 目录）
cd E:\workspace\skills\jingmai-product-publish-v2
uv run python session1_helper.py
# 或双击 start_helper.bat
```

**验证 Helper 是否运行：**
```bash
# 回到主项目目录
cd E:\workspace\skills\jingmai-product-publish
uv run jingmai-publish run-desktop-check --step t1-login-check --root .
# 如果能截到京麦窗口 → Helper 正常工作
```

## 故障排查

| 症状 | 可能原因 | 解决方案 |
|------|---------|---------|
| `uv` 命令不存在 | uv 未安装 | 执行步骤1安装 uv，或 `pip install uv` |
| `uv sync` 失败 | Python < 3.12 | 安装 Python 3.12+，推荐 `winget install Python.Python.3.12` |
| `playwright install` 失败 | 网络问题或权限不足 | 管理员 PowerShell 重试；配置代理后重试 |
| `check-config` 输出 `success: false` | 配置缺失或不合法 | 检查 `.env` 文件是否存在、MYSQL_PORT 范围、REDIS_URL/OLLAMA_BASE_URL 格式 |
| 数据库初始化失败 | MySQL 连接不上 | 检查 `MYSQL_*` 环境变量；脚本会自动降级到 SQLite，可留空 |
| 桌面操作无响应 | Session1 Helper 未启动 | 双击 `start_helper.bat` 或在 v2 目录运行 `uv run python session1_helper.py` |
| 京麦窗口未找到 | 京麦未登录或窗口标题不匹配 | 确认京麦客户端已登录并显示在主桌面 |
| 截图分析超时 | Ollama 未启动或显存不足 | 确认 `ollama serve` 运行中，检查 `OLLAMA_BASE_URL` 配置 |
| Excel 导入报错 | 表头不匹配或数据格式异常 | 对照模板检查列名（商品名称/价格/库存/类目/规格/图片）；确保无合并单元格 |
| `invalid literal for int() with base 10: '模板'` | Excel 第4行是模板示例行（第1列="模板"），代码 `int('模板')` 崩溃 | **必须执行预处理脚本**（见上方「格式预处理」章节），删除模板行后再导入 |
| `invalid literal for int()` 其他值 | Excel 第1列（A列）包含非数字内容 | 检查 A 列所有值是否为纯数字序号（1,2,3…）；删除模板行、标题行、空行 |
| Excel 导入0条 | 代码从第4行开始读数据，表头上方有行导致第4行是空的 | 执行预处理脚本清理表头上方行；或手动删除前N行使表头对齐到第3行、数据从第4行开始 |
| Excel 解析到空值 | 合并单元格导致 openpyxl 读取为 None | 先执行 `uv run python -c "import openpyxl; wb=openpyxl.load_workbook('文件'); print(wb.active.merged_cells.ranges)"` 确认合并区域，手动取消合并后重新导入 |
| Excel 表头不在第1行 | 微信/邮件传输的 Excel 有标题行和提示行（代码硬编码读第3行表头，不兼容非标准格式） | **必须执行预处理脚本**（见上方「格式预处理」章节），自动检测表头+删除上方行+清理模板行+解除合并；不可手动删除（容易出错） |
| Excel 有多个 sheet | 其他 sheet 含资质要求/参考链接等辅助信息 | 只导入第一个 sheet；确保第一个 sheet 是商品数据，辅助信息移到其他 sheet |
| 商品资质列为空 | Excel 中未嵌入资质图片/PDF | 可导入草稿但京麦审核不通过；建议补全资质文件后重新导入；如紧急先导入草稿再补资质 |
| 必填字段缺失 | 商品名称/京东挂网价/京东链接为空 | 展示缺失字段清单（字段名+行号），用户补全后重新导入；不允许跳过必填字段导入 |
| UIA 元素找不到 | 京麦版本更新导致元素路径变化 | 运行 `run-desktop-check --step t1-login-check --debug` 生成最新截图，比对元素定位 |
| 发布后商品未显示 | 京东审核延迟 | 等待 5-10 分钟刷新；检查「待审核」tab；非报错，属正常流程 |
| 批量导入中途卡住 | 某个商品数据异常导致流程中断 | 查看 `logs/` 目录下的错误日志，定位失败商品行号，修正后单独导入 |
| 京麦客户端闪退 | 京麦自身稳定性问题 | 重新登录京麦；运行 `check-config` 确认环境；从断点续传（已导入商品不会重复） |
| 分辨率不匹配 | 非 2560×1392 导致坐标偏移 | 调整分辨率至推荐值；或在 `.env` 中设置 `SCREEN_WIDTH`/`SCREEN_HEIGHT` 覆盖默认坐标 |

## 项目文件

| 文件 | 用途 |
|------|------|
| `pyproject.toml` | 项目元数据、依赖声明、CLI 入口点 |
| `.env` | 运行时配置（需自行创建，参考上方「配置」章节） |
| `uv.lock` | 依赖版本锁定文件（`uv sync` 自动生成） |
| `jingmai_publish/cli.py` | CLI 命令入口（`jingmai-publish` → `cli:main`） |
| `jingmai_publish/config.py` | 配置加载与校验逻辑 |
| `jingmai_publish/bootstrap.py` | 数据库初始化逻辑 |
| `jingmai_publish/services/` | 核心业务服务（导入、发布、证据等） |
| `jingmai_publish/agent/` | Agent 执行引擎（Planner/Executor/Reflection） |
| `jingmai_publish/desktop/` | 桌面自动化适配层（UIA/Win32） |
| `logs/` | 运行日志（`--log-file` 可指定路径） |
| `resources/screenshots/` | 截图证据目录 |
