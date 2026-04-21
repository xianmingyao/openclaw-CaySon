---
name: desktop-control
description: |
  desktop-control 是 Windows 桌面自动化 CLI 工具,提供 UFO 桌面操作、Evolution 进化引擎、Browser Bridge 浏览器自动化和 MCP 服务器四大核心功能。

  **核心能力**:
  - UFO 桌面自动化(20种可执行动作)
  - Evolution 进化引擎(技能生成与自适应学习)
  - Browser Bridge(基于 CDP 的浏览器自动化)
  - MCP 服务器(标准化工具接口)

  **何时使用**:
  - 用户询问 desktop-control 项目的安装、配置、使用方法
  - 用户需要桌面自动化、浏览器自动化的解决方案
  - 用户遇到 desktop-control 相关错误需要排查

  **触发词**:
  - desktop-control / 桌面控制
  - 桌面自动化 / Windows自动化
  - UFO操作 / 桌面操作
  - Evolution引擎 / 进化引擎
  - BrowserBridge / 浏览器自动化
  - MCP服务器
  - 技能生成 / Skill Generator
  - 京麦上架 / agents publish

  **技能类型**: 项目文档型(提供使用指导、流程化操作、故障排查)
  **适用平台**: Windows 10/11 (Python 3.11+)
  **项目地址**: E:\workspace\skills\desktop-control-cli

version: 2.1.0
last_updated: 2026-04-21
---

# desktop-control - Windows 桌面自动化 CLI 工具

**描述:** 基于 OpenHarmony v4.0 融合架构的 Windows 桌面自动化框架

## 使用流程

desktop-control 是文档指导型技能,提供流程化使用指导。根据您的自动化需求,选择合适的使用方式:

### 📋 快速导航

| 如果您... | 跳转到 | 操作时间 |
|----------|-------|---------|
| **第一次使用** | Phase 1 | 5分钟 |
| **已安装,选择功能** | Phase 2 | 1分钟 |
| **准备执行任务** | Phase 3 | 按需 |
| **遇到错误** | Phase 2.5 + 附录 | 按需 |
| **查看完整场景** | 完整业务场景 | 10分钟 |

### 整体流程图

```
┌─────────────────────────────────────────────────────────────┐
│                    desktop-control 使用流程                   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
            ┌──────────────────────────────┐
            │   Phase 1: 环境准备（首次）    │
            │   • 安装依赖                │
            │   • 初始化数据库              │
            │   • 验证安装                │
            └──────────────────────────────┘
                           │
                           ▼
            ✅ 检查点：确认看到3条测试技能
                           │
                           ▼
            ┌──────────────────────────────┐
            │   Phase 2: 选择使用方式       │
            │   • 桌面自动化 (UFO)         │
            │   • 浏览器自动化 (Bridge)    │
            │   • 智能技能生成 (Evolution) │
            └──────────────────────────────┘
                           │
                           ▼
            🤔 检查点：选择您的自动化场景
                           │
                           ▼
            ┌──────────────────────────────┐
            │   Phase 2.5: 边界条件（可选）│
            │   • 预防性检查表             │
            │   • Fallback 策略           │
            │   • 恢复流程                │
            └──────────────────────────────┘
                           │
                           ▼
            ┌──────────────────────────────┐
            │   Phase 3: 执行自动化任务     │
            │   • 基本命令示例             │
            │   • 完整业务场景             │
            └──────────────────────────────┘
                           │
                           ▼
                    🎉 完成自动化任务
```

---

## Phase 1: 环境准备

**🎯 适用人群**: 第一次使用 desktop-control 的用户

**⏱️ 预计时间**: 5分钟

**首次使用必须完成以下步骤:**

