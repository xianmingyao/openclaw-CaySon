# 京麦桌面商品上架系统 (Jingmai Desktop Product Publish)

> 基于 Windows 桌面自动化（UIA）的京麦商品发布全流程自动化系统。零 API 依赖，纯 UI 操作链路。

[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-216%20passed-brightgreen)](./tests/)
[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)

---

## 目录

- [1. 项目背景](#1-项目背景)
- [2. 系统架构](#2-系统架构)
- [3. 环境准备](#3-环境准备)
- [4. 命令使用指南](#4-命令使用指南)
- [5. T1-T8 发布流程详解](#5-t1-t8-发布流程详解)
- [6. 教学指南（快速上手）](#6-教学指南快速上手)
- [7. 常见问题](#7-常见问题)
- [8. 开发指南](#8-开发指南)

---

## 1. 项目背景

### 1.1 为什么要做这个项目

京麦（JD 商家后台桌面客户端）是京东商家日常运营的核心工具。商家每天需要发布大量商品，而京麦桌面端没有开放 API，所有操作必须通过 UI 操作完成。

**痛点：**
- 手动填写一个商品需要 15-30 分钟，涉及 8 个页签、50+ 字段
- 字段位置因类目不同而动态变化，容易填错
- 图片上传需要精确的文件对话框操作，无法通过简单脚本完成
- 没有可用的批量上架工具

**解决方案：**
本系统通过 **Windows UI Automation (UIA)** 直接与京麦桌面端交互，模拟人工操作的每一步 —— 从窗口接管到商品信息填充，再到图片上传和最终发布/保存草稿，全部自动化完成。

### 1.2 核心能力

| 能力 | 说明 |
|------|------|
| **窗口接管** | 自动发现并接管京麦窗口，兼容多版本京麦客户端 |
| **类目导航** | 智能识别类目选择页，推进到发布表单 |
| **信息填充** | 标题、型号、品牌、必填属性、SKU 价格/规格等一键填充 |
| **图片上传** | 主图、透图的本地上传链路（Alt+D 地址栏导航、文件对话框操作） |
| **详情编辑** | 代码编辑器写入 HTML 详情内容，支持抓取京东商品详情 |
| **物流信息** | 销售单位、包装、质保期等物流字段填充 |
| **草稿/发布** | 保存草稿或直接发布商品 |

### 1.3 技术栈

```
Python 3.12
├── pywinauto        → Windows UIA 桌面自动化（F12 SDK 探测器兼容）
├── playwright        → 浏览器自动化（京东详情抓取）
├── SQLAlchemy        → ORM（MySQL，任务与日志持久化）
├── openpyxl          → Excel 商品数据读取
├── Pillow            → 图片尺寸预检
├── BeautifulSoup 4   → HTML 清洗与解析
└── pytest            → 测试框架（216 个测试用例）
```

---

## 2. 系统架构

### 2.1 分层架构

```
┌────────────────────────────────────────────┐
│                 CLI 层 (cli.py)              │  ← 7 个子命令入口
├────────────────────────────────────────────┤
│             Service 层 (services/)           │  ← 任务编排、E2E 流程
│  DesktopVerificationService                 │
│  DraftE2EOrchestrator                       │
│  ImportPipelineService                      │
├────────────────────────────────────────────┤
│          Agent 决策层 (agent/)               │  ← Planner → Executor → Reflection
│  AgentPipeline  (规划→执行→反思闭环)          │
├────────────────────────────────────────────┤
│          Runtime 运行时 (runtime/)            │  ← HostRuntime, EventLoop, Manifest
│  observe → decide → act → verify → repeat   │
├────────────────────────────────────────────┤
│          Desktop 桌面层 (desktop/)            │  ← UIA Adapter, WindowManager
│  screen_ai_adapter / uia_adapter            │
├────────────────────────────────────────────┤
│          Workflow 工作流 (jingmai_workflow)   │  ← T1-T8 具体操作实现
├────────────────────────────────────────────┤
│      DB / Repositories (db/, repositories/)  │  ← MySQL 持久化
└────────────────────────────────────────────┘
```

### 2.2 Agent 决策闭环（BL-091）

系统核心是一个 **Planner → Executor → Reflection** 的决策管线：

1. **Planner**：解析目标步骤，生成有序的 `ActionStep` 列表（拓扑排序，含前置条件检查）
2. **Executor**：通过反射调用 (`getattr`) 执行每个步骤，失败自动重试
3. **Reflection**：根据结果决定 **CONTINUE（继续）** / **RETRY（重试）** / **SKIP（跳过）** / **ABORT（中止）**

```
plan = planner.plan(step)
for each action in plan:
    for attempt in 1..max_retry:
        outcome = executor.execute(action)
        decision = reflection.reflect(action, outcome)
        if CONTINUE: break
        if ABORT: halt pipeline
        if RETRY: continue
```

---

## 3. 环境准备

### 3.1 系统要求

- **操作系统**：Windows 10/11（UIA 自动化仅支持 Windows）
- **Python**：3.12+
- **数据库**：MySQL 8.0+（推荐）
- **京麦客户端**：已安装并可以正常登录

### 3.2 安装依赖

```bash
# 1. 克隆项目
git clone <repo-url>
cd jingmai-product-publish-v2

# 2. 安装依赖
pip install -r requirements.txt

# 3. 确认 pywinauto 后端可用
python -c "from pywinauto import Application; print('pywinauto OK')"
```

### 3.3 配置 .env 文件

在项目根目录创建 `.env` 文件：

```env
# 数据库（必填）
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=jingmai_agent

# 可选配置
DEBUG=false
LOG_DIR=logs
SCREENSHOT_DIR=resources/screenshots
SCREENSHOT_ENABLED=true

# 飞书通道（如使用飞书任务触发时需要）
# FEISHU_APP_ID=cli_xxx
# FEISHU_APP_SECRET=xxx
```

### 3.4 初始化数据库

```bash
python -m jingmai_publish.cli init-db
```

---

## 4. 命令使用指南

系统提供 **7 个 CLI 命令**，覆盖从数据导入到桌面执行的完整链路。

### 4.1 命令概览

| 命令 | 用途 | 适用场景 |
|------|------|----------|
| `init-db` | 初始化数据库表结构 | 首次部署 |
| `run-import` | 从 Excel 读取创建任务 | 批量导入商品 |
| `run-local-path-task` | 从本地路径消息触发任务 | 本地自动化触发 |
| `run-feishu-path-task` | 从飞书事件 payload 触发任务 | 飞书消息通道触发 |
| `cleanup-runtime-logs` | 清理过期日志与截图 | 定期维护 |
| `run-draft-e2e` | 全流程执行到保存草稿 | 单商品自动化上架 |
| `run-desktop-check` | 单步探针/闭环验证 | 调试、分步骤测试 |

---

### 4.2 `init-db` — 初始化数据库

```bash
python -m jingmai_publish.cli init-db [--root .]
```

创建 `jingmai_agent` 数据库中所有必要的表结构。

---

### 4.3 `run-import` — 导入 Excel 商品数据

```bash
python -m jingmai_publish.cli run-import \
    --excel path/to/products.xlsx \
    --mode draft \                  # draft | publish
    [--store-id STORE001] \
    [--root .]
```

**参数说明：**

| 参数 | 必填 | 说明 |
|------|------|------|
| `--excel` | 是 | Excel 文件路径，必须包含商品标题、型号等列 |
| `--mode` | 否 | `draft`（仅草稿）或 `publish`（发布），默认 `draft` |
| `--store-id` | 否 | 店铺标识，用于多店铺场景隔离 |
| `--root` | 否 | 项目根目录，默认当前目录 |

**Excel 列要求：**

| 列名 | 必填 | 说明 |
|------|------|------|
| 商品标题 | 是 | 发布到京东的商品标题 |
| 型号 | 是 | 商品型号 |
| 品牌 | 否 | 品牌名称，不填则不过滤 |
| 市场价 | 否 | 发布表单中价格字段之一 |
| 京东价 | 否 | 发布表单中价格字段之一 |
| 采购价 | 否 | 发布表单中价格字段之一 |
| 主图路径 | 否 | 本地主图文件路径 |
| 透图路径 | 否 | 本地透图文件路径 |
| 详情内容 | 否 | 详情编辑器的内容 |
| 销售单位 | 否 | T7 物流字段 |
| 商品包装 | 否 | T7 物流字段 |

---

### 4.4 `run-draft-e2e` — 全流程端到端

从 Excel 读取一条商品数据，执行完整的 T1→T8 流程保存为草稿。

```bash
python -m jingmai_publish.cli run-draft-e2e \
    --excel path/to/products.xlsx \
    --item-index 0 \                      # 商品索引（0-based）
    --main-image-path ./images/main.jpg \
    --transparent-image-path ./images/transparent.png \
    [--required-attr "打火线"] \
    [--current "10A"] \
    [--factory-inventory "100"] \
    [--detail-content "<p>商品详情HTML</p>"] \
    [--detail-content-file ./detail.html] \
    [--rated-voltage "220V"] \
    [--cable-length "1.5m"] \
    [--sale-unit "件"] \
    [--package-type "普通商品"] \
    [--delivery-mark "普通品"] \
    [--package-list "主机,说明书,保修卡"] \
    [--warranty-period "365"] \
    [--debug] \
    [--window-keyword "京麦"] [--window-keyword "Jingmai"] \
    [--root .]
```

**关键参数：**

| 参数 | 必填 | 默认 | 说明 |
|------|------|------|------|
| `--excel` | 是 | - | Excel 路径 |
| `--item-index` | 否 | 0 | 要处理的第几条商品 |
| `--main-image-path` | 是 | - | 主图本地路径（≥480x480 方图） |
| `--transparent-image-path` | 是 | - | 透图本地路径 |
| `--required-attr` | 否 | - | T4 必填属性值（如不提供则自动尝试候选值） |
| `--detail-content` | 否 | - | 详情 HTML 内容 |
| `--detail-content-file` | 否 | - | 详情 HTML 文件路径（内容过长时推荐） |
| `--window-keyword` | 否 | 京麦, Jingmai | 窗口标题匹配关键词 |
| `--debug` | 否 | false | 启用调试输出 |

---

### 4.5 `run-desktop-check` — 单步探针

逐步验证每个环节，适合调试和分步骤测试。支持 24 个子步骤。

```bash
# 运行全部步骤（T1+T2）
python -m jingmai_publish.cli run-desktop-check --step both

# 只运行 T1（窗口接管）
python -m jingmai_publish.cli run-desktop-check --step t1

# 只运行 T4（基础信息填充）
python -m jingmai_publish.cli run-desktop-check \
    --step t4 \
    --title "我的商品标题" \
    --model "ABC-123" \
    --required-attr "打火线" \
    --brand "某品牌"

# 运行 T5 SKU 信息探针
python -m jingmai_publish.cli run-desktop-check \
    --step t5-probe

# 运行 T6 主图上传
python -m jingmai_publish.cli run-desktop-check \
    --step t6-main-image \
    --image-path ./images/main.jpg

# 运行 T8 发布
python -m jingmai_publish.cli run-desktop-check \
    --step t8-publish-product
```

**完整的 `--step` 可选值（共 24 个）：**

| 步骤 | 说明 | 需要参数 |
|------|------|----------|
| `t1` | 窗口接管 | 无 |
| `t2` | 进入发布入口 | 无 |
| `t3` | 确认商品类目 | 无 |
| `t4` | 基础信息填充 | `--title`, `--model`, `--required-attr`, `--brand` |
| `t4-extra` | 扩展必填项填充 | `--rated-voltage`, `--cable-length` |
| `t4-option-probe` | T4 品牌/电压/长度可选值探测 | 无 |
| `t5-probe` | SKU 单元格全量探测 | 无 |
| `t5-input-probe` | SKU 单格输入验证 | `--sku-cell-id`, `--sku-value`, `--sku-submit` |
| `t5-row-probe` | SKU 首行批量输入 | `--sku-name`, `--market-price`, `--jd-price` |
| `t5-market-probe` | 市场价字段定位验证 | `--market-price` |
| `t5-first-row` | SKU 首行完整输入+校验 | `--sku-name`, `--market-price`, `--purchase-price`, `--jd-price` |
| `t5-required-fields` | SKU 必填字段填充 | 价格/电流/重量/尺寸/厂直库存等 |
| `t5-dimension-probe` | 重量/尺寸字段填充 | `--weight`, `--length-mm`, `--width-mm`, `--height-mm` |
| `t5-weight-probe` | 重量字段多格式验证 | `--weight` |
| `t6-probe` | 图片/详情编辑器入口检测 | 无 |
| `t6-dialog-probe` | 上传对话框流程验证 | `--image-path` |
| `t6-main-image` | 主图上传 | `--image-path` |
| `t6-transparent-image` | 透图上传 | `--transparent-image-path` 或 `--image-path` |
| `t6-detail-editor` | 详情编辑器填充 | `--detail-content`/`--detail-html`/`--detail-content-file`/`--jd-item-url` |
| `t7` | 物流信息填写 | `--sale-unit`, `--package-type`, `--delivery-mark`, `--package-list`, `--warranty-period` |
| `t8-probe` | 保存/发布按钮检测 | 无 |
| `t8-save-draft` | 保存草稿 | 无 |
| `t8-publish-product` | 发布商品 | 无 |
| `both` | T1+T2 一起执行 | 无 |

**通用参数（所有步骤可用）：**

| 参数 | 说明 |
|------|------|
| `--debug` | 输出详细调试信息 |
| `--window-keyword "xxx"` | 窗口标题匹配关键词（可多次使用） |
| `--preferred-class "Button"` | 控件类优先级（可多次使用） |
| `--click-alias "目标文本=别名1,别名2"` | 点击文本别名映射 |

---

### 4.6 `run-local-path-task` — 本地路径消息触发

```bash
python -m jingmai_publish.cli run-local-path-task \
    --path-file path/to/message.json \
    --mode draft \
    [--store-id STORE001] \
    [--source-channel local_path_message] \
    [--root .]
```

用于从 JSON 消息文件读取 Excel 路径并自动触发上架任务。消息文件格式：

```json
{
    "excel_path": "C:/data/products.xlsx",
    "store_id": "STORE001"
}
```

---

### 4.7 `run-feishu-path-task` — 飞书事件触发

```bash
python -m jingmai_publish.cli run-feishu-path-task \
    --payload-file path/to/feishu_event.json \
    --mode draft \
    [--store-id STORE001] \
    [--root .]
```

接收飞书事件 payload，解析其中的 Excel 文件消息，触发上架任务。

---

### 4.8 `cleanup-runtime-logs` — 日志清理

```bash
python -m jingmai_publish.cli cleanup-runtime-logs [--root .]
```

清理超过保留期限的运行时日志和截图文件（默认保留 3 天）。

---

## 5. T1-T8 发布流程详解

### 5.1 流程概览

```
T1  ──→ T2 ──→ T3 ──→ T4 ──→ T5 ──→ T6 ──→ T7 ──→ T8
│         │       │       │       │       │       │       │
窗口     进入    确认   基础     SKU    图片+   物流    草稿/
接管     发布    类目   信息    信息    详情    信息    发布
```

### 5.2 各步骤详情

#### T1 — 窗口接管

- 自动搜索标题含 "京麦" 或 "Jingmai" 的窗口
- 通过 `pywinauto` 建立 UIA 连接
- 捕获当前窗口截屏
- **输出**：`window_handle`（后续所有步骤使用）

#### T2 — 进入发布入口

- 在窗口中点击 "发布商品" 文本
- **输出**：进入商品发布工作台

#### T3 — 确认商品类目

- 检测当前页面状态（草稿列表 / 类目选择页 / 发布表单）
- 若在草稿列表：点击 "发布商品" 按钮进入
- 若在类目选择页：
  - 优先点击 "近期使用类目" 中的匹配项
  - 自动选择预设类目（工业品 > 电料辅件 > 电气辅材 > 电气配件）
  - 点击 "下一步" 进入发布表单
- **输出**：进入发布表单页面

#### T4 — 基础信息填充

- **必填项**：
  - 商品标题（通过 Label/AutomationId 定位）
  - 型号
  - 品牌（下拉选择，支持候选值匹配）
  - 必填属性（类型下拉，自动尝试多个候选值）
- **扩展项**（`t4-extra`）：
  - 额定电压（下拉）
  - 电缆长度（下拉）

#### T5 — SKU 信息填写

- **市场价 / 京东价 / 采购价**：通过 Label 定位输入框填充
- **电流 / 厂直库存**：同上
- **重量 / 长 / 宽 / 高**：在物流页签中填充
- **特殊处理**：
  - `automation_id` 动态解析（匹配 SKU 控件区域的实际 ID）
  - 市场价字段自动探测多个候选位置
  - 重量支持多格式变体（小数点、逗号、全角句点）
  - 输入后读取 document text 校验是否写入成功

#### T6 — 图片与详情

**图片上传**（主图和透图分两个独立步骤）：
1. 定位图片上传槽位（检测空槽/已填充槽）
2. 悬停触发 "本地上传" 入口
3. 在文件对话框中：Alt+D → 输入目录 → 回车导航 → 文件名 → 打开
4. 确认选择（图片管理弹层中点击 "确定"）
5. 轮询等待槽位内容更新

**详情编辑器**：
- 切换到 "商品描述" → 点击 "代码编辑"
- 将 HTML 内容键入编辑器
- 校验内容是否可见
- 支持多种内容来源：
  - `--detail-content`：直接传入 HTML
  - `--detail-content-file`：从文件读取
  - `--jd-item-url`：从京东商品页抓取图文

**图片要求**：
- 格式：JPG / PNG
- 最小尺寸：480x480
- 方图：宽高必须一致

#### T7 — 物流信息

- 销售单位（下拉）
- 商品包装（下拉）
- 特殊发货时效标记（下拉）
- 包装清单（文本输入）
- 质保期（下拉，自动匹配枚举值）
- 保质期（天）（文本输入）

智能处理：如果类目不支持的选项值，自动 Fallback 到页面实际可选的选项。

#### T8 — 保存草稿 / 发布

- **保存草稿**：
  - 点击 "保存草稿"
  - 处理保存发品模板弹层（若出现，在特定区域再次点击 "保存草稿"）
  - 轮询页面变化确认保存成功
- **发布商品**：
  - 点击 "发布商品"
  - 处理 "继续发布" / "确认发布" 确认弹层
  - 检测审核态文案确认提交成功

---

## 6. 教学指南（快速上手）

### 6.1 第一次运行（5 分钟）

**Step 1：确保京麦桌面端已打开并登录**

京麦桌面端窗口标题应包含 "京麦" 或 "Jingmai"。

**Step 2：初始化数据库**

```bash
python -m jingmai_publish.cli init-db
```

**Step 3：测试窗口接管**

```bash
python -m jingmai_publish.cli run-desktop-check --step t1
```

预期输出类似：
```json
{
    "t1": {
        "step_id": "T1",
        "success": true,
        "page_state": "jingmai_home",
        "message": "已接管京麦窗口: 京麦工作台"
    }
}
```

**Step 4：测试进入发布入口**

```bash
python -m jingmai_publish.cli run-desktop-check --step t2
```

**Step 5：测试基础信息填充**

```bash
python -m jingmai_publish.cli run-desktop-check \
    --step t4 \
    --title "测试商品" \
    --model "TEST-001" \
    --required-attr "打火线"
```

### 6.2 完整草稿流程（10 分钟）

准备一张 800x800 的主图和透图，一条商品数据：

```bash
python -m jingmai_publish.cli run-draft-e2e \
    --excel ./商品导入模板.xlsx \
    --item-index 0 \
    --main-image-path ./images/main.jpg \
    --transparent-image-path ./images/transparent.png \
    --required-attr "固定座" \
    --current "16A" \
    --factory-inventory "500" \
    --detail-content-file ./detail.html \
    --warranty-period "365" \
    --debug
```

### 6.3 Excel 导入模板

创建一个 `商品导入模板.xlsx`，包含以下列：

| A | B | C | D | E | F | G | H |
|---|---|---|---|---|---|---|---|
| 商品标题 | 型号 | 品牌 | 市场价 | 京东价 | 采购价 | 主图路径 | 透图路径 |
| 智能插座Pro | SP-001 | 某品牌 | 99.00 | 89.00 | 65.00 | C:\images\sp001.jpg | C:\images\sp001_t.png |

### 6.4 调试技巧

#### 按步骤调试

当某个步骤失败时，单独运行该步骤：

```bash
# 只调试 T5 必填字段
python -m jingmai_publish.cli run-desktop-check \
    --step t5-required-fields \
    --market-price "99.00" \
    --jd-price "89.00" \
    --purchase-price "65.00" \
    --current "16A" \
    --weight "0.5" \
    --factory-inventory "500" \
    --debug
```

#### 使用探针（Probe）步骤

探针步骤不执行实际操作，只检测当前页面状态和控制元素：

```bash
# 检测 T5 SKU 区域有哪些控件
python -m jingmai_publish.cli run-desktop-check --step t5-probe

# 检测品牌/电压/长度有哪些可选值
python -m jingmai_publish.cli run-desktop-check --step t4-option-probe

# 检测图片上传区域状态
python -m jingmai_publish.cli run-desktop-check --step t6-probe

# 检测保存/发布按钮是否可见
python -m jingmai_publish.cli run-desktop-check --step t8-probe
```

#### 窗口匹配问题

如果找不到京麦窗口，使用 `--window-keyword` 指定：

```bash
python -m jingmai_publish.cli run-desktop-check \
    --step t1 \
    --window-keyword "京麦工作台" \
    --window-keyword "Jingmai Workbench"
```

#### 点击别名

如果京麦按钮文本与预期不符，使用别名映射：

```bash
python -m jingmai_publish.cli run-desktop-check \
    --step t2 \
    --click-alias "发布商品=我要发布,发新品"
```

---

## 7. 常见问题

### Q1: `window_handle is None` 或找不到京麦窗口

**原因**：京麦桌面端未打开，或窗口标题与默认关键词不匹配。

**解决**：
```bash
# 先用 --debug 看有哪些窗口
python -m jingmai_publish.cli run-desktop-check --step t1 --debug

# 指定准确的窗口关键词
python -m jingmai_publish.cli run-desktop-check --step t1 --window-keyword "你的京麦窗口标题"
```

### Q2: T4 品牌/必填属性填充失败

**原因**：京麦下拉选项与传入的值不匹配（品牌名称格式问题，或必填属性不在候选列表中）。

**解决**：
- 先用 `--step t4-option-probe` 查看可用的品牌和属性选项
- 对于必填属性，系统已内置候选列表（打火线、零火、固定座、台架等），会依次尝试
- 品牌建议使用 "品牌名-中文名" 格式（如 "Siemens-西门子"）

### Q3: T6 图片上传失败

**常见原因**：
1. 图片尺寸不符合要求（< 480px 或非正方形）
2. 文件对话框未及时响应

**解决**：
- 确保图片 ≥ 480x480 且宽高相等
- 如果文件对话框导航失败，手动打开图片选择弹层，再运行 T6 步骤
- 检查屏幕分辨率，确保窗口不被遮挡

### Q4: 详情编辑器内容未写入

**原因**：代码编辑器未正确激活，或焦点未在编辑器内。

**解决**：
- 确保详情内容不以 "BL-088-3" 开头（这是探针标记，系统会拒绝）
- 内容超长时会自动截断到 90000 字符
- 先运行 `--step t6-probe` 确认编辑器入口是否可见

### Q5: T8 保存草稿后页面回退到空白表单

**原因**：京麦保存草稿后会打开一个空白的发布表单。

**解决**：这是京麦的正常行为。系统的反射机制会识别此状态并标记为成功。

### Q6: 数据库连接失败

```bash
# 确认 MySQL 服务运行中
# 检查 .env 中的连接参数
MYSQL_HOST=127.0.0.1  # 不是 localhost（pywinauto 环境下 localhost 可能解析异常）
MYSQL_PASSWORD=your_password
```

---

## 8. 开发指南

### 8.1 项目结构

```
jingmai-product-publish-v2/
├── jingmai_publish/           # 主包
│   ├── agent/                 # Agent 决策层（BL-091）
│   │   ├── __init__.py
│   │   ├── types.py           # ActionStep, Plan, ReflectionDecision
│   │   ├── registry.py        # 24 个 ActionStep 定义
│   │   ├── planner.py         # 步骤规划器（拓扑排序）
│   │   ├── executor.py        # 步骤执行器（getattr 反射调用）
│   │   ├── reflection.py      # 反思决策器
│   │   └── pipeline.py        # Planner→Executor→Reflection 管线
│   ├── runtime/               # 运行时（BL-100/BL-101）
│   │   ├── kernel.py          # HostRuntime（observe→decide→act→verify）
│   │   ├── event_loop.py      # RuntimeEventLoop
│   │   ├── manifest.py        # ProviderManifest
│   │   └── providers.py       # ProviderRegistry
│   ├── desktop/               # 桌面自动化层
│   │   ├── uia_adapter.py     # UIA 适配器（核心）
│   │   ├── window_manager.py  # 窗口管理器
│   │   └── ...
│   ├── services/              # 服务层
│   │   ├── desktop_verify.py  # 桌面验证服务
│   │   ├── draft_e2e.py       # 端到端草稿编排
│   │   ├── jingmai_workflow.py # T1-T8 工作流实现
│   │   ├── task_runner.py     # 任务执行器
│   │   ├── import_pipeline.py # Excel 导入流水线
│   │   ├── jd_fetch.py        # 京东商品详情抓取
│   │   └── ...
│   ├── db/                    # 数据库层
│   ├── repositories/          # 数据仓库层
│   ├── bootstrap.py           # 数据库初始化
│   ├── cli.py                 # CLI 入口（7 个命令）
│   └── config.py              # 配置加载（.env）
├── tests/                     # 测试（216 用例）
│   ├── test_cli.py
│   ├── test_desktop_verify.py
│   ├── test_agent_*.py        # Agent 层单元测试
│   └── ...
├── requirements.txt
├── .env                       # 环境配置（不提交到 Git）
└── README.md
```

### 8.2 运行测试

```bash
# 全量测试
python -m pytest tests/ -v

# 只跑 Agent 层测试
python -m pytest tests/test_agent_*.py -v

# 只跑指定文件
python -m pytest tests/test_agent_pipeline.py -v

# 带覆盖率
python -m pytest tests/ --cov=jingmai_publish --cov-report=html
```

### 8.3 添加新的工作流步骤

1. 在 `jingmai_workflow.py` 中添加方法（如 `run_t9_xxx`）
2. 在 `agent/registry.py` 的 `REGISTRY_ENTRIES` 中添加 `ActionStep` 定义
3. 在 `cli.py` 的 `DESKTOP_STEPS` 列表中添加步骤名
4. 添加相应的 CLI 参数（如需要）
5. 在 `tests/` 中添加对应的测试用例

### 8.4 关键设计决策

| 决策 | 理由 |
|------|------|
| 不使用京麦 API | 京麦桌面端无开放 API，UIA 是唯一可用通道 |
| `getattr` 反射调度 | 替代硬编码 if/elif 链，24 个步骤只需注册 ActionStep |
| StepValidationError 继承 ValueError | 区分参数校验错误（应传播）和运行时错误（应包装） |
| Agent 管线可插拔 | 预留 LLM/Vision Provider 扩展点 |
| 截图驱动的验证 | 每步自动截图，便于人工回溯问题 |

---

## 许可证

MIT License

---

**最后更新**：2026-05-17  
**版本**：v2.0.0（Agent 决策层 BL-091）  
**测试状态**：216 passed, 0 failed