1. **安装 uv**(如果还没有)
   ```bash
   # Windows (PowerShell)
   irm https://astral.sh/uv/install.ps1 | iex
   
   # 或使用 curl
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
   **为什么使用 uv?**
   - ⚡ 更快的依赖解析和安装速度
   - 🔒 锁定依赖版本,确保可重现构建
   - 🔄 自动管理虚拟环境,无需手动创建
   - 📦 统一管理开发依赖和生产依赖

2. **安装依赖**(使用 uv)
   ```bash
   cd E:\workspace\skills\desktop-control-cli
   uv sync
   ```

3. **初始化数据库**(必需!)
   ```bash
   python init_db_simple.py
   ```
   **注意**: 这是首次使用时的必需步骤,否则技能列表将为空

4. **验证安装**
   ```bash
   uv run python cli.py info
   uv run python cli.py evolution list-skills
   ```

✅ **检查点**: 确认看到 3 条测试技能输出后,再继续 Phase 2。

---

## Phase 2: 选择使用方式

**🎯 适用人群**: 已完成 Phase 1 环境准备的用户

**⏱️ 预计时间**: 1分钟

**目标**: 根据您的自动化场景,选择合适的功能模块

### 功能模块对照表

| 场景 | 推荐模块 | 关键命令 |
|------|---------|---------|
| **桌面操作自动化**(点击、输入、截图) | UFO 桌面自动化 | `ufo mouse click`, `ufo keyboard type`, `ufo system screenshot` |
| **浏览器自动化**(网页操作、数据抓取) | Browser Bridge | `bridge create`, `bridge navigate`, `bridge execute`, `bridge screenshot` |
| **智能技能生成**(从错误学习、录制流程) | Evolution 进化引擎 | `evolution analyze`, `evolution generate`, `evolution execute` |
| **多Agent协同**(复杂任务自动化) | Agents 系统 | `agents publish`, `agents vision identify`, `agents vision explore` |
| **标准化工具接口** | MCP 服务器 | `mcp start`, `mcp list-tools` |

💡 **提示**: 您也可以组合使用多个模块,例如用 Evolution 录制一个包含 Bridge 操作的完整流程。

### 决策树

```
您的自动化目标是什么?
│
├─ 需要操作桌面应用(点击按钮、输入文本)
│  └─ → 使用 UFO 桌面自动化
│     命令示例：ufo mouse click, ufo keyboard type
│
├─ 需要操作网页(打开网址、填写表单、点击元素)
│  └─ → 使用 Bridge 浏览器自动化
│     命令示例：bridge create, bridge navigate, bridge execute
│
├─ 需要从错误中学习/录制流程
│  └─ → 使用 Evolution 进化引擎
│     命令示例：evolution analyze, evolution generate, evolution execute
│
├─ 需要视觉识别界面元素
│  └─ → 使用 Agents Vision 系统
│     命令示例：agents vision identify, agents vision explore
│
└─ 不确定需要什么
   └─ → 运行 `uv run python cli.py info` 查看所有功能
```

🤔 **检查点 2**: 请根据您的自动化需求选择合适的功能模块

---

## Phase 2.5: 边界条件与 Fallback 策略

⚠️ **检查点 3(可选)**: 在执行自动化任务前,建议您了解边界条件和 Fallback 策略。

### 快速检查(30秒内完成)

- [ ] 数据库已初始化(`uv run python cli.py evolution list-skills` 有输出)
- [ ] 目标应用/页面存在(手动确认可访问)
- [ ] 有管理员权限(UFO 操作需要)

💡 **如果以上任何一项不通过**,请参考以下 Fallback 策略。

### 通用预防性检查表

执行任何自动化任务前,请确认:

| 检查项 | 验证方法 | 失败后果 |
|-------|---------|---------|
| **数据库已初始化** | `uv run python cli.py evolution list-skills` 看到技能列表 | Evolution 功能不可用 |
| **目标应用/页面存在** | 手动确认目标可访问 | UFO 操作点击空位置 / Bridge 导航失败 |
| **管理员权限** | 右键"以管理员身份运行" | UFO 操作可能失败 |
| **网络连接** | `ping google.com` | Bridge 操作超时 |
| **磁盘空间** | `dir` 检查剩余空间 | 截图/日志保存失败 |
| **端口可用** | `netstat -ano \| findstr :9222` | Bridge 会话创建失败 |

### 模块级 Fallback 策略

#### 1. UFO 桌面自动化 Fallback

| 场景 | 主方案 | Fallback 方案 |
|------|-------|--------------|
| **坐标点击失败** | `ufo mouse click 100 200` | 1. 使用 `ufo system wait 0.5` 等待后重试<br>2. 使用 Evolution FIX 模式生成修正技能 |
| **元素不存在** | 指定固定坐标 | 1. 使用 `ufo system get-text` 先验证元素<br>2. 录制流程生成 CAPTURED 技能 |
| **输入乱码** | `ufo keyboard type "文本"` | 1. 添加 `--interval 0.1` 参数减慢输入<br>2. 使用 `ufo keyboard press` 逐字符输入 |
| **权限不足** | 直接操作 | 以管理员身份运行 CLI |

**恢复命令:**
```bash
# 启用详细日志诊断
uv run python cli.py --verbose ufo mouse click 100 200

# 检查 UFO 健康状态
uv run python cli.py ufo health
```

#### 2. Bridge 浏览器自动化 Fallback

| 场景 | 主方案 | Fallback 方案 |
|------|-------|--------------|
| **浏览器启动失败** | `bridge create --browser-type chrome` | 系统自动回退到 Edge/Chromium(默认启用)<br>禁用回退：`--no-auto-fallback` |
| **页面加载超时** | `bridge navigate session_123 <url>` | 1. 增加 `--timeout 60000`(60秒)<br>2. 使用 `--wait networkidle0` 等待网络空闲<br>3. 分步导航：先到主站,再到目标页 |
| **脚本执行失败** | `bridge execute session_123 "script"` | 1. 检查语法：先用简化脚本测试<br>2. 添加 `--await-promise` 等待异步<br>3. 使用 `try-catch` 包裹脚本 |
| **会话断开** | 执行命令报错 | 1. `bridge list` 检查会话状态<br>2. `bridge create` 创建新会话 |

**恢复命令:**
```bash
# 检查 Bridge 服务状态
uv run python cli.py bridge health

# 查看活动会话
uv run python cli.py bridge list

# 强制关闭并重建会话
uv run python cli.py bridge close session_123
uv run python cli.py bridge create --browser-type edge
```

#### 3. Evolution 进化引擎 Fallback

| 场景 | 主方案 | Fallback 方案 |
|------|-------|--------------|
| **技能执行失败** | `evolution execute --skill skill_name` | 1. 使用 `evolution analyze --execution-id <id>` 分析失败<br>2. 运行 `evolution generate --name fixed_skill --type FIX` 生成修复版<br>3. 手动编辑技能参数后重试 |
| **分析无结果** | `evolution analyze --execution-id exec_001` | 1. 检查 execution-id 是否存在<br>2. 使用 `--error-type` 和 `--error-message` 手动指定错误 |
| **技能列表为空** | `evolution list-skills` | 运行 `python init_db_simple.py` 初始化数据库 |

**恢复流程:**
```bash
# Step 1: 分析失败原因
uv run python cli.py evolution analyze --execution-id exec_001 --tool-name ufo_click --error-type timeout

# Step 2: 生成修复技能
uv run python cli.py evolution generate --name ufo_click_fixed --type FIX

# Step 3: 执行修复技能
uv run python cli.py evolution execute --skill ufo_click_fixed
```

#### 通用恢复流程

当自动化任务失败时,按以下流程排查:

```
1. 启用详细日志
   └─ uv run python cli.py --verbose [MODULE] [COMMAND]

2. 检查服务健康状态
   ├─ uv run python cli.py ufo health
   ├─ uv run python cli.py bridge health
   └─ uv run python cli.py evolution health

3. 查看具体错误信息
   └─ 对照"常见错误和解决方案"章节

4. 尝试 Fallback 方案
   ├─ UFO: 添加等待时间、修正坐标、使用 FIX 模式
   ├─ Bridge: 切换浏览器、增加超时、检查网络
   └─ Evolution: 分析失败、生成修复技能、重试

5. 记录问题
   └─ 将错误信息和新解决方案记录到文档
```

### 检查点失败处理流程

**检查点 1(Phase 1 完成)失败:**
```
症状: `uv run python cli.py evolution list-skills` 报错或输出为空
├─ 原因: 数据库未初始化
├─ 解决: 运行 `python init_db_simple.py`
└─ 验证: 重新运行 list-skills 确认看到3条测试技能
```

**检查点 2(Phase 2 场景选择)失败:**
```
症状: 不知道选择哪个模块
├─ 原因: 对自动化需求不明确
├─ 解决:
│   1. 运行 `uv run python cli.py info` 查看所有功能
│   2. 阅读"完整业务场景示例"章节了解实际应用
│   3. 从简单场景开始(如先测试 UFO 点击)
└─ 验证: 选择一个模块后,执行示例命令确认可用
```

**检查点 3(Phase 2.5 环境检查)失败:**
```
症状: 快速检查有项目不通过
├─ 原因: 环境未准备好
├─ 解决:
│   1. 数据库未初始化 → 运行 `python init_db_simple.py`
│   2. 目标不存在 → 手动打开目标应用/页面确认可访问
│   3. 权限不足 → 右键"以管理员身份运行"CLI
│   4. 网络问题 → 检查网络连接或使用本地测试
│   5. 端口占用 → 运行 `bridge list` 查看会话,关闭旧会话
└─ 验证: 所有检查项通过后继续 Phase 3
```

💡 **提示**: 大多数检查点失败都可以在 Phase 2-2.5 解决,不需要进入 Phase 3。

---

## Phase 3: 执行自动化任务

**🎯 适用人群**: 已完成 Phase 1-2,准备执行自动化任务的用户

**⏱️ 预计时间**: 按需(从几分钟到几小时不等)

**目标**: 根据 Phase 2 的选择,参考命令参考章节执行具体操作

### 前置条件检查

⚠️ **在执行前,请确认**:
- [ ] 已完成 Phase 1 环境准备(数据库已初始化)
- [ ] 已确认要使用的功能模块(UFO / Bridge / Evolution / Agents)
- [ ] 了解要操作的目标(屏幕坐标 / 网页URL / 技能名称)

### 快速导航

- **只想测试基本命令** → 查看"快速命令索引"或引用 [COMMANDS.md](docs/COMMANDS.md)
- **需要完整业务场景** → 查看"完整业务场景示例"(京麦上架)
- **遇到问题** → 查看"异常处理"或引用 [COMMANDS.md](docs/COMMANDS.md) 的错误处理章节

### 典型使用流程示例

#### 示例1: UFO 桌面自动化

```bash
# 1. 点击屏幕位置
uv run python cli.py ufo mouse click 100 200

# 2. 输入文本
uv run python cli.py ufo keyboard type "Hello, World!"

# 3. 截图保存
uv run python cli.py ufo system screenshot --path result.png
```

#### 示例2: Bridge 浏览器自动化

```bash
# 1. 创建会话
uv run python cli.py bridge create --window-size 1920,1080
# 输出: 会话ID: session_abc123

# 2. 导航到页面
uv run python cli.py bridge navigate session_abc123 https://example.com

# 3. 执行脚本
uv run python cli.py bridge execute session_abc123 "document.title"

# 4. 截图
uv run python cli.py bridge screenshot session_abc123 output.png
```

#### 示例3: Evolution 技能生成

```bash
# 1. 分析执行结果
uv run python cli.py evolution analyze --execution-id exec_001

# 2. 生成进化技能
uv run python cli.py evolution generate --name auto_login --type FIX

# 3. 执行技能
uv run python cli.py evolution execute --skill auto_login
```

#### 示例4: Agents 多Agent系统

```bash
# 1. 批量识别界面元素
uv run python cli.py agents vision identify "商品管理,订单管理,库存管理" --context jingmai

# 2. 交互式探索界面
uv run python cli.py agents vision explore --context jingmai

# 3. 执行京麦上架任务
uv run python cli.py agents publish "iPhone 15 Pro Max" --category "手机通讯" --price 9999 --images "img1.jpg,img2.jpg"
```

---

## 完整业务场景示例:京麦商品上架自动化

以下是一个完整的京麦商家后台商品上架自动化流程,展示如何组合使用 UFO、Bridge 和 Agents。

### 场景描述

在京麦商家后台自动上架商品,流程包括:
1. 打开浏览器登录京麦
2. 点击"商品"→"发布商品"
3. 选择类目并填写商品信息
4. 上传商品图片
5. 点击发布按钮

### 完整脚本

```bash
#!/bin/bash
# 京麦商品上架自动化脚本

# ============================================
# 第一步：初始化环境
# ============================================
echo "=== 京麦上架自动化开始 ==="

# 1. 检查数据库状态
uv run python cli.py evolution list-skills
# 预期：看到至少 3 条测试技能

# 2. 检查 Bridge 服务状态
uv run python cli.py bridge health
# 预期：🟢 服务状态: healthy

# ============================================
# 第二步：创建浏览器会话
# ============================================
echo "--- 创建浏览器会话 ---"

# 创建会话(使用 Edge 浏览器,显示窗口)
uv run python cli.py bridge create --browser-type edge --no-headless --window-size 1920,1080
# 预期输出会包含：会话ID: session_xxx
# ⚠️ 记录输出的 session_id,后续命令需要使用

# 假设输出的会话ID是 session_jingmai_001
SESSION_ID="session_jingmai_001"

# ============================================
# 第三步：使用视觉识别定位元素
# ============================================
echo "--- 识别界面元素 ---"

# 批量识别关键元素
uv run python cli.py agents vision identify "商品管理,发布商品,类目选择" --context jingmai --screenshot
# 输出包含各元素的坐标位置

# ============================================
# 第四步：执行上架操作
# ============================================
echo "--- 执行上架操作 ---"

# 使用 Agents 系统自动执行上架流程
uv run python cli.py agents publish "iPhone 15 Pro Max 256GB" \
  --category "手机通讯" \
  --price 9999 \
  --images "img1.jpg,img2.jpg,img3.jpg" \
  --description "国行版 iPhone 15 Pro Max 256GB 深空黑色"

# ============================================
# 第五步：截图验证结果
# ============================================
echo "--- 截图验证结果 ---"

uv run python cli.py bridge screenshot $SESSION_ID jingmai_publish_result.png
echo "=== 京麦上架自动化完成 ==="
```

### 脚本执行说明

**前置条件:**
1. 已完成数据库初始化: `python init_db_simple.py`
2. 已准备商品图片: 3张1440*1440的jpg/png图片
3. 已注册京麦账号: 准备好用户名和密码

**执行脚本:**
```bash
# 保存为 jingmai_publish.sh
bash jingmai_publish.sh
```

**如果执行失败:**
1. 查看详细日志: `uv run python cli.py --verbose agents publish ...`
2. 使用 Evolution FIX 模式从错误中学习
3. 使用 vision identify 重新识别元素位置

---

## 快速命令索引

### 环境准备

```bash
# 1. 安装依赖
cd E:\workspace\skills\desktop-control-cli
uv sync

# 2. 初始化数据库(必需!)
python init_db_simple.py

# 3. 验证安装
uv run python cli.py info
uv run python cli.py evolution list-skills
```

### 核心命令

```bash
# UFO 桌面操作
uv run python cli.py ufo mouse click 100 200
uv run python cli.py ufo keyboard type "text"
uv run python cli.py ufo system screenshot --path output.png

# Bridge 浏览器自动化
uv run python cli.py bridge create --window-size 1920,1080
uv run python cli.py bridge navigate session_123 https://example.com
uv run python cli.py bridge execute session_123 "document.title"
uv run python cli.py bridge screenshot session_123 output.png

# Evolution 技能生成
uv run python cli.py evolution analyze --execution-id exec_001
uv run python cli.py evolution generate --name auto_login --type FIX
uv run python cli.py evolution execute --skill auto_login

# Agents 多Agent系统
uv run python cli.py agents publish "商品名称" --category "数码" --price 999
uv run python cli.py agents vision identify "商品管理" --context jingmai
uv run python cli.py agents vision explore --context jingmai
```

**详细命令参数**请参考: [COMMANDS.md](docs/COMMANDS.md)

---

## 异常处理

### 常见错误速查

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `can't open file 'init_db_simple.py'` | 错误的执行目录 | 返回项目根目录执行 |
| `[EMPTY] 没有活动技能` | 数据库未初始化 | 运行 `python init_db_simple.py` |
| `端口已被占用` | Bridge 会话冲突 | `bridge list` 查看并关闭旧会话 |
| `浏览器未找到` | 指定浏览器不可用 | 系统自动回退到 Edge/Chromium |

### 模块级 Fallback 策略

详细的 Fallback 策略请参见上文的 **Phase 2.5: 边界条件与 Fallback 策略** 章节。

---

## 文档引用

### 详细的命令参考

| 需求 | 引用文档 | 说明 |
|------|---------|------|
| **完整 CLI 命令参数** | [COMMANDS.md](docs/COMMANDS.md) | 所有命令的详细参数和示例 |
| **反思闭环流程** | [WORKFLOW.md](docs/WORKFLOW.md) | Plan-Act-Check-Think 流程说明 |
| **系统架构设计** | [ARCHITECTURE.md](docs/ARCHITECTURE.md) | OpenHarmony 融合架构说明 |
| **开发指南** | [DEVELOPMENT.md](docs/DEVELOPMENT.md) | 代码风格、测试、项目结构 |

### 附录参考

#### UFO 20 种可执行动作

| 类别 | 动作 | 命令示例 |
|------|------|----------|
| 鼠标 | 点击 | `ufo mouse click 100 200` |
| 鼠标 | 双击 | `ufo mouse double-click 100 200` |
| 鼠标 | 右击 | `ufo mouse right-click 100 200` |
| 鼠标 | 拖拽 | `ufo mouse drag 100 100 500 500` |
| 鼠标 | 滚动 | `ufo mouse scroll --scroll-y -3` |
| 键盘 | 输入 | `ufo keyboard type "text"` |
| 键盘 | 按键 | `ufo keyboard press enter` |
| 键盘 | 组合键 | `ufo keyboard hotkey ctrl+c` |
| 系统 | 截图 | `ufo system screenshot --path screen.png` |
| 系统 | 等待 | `ufo system wait 1.5` |
| 系统 | 获取文本 | `ufo system get-text --x 100 --y 200` |
| 系统 | 执行命令 | `ufo system execute notepad` |

#### Evolution 进化类型对比

| 类型 | 用途 | 示例 |
|------|------|------|
| **FIX** | 修复进化 | 从点击失败中学习,自动调整坐标或添加等待 |
| **DERIVED** | 衍生进化 | 从"登录"技能衍生出"登录并截图"技能 |
| **CAPTURED** | 捕获进化 | 录制用户操作流程,自动生成可重复执行的技能 |

#### Bridge 支持的浏览器

| 浏览器 | `--browser-type` 值 | 支持状态 |
|--------|-------------------|----------|
| Google Chrome | `chrome` | ✅ 完全支持 |
| Chromium | `chromium` | ✅ 完全支持 |
| Microsoft Edge | `edge` | ✅ 完全支持 |

#### MCP 工具命名规范

```
{模块}_{动作}

示例：
- ufo_click
- ufo_type
- evolution_execute
- bridge_navigate
- bridge_screenshot
```

#### 错误代码参考

| 错误代码 | 说明 | 解决方案 |
|---------|------|----------|
| `E001` | UFO 初始化失败 | 检查管理员权限 |
| `E002` | Bridge 会话创建失败 | 检查浏览器是否已安装 |
| `E003` | Evolution 分析失败 | 检查 execution-id 是否存在 |
| `E004` | MCP 服务器启动失败 | 检查端口是否被占用 |

---

## 检查点验证

✅ **Phase 1 完成**: `uv run python cli.py evolution list-skills` 显示至少 3 条测试技能  
✅ **Phase 2 完成**: 用户明确选择要使用的功能模块  
✅ **Phase 2.5 完成**: 所有快速检查项通过  
✅ **Phase 3 完成**: 用户成功执行目标命令并看到预期输出

---

*基于 Google Agent Skills 五大模式设计*  
*参考: skill-writing-guide.md*
