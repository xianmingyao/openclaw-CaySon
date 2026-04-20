---
name: desktop-control
description: |
  desktop-control 是基于 OpenHarmony v4.0 融合架构的 Windows 桌面自动化 CLI 工具项目文档。

  **核心功能**:
  - UFO 桌面自动化（20种可执行动作）
  - Evolution 进化引擎（技能生成与自适应学习）
  - Browser Bridge（基于 CDP 的浏览器自动化）
  - MCP 服务器（标准化工具接口）

  **何时使用**:
  - 用户询问 desktop-control 项目的安装、配置、使用方法时
  - 用户需要桌面自动化、浏览器自动化的解决方案时
  - 用户遇到 desktop-control 相关错误需要排查时
  - 用户想了解 OpenHarmony 融合架构或技能生成系统时

  **触发词**:
  - desktop-control / 桌面控制
  - 桌面自动化 / Windows自动化
  - UFO操作 / 桌面操作
  - Evolution引擎 / 进化引擎
  - BrowserBridge / 浏览器自动化
  - MCP服务器
  - OpenHarmony / 融合架构
  - 技能生成 / Skill Generator

  **技能类型**: 项目文档型（提供命令参考、配置说明、故障排查等静态信息）

  **适用平台**: Windows 10/11 (Python 3.11+)

  **项目地址**: E:\workspace\skills\desktop-control-cli
version: 1.0.0
last_updated: 2026-04-20
---

# desktop-control - Windows 桌面自动化 CLI 工具

基于 OpenHarmony v4.0 融合架构的 Windows 桌面自动化框架，提供 UFO 桌面操作、Evolution 进化引擎、Browser Bridge 浏览器自动化和 MCP 服务器四大核心功能。

**跨平台:** Windows 10/11 (Python 3.11+)

---

## 环境安装

### 系统要求

- Python 3.11+
- Windows 10/11
- 管理员权限（用于桌面自动化操作）

### 安装依赖

```bash
# 进入项目目录
cd E:\workspace\skills\desktop-control-cli

# 安装依赖
pip install -r requirements.txt

# 或使用 uv（推荐）
pip install uv
uv sync
```

### 初始化数据库（必需！）

```bash
# 在项目根目录运行初始化脚本
python init_db_simple.py
```

**注意：** 这是首次使用时的必需步骤，否则技能列表将为空。

### 验证安装

```bash
# 查看系统信息
python cli.py info

# 查看版本
python cli.py version

# 查看技能列表（验证数据库）
python cli.py evolution list-skills
```

---

## 快速开始（5分钟）

### 第一步：初始化数据库

```bash
# 在项目根目录运行
python init_db_simple.py
```

**预期输出：**
```
✅ 数据库初始化成功
✅ 添加了 3 条测试技能
```

### 第二步：创建浏览器会话

```bash
# 创建基本会话
python cli.py bridge create --window-size 1920,1080
```

**预期输出：**
```
[OK] 会话创建成功
会话ID: session_abc123
CDP URL: ws://localhost:9222/devtools/page/ABC123
浏览器类型: chrome
```

### 第三步：查看技能列表

```bash
# 查看所有可用技能
python cli.py evolution list-skills
```

**预期输出：**
```
[LIST] 可用技能: 3
1. auto_login - 自动登录技能
2. navigate - 页面导航
3. screenshot - 页面截图
```

### 第四步：执行技能

```bash
# 执行登录技能
python cli.py evolution execute --skill auto_login --username admin --password 123456
```

### 第五步：关闭会话

```bash
# 查看所有会话
python cli.py bridge list

# 关闭指定会话
python cli.py bridge close session_abc123
```

---

## 快速开始

### 基本命令结构

```bash
# 主命令格式
python cli.py [MODULE] [COMMAND] [OPTIONS]

# 查看帮助
python cli.py --help
python cli.py [MODULE] --help
```

### 核心功能快速示例

#### 1. UFO 桌面自动化

```bash
# 鼠标点击
python cli.py ufo mouse click 100 200 --button left

# 输入文本
python cli.py ufo keyboard type "Hello, World!"

# 截图
python cli.py ufo system screenshot --path screenshot.png

# 组合键
python cli.py ufo keyboard hotkey ctrl+c
```

#### 2. Evolution 进化引擎

```bash
# 分析执行结果
python cli.py evolution analyze --execution-id exec_001

# 生成进化技能
python cli.py evolution generate --name auto_login --type FIX

# 列出所有技能
python cli.py evolution list-skills
```

#### 3. Browser Bridge

```bash
# 创建浏览器会话
python cli.py bridge create --browser-type chrome --headless

# 导航到URL
python cli.py bridge navigate session_123 https://example.com

# 执行脚本
python cli.py bridge execute session_123 "document.title"

# 截图
python cli.py bridge screenshot session_123 output.png
```

#### 4. MCP 服务器

```bash
# 启动MCP服务器
python cli.py mcp start --verbose

# 列出工具
python cli.py mcp list-tools --count 20

# 查看状态
python cli.py mcp status
```

---

## UFO 命令

UFO（Universal Flying Object）桌面自动化系统提供 20 种可执行动作。

### `ufo mouse` — 鼠标操作组

#### `click` — 点击指定坐标

```bash
# 基本点击
python cli.py ufo mouse click 100 200

# 指定按钮
python cli.py ufo mouse click 100 200 --button right

# 多次点击
python cli.py ufo mouse click 100 200 --clicks 2
```

**参数：**
- `x` — X 坐标（必需）
- `y` — Y 坐标（必需）
- `--button`, `-b` — 鼠标按钮：`left` | `right` | `middle`（默认：left）
- `--clicks`, `-c` — 点击次数（默认：1）

---

#### `double-click` — 双击指定坐标

```bash
python cli.py ufo mouse double-click 100 200 --button left
```

**参数：**
- `x` — X 坐标（必需）
- `y` — Y 坐标（必需）
- `--button`, `-b` — 鼠标按钮（默认：left）

---

#### `right-click` — 右键单击

```bash
python cli.py ufo mouse right-click 100 200
```

**参数：**
- `x` — X 坐标（必需）
- `y` — Y 坐标（必需）

---

#### `drag` — 拖拽操作

```bash
# 从 (100,100) 拖拽到 (500,500)
python cli.py ufo mouse drag 100 100 500 500

# 指定持续时间
python cli.py ufo mouse drag 100 100 500 500 --duration 0.5
```

**参数：**
- `start_x` — 起始 X 坐标（必需）
- `start_y` — 起始 Y 坐标（必需）
- `end_x` — 结束 X 坐标（必需）
- `end_y` — 结束 Y 坐标（必需）
- `--duration`, `-d` — 拖拽持续时间（秒，默认：0.5）

---

#### `scroll` — 滚动鼠标滚轮

```bash
# 垂直滚动（向下）
python cli.py ufo mouse scroll --scroll-y -3

# 水平滚动
python cli.py ufo mouse scroll --scroll-x 5

# 指定位置滚动
python cli.py ufo mouse scroll --x 100 --y 200 --scroll-y -3
```

**参数：**
- `--x` — 鼠标 X 坐标
- `--y` — 鼠标 Y 坐标
- `--scroll-x` — 水平滚动距离（默认：0）
- `--scroll-y` — 垂直滚动距离（默认：-3）

---

### `ufo keyboard` — 键盘操作组

#### `type` — 输入文本

```bash
# 基本输入
python cli.py ufo keyboard type "Hello, World!"

# 带间隔输入
python cli.py ufo keyboard type "text" --interval 0.1
```

**参数：**
- `text` — 要输入的文本（必需）
- `--interval`, `-i` — 输入间隔（秒，默认：0.0）

---

#### `press` — 按下按键

```bash
python cli.py ufo keyboard press enter

# 指定持续时间
python cli.py ufo keyboard press space --duration 0.2
```

**参数：**
- `key` — 按键名称（必需）
- `--duration`, `-d` — 按键持续时间（秒，默认：0.1）

---

#### `hotkey` — 执行组合热键

```bash
python cli.py ufo keyboard hotkey ctrl+c
python cli.py ufo keyboard hotkey ctrl+shift+esc
```

**参数：**
- `hotkey` — 组合键（必需，格式：`ctrl+alt+delete`）

---

### `ufo system` — 系统操作组

#### `screenshot` — 截取屏幕截图

```bash
# 全屏截图
python cli.py ufo system screenshot --path screenshot.png

# 裁剪到活动窗口
python cli.py ufo system screenshot --path window.png --crop-window
```

**参数：**
- `--path`, `-p` — 保存路径
- `--crop-window` — 裁剪到活动窗口

---

#### `wait` — 等待指定时间

```bash
python cli.py ufo system wait 1.5
```

**参数：**
- `seconds` — 等待时间（秒，必需）

---

#### `get-text` — 获取屏幕指定位置的文本

```bash
python cli.py ufo system get-text --x 100 --y 200 --width 200 --height 50
```

**参数：**
- `--x` — X 坐标（必需）
- `--y` — Y 坐标（必需）
- `--width` — 识别区域宽度（默认：100）
- `--height` — 识别区域高度（默认：30）

---

#### `execute` — 执行系统命令

```bash
# 基本执行
python cli.py ufo system execute notepad

# 使用 shell 执行
python cli.py ufo system execute "dir /s" --shell
```

**参数：**
- `command` — 要执行的命令（必需）
- `--shell`, `-s` — 使用 shell 执行

---

### UFO 工具命令

#### `health` — 健康检查

```bash
python cli.py ufo health
```

检查 UFO 系统状态、版本、工具总数等信息。

#### `tools` — 列出所有可用工具

```bash
python cli.py ufo tools
```

显示所有 UFO 工具及其描述。

---

## Evolution 命令

Evolution 进化引擎提供技能进化、自适应学习和错误分析功能。

### `evolution analyze` — 分析执行结果

```bash
# 基本分析
python cli.py evolution analyze --execution-id exec_001

# 带错误信息分析
python cli.py evolution analyze --execution-id exec_001 --tool-name ufo_click --error-type timeout --error-message "Element not found"
```

**参数：**
- `--execution-id` — 执行 ID（必需）
- `--tool-name` — 工具名称
- `--error-type` — 错误类型
- `--error-message` — 错误消息

---

### `evolution generate` — 生成进化技能

```bash
# 生成修复进化技能（使用 --name）
python cli.py evolution generate --name auto_login --type FIX

# 或使用 --tool-name（完全等效）
python cli.py evolution generate --tool-name auto_login --type FIX

# 生成衍生进化技能
python cli.py evolution generate --name enhanced_click --type DERIVED

# 生成捕获进化技能
python cli.py evolution generate --name captured_flow --type CAPTURED

# 使用默认类型（FIX）
python cli.py evolution generate --name auto_login
```

**参数：**
- `--name` / `--tool-name` — 技能名称（必需，两种写法完全等效）
- `--type` — 进化类型：`FIX` | `DERIVED` | `CAPTURED`（默认：FIX）

**进化类型说明：**
- **FIX**：修复进化 - 从错误中学习并修复
- **DERIVED**：衍生进化 - 从现有技能衍生新技能
- **CAPTURED**：捕获进化 - 捕获用户操作流程生成技能

---

### `evolution list-skills` — 列出所有进化技能

```bash
# 列出技能（默认 10 个）
python cli.py evolution list-skills

# 列出更多技能
python cli.py evolution list-skills --limit 20
```

**参数：**
- `--limit` — 返回数量限制（默认：10）

---

### `evolution execute` — 执行进化技能

```bash
# 执行技能
python cli.py evolution execute --skill auto_login

# 带参数执行
python cli.py evolution execute --skill auto_login --username admin --password 123456
```

**参数：**
- `--skill` — 技能名称或 ID（必需）
- `--params` — 技能参数（JSON 格式）

---

### `evolution health` — 健康检查

```bash
python cli.py evolution health
```

检查 Evolution 系统状态。

---

## Bridge 命令

Browser Bridge 提供基于 CDP (Chrome DevTools Protocol) 的浏览器自动化功能。

### 前置条件

在使用 Bridge 命令之前，请确保：

1. **已初始化数据库**
   ```bash
   python init_db_simple.py
   ```

2. **在项目根目录运行命令**
   ```bash
   # 确保当前目录是
   E:\workspace\skills\desktop-control-cli
   ```

3. **系统已安装浏览器**
   - Chrome (推荐)
   - Chromium
   - Microsoft Edge (Windows 自带)

### `bridge create` — 创建新的浏览器会话

**重要提示：**
- ⚠️ 必须在**项目根目录**运行命令，不是在 `desktop-control/` 子目录
- ⚠️ 首次使用前必须运行 `python init_db_simple.py` 初始化数据库
- ⚠️ 如果指定的浏览器不可用，系统会自动回退到可用浏览器

```bash
# 创建基本会话（默认 Chrome 无头模式）
python cli.py bridge create

# 指定浏览器类型
python cli.py bridge create --browser-type chromium

# 显示模式（可以看到浏览器窗口）
python cli.py bridge create --no-headless

# 指定窗口大小
python cli.py bridge create --window-size 1920,1080

# 使用代理
python cli.py bridge create --proxy http://proxy.example.com:8080

# 禁用自动回退（只使用指定浏览器）
python cli.py bridge create --browser-type chromium --no-auto-fallback
```

**参数：**
- `--browser-type`, `-b` — 浏览器类型：`chrome` | `chromium` | `edge`（默认：chrome）
- `--headless/--no-headless` — 无头模式（默认：--headless）
- `--window-size`, `-w` — 窗口大小（格式：WIDTH,HEIGHT）
- `--proxy`, `-p` — 代理服务器

**输出：**
```
✅ 会话创建成功
会话ID: session_abc123
CDP URL: ws://localhost:9222/devtools/page/ABC123
浏览器类型: chrome
用户代理: Mozilla/5.0 ...
```

---

### `bridge close` — 关闭浏览器会话

```bash
python cli.py bridge close session_abc123
```

**参数：**
- `session_id` — 会话 ID（必需）

---

### `bridge info` — 获取会话信息

```bash
python cli.py bridge info session_abc123
```

**参数：**
- `session_id` — 会话 ID（必需）

**输出：**
```
会话ID: session_abc123
浏览器类型: chrome
状态: connected
CDP URL: ws://localhost:9222/devtools/page/ABC123
浏览器PID: 12345
WebSocket端口: 9222
视口大小: 1920x1080
```

---

### `bridge list` — 列出所有会话

```bash
python cli.py bridge list
```

**输出：**
```
📋 活动会话: 2
🟢 session_abc123 - chrome
🟢 session_def456 - edge
```

---

### `bridge navigate` — 导航到指定 URL

```bash
# 基本导航
python cli.py bridge navigate session_abc123 https://example.com

# 指定等待条件
python cli.py bridge navigate session_abc123 https://example.com --wait load

# 指定超时
python cli.py bridge navigate session_abc123 https://example.com --timeout 60000
```

**参数：**
- `session_id` — 会话 ID（必需）
- `url` — 目标 URL（必需）
- `--wait`, `-w` — 等待条件：`load` | `DOMContentLoaded` | `networkidle0` | `networkidle2`（默认：load）
- `--timeout`, `-t` — 超时时间（毫秒，默认：30000）

**输出：**
```
✅ 导航成功
URL: https://example.com
状态: success
加载时间: 1234.56ms
```

---

### `bridge execute` — 执行 JavaScript 脚本

```bash
# 基本执行
python cli.py bridge execute session_123 "document.title"

# 等待 Promise
python cli.py bridge execute session_123 "fetch('/api/data').then(r=>r.json())" --await-promise

# 指定超时
python cli.py bridge execute session_123 "someAsyncFunction()" --await-promise --timeout 60000
```

**参数：**
- `session_id` — 会话 ID（必需）
- `script` — JavaScript 脚本（必需）
- `--await-promise/--no-await-promise` — 等待 Promise（默认：--no-await-promise）
- `--timeout`, `-t` — 超时时间（毫秒，默认：30000）

**输出：**
```
✅ 执行成功
结果: "Example Page Title"
执行时间: 12.34ms
```

---

### `bridge screenshot` — 截取页面截图

```bash
# 视口截图
python cli.py bridge screenshot session_123 output.png

# 完整页面截图
python cli.py bridge screenshot session_123 output.png --full-page
```

**参数：**
- `session_id` — 会话 ID（必需）
- `path` — 保存路径（必需）
- `--full-page/--no-full-page` — 完整页面截图（默认：--no-full-page）

---

### `bridge health` — 健康检查

```bash
python cli.py bridge health
```

**输出：**
```
🟢 服务状态: healthy
服务: BridgeService
版本: 1.0.0
活动会话: 2
WebSocket支持: True
```

---

### `bridge config` — 显示当前配置

```bash
python cli.py bridge config
```

**输出：**
```
📋 Bridge配置:
WebSocket端口: 8765
最大会话数: 10
启用无头模式: True
```

---

## MCP 命令

MCP (Model Context Protocol) 服务器提供标准化的工具接口。

### `mcp start` — 启动 MCP 服务器

```bash
# 基本启动
python cli.py mcp start

# 启用详细日志
python cli.py mcp start --verbose
```

**参数：**
- `--verbose`, `-v` — 启用详细日志

---

### `mcp list-tools` — 列出所有可用工具

```bash
# 列出工具（默认 10 个）
python cli.py mcp list-tools

# 列出更多工具
python cli.py mcp list-tools --count 20
```

**参数：**
- `--count`, `-c` — 最大显示数量（默认：10）

**输出示例：**
```
[TOOLS] 可用工具 (20):
  1. ufo_click
  2. ufo_type
  3. ufo_screenshot
  4. ufo_press
  5. ufo_hotkey
  6. evolution_execute
  7. evolution_status
  8. bridge_navigate
  9. bridge_click
  10. bridge_screenshot
  ...
```

---

### `mcp call-tool` — 测试调用工具

```bash
python cli.py mcp call-tool ufo_click
```

**参数：**
- `tool_name` — 工具名称（必需）

**注意：** 此功能需要完整的 MCP 客户端支持。

---

### `mcp status` — 查看服务器状态

```bash
python cli.py mcp status
```

**输出：**
```
[STATUS] MCP 服务器状态
版本: 1.0.0
MCP 支持: [OK]
```

---

## 全局命令

### `test` — 运行测试

```bash
# 运行所有测试
python cli.py test all

# 运行特定模块测试
python cli.py test ufo
python cli.py test evolution
python cli.py test bridge
python cli.py test mcp
```

**测试路径：**
- `all` — 运行所有单元测试和集成测试
- `ufo` — 运行 UFO 模块测试
- `evolution` — 运行 Evolution 模块测试
- `bridge` — 运行 Bridge 模块测试
- `mcp` — 运行 MCP 模块测试

---

### `info` — 显示系统信息

```bash
python cli.py info
```

**输出：**
```
[INFO] Desktop Control 系统信息

模块状态:
  [DONE] UFO
  [DONE] Evolution
  [DONE] Bridge
  [DONE] MCP

可用模块: 4/4

核心特性:
  - UFO 桌面自动化 (20种动作)
  - Evolution 进化引擎 (FIX/DERIVED/CAPTURED)
  - Skill 生成系统 (7阶段流程)
  - Browser Bridge (CDP 协议)
  - MCP 服务器 (标准化工具接口)
```

---

### `structure` — 显示项目结构

```bash
# 树形结构（默认）
python cli.py structure

# 简单格式
python cli.py structure --format simple
```

**参数：**
- `--format`, `-f` — 输出格式：`tree` | `simple`（默认：tree）

---

### `version` — 显示版本信息

```bash
python cli.py version
```

**输出：**
```
Desktop Control v1.0.0
OpenHarmony v4.0 融合架构
Python 3.11+
(c) 2026 Desktop Control Team
```

---

## 配置

### 全局选项

所有命令都支持以下全局选项：

```bash
# 启用详细日志
python cli.py --verbose ufo mouse click 100 200

# 指定配置文件
python cli.py --config custom_config.json ufo mouse click 100 200

# JSON 格式输出
python cli.py --json ufo mouse click 100 200
```

**全局参数：**
- `--verbose`, `-v` — 启用详细日志
- `--config`, `-c` — 配置文件路径
- `--json` — 以 JSON 格式输出

---

### 环境变量

```bash
# Bridge 配置
export BRIDGE_WEBSOCKET_PORT=8765
export BRIDGE_MAX_SESSIONS=10
export BRIDGE_ENABLE_HEADLESS=true

# 日志配置
export LOG_LEVEL=INFO
export LOG_FILE=./logs/desktop-control.log
```

---

## 架构设计

### OpenHarmony v4.0 融合架构

- **外层**：OpenHarness 核心架构
- **内层**：PyAdmin 优雅设计模式

### 核心设计模式

#### 1. 单例模式

```python
service = UFOService.instance()
```

#### 2. 依赖注入

```python
@Depends(UFOService.instance())
class MyService:
    def __init__(self, ufo_service: UFOService):
        self._ufo = ufo_service
```

#### 3. 统一响应格式

```python
@unified_resp
async def my_method():
    return {"success": True, "data": result}
```

#### 4. Hook 生命周期管理

6 个生命周期阶段：

| 阶段 | 说明 |
|------|------|
| `before_init` | 初始化前 |
| `after_init` | 初始化后 |
| `before_exec` | 执行前 |
| `after_exec` | 执行后 |
| `on_error` | 错误处理 |
| `before_shutdown` | 关闭前 |
| `after_shutdown` | 关闭后 |

### 三级配置系统

1. **Settings**（一级）：全局配置文件
2. **ModuleConfig**（二级）：模块配置
3. **RuntimeConfig**（三级）：运行时配置

---

## Skill 生成系统

### 7 阶段技能生成流程

```
Stage 1: Analyze  → 分析动作依赖和执行顺序
Stage 2: Design   → 设计技能结构和参数映射
Stage 3: Implement→ 生成技能代码和配置
Stage 4: Test     → 验证技能正确性
Stage 5: Document → 生成技能文档
Stage 6: Package  → 打包技能为可分发格式
Stage 7: Publish  → 发布技能到目标位置
```

### 使用 Skill Generator

```python
from app.skill_generator.service.generator import SkillGeneratorService
from app.skill_generator.schemas.generator import SkillGenerateIn, UFOActionInfo

# 创建服务实例
service = SkillGeneratorService.instance()
await service.initialize()

# 定义技能
skill_input = SkillGenerateIn(
    skill_name="auto_login",
    description="自动登录技能",
    actions=[
        UFOActionInfo(
            action_name="type",
            description="输入用户名",
            params=[{"name": "text", "type": "string"}],
            example="ufo keyboard type admin"
        ),
        UFOActionInfo(
            action_name="press",
            description="按回车键",
            params=[{"name": "key", "type": "string"}],
            example="ufo keyboard press enter"
        )
    ],
    output_dir="./skills"
)

# 生成技能
result = await service.generate_skill(skill_input)
print(f"✅ 技能生成成功: {result.skill_file}")
```

---

## 开发指南

### 代码风格

- Python 3.11+
- 遵循 PEP 8 规范
- 使用类型注解
- 完整的文档字符串

### 测试

```bash
# 运行所有测试
python cli.py test all

# 运行特定测试
pytest tests/unit/test_ufo.py -v
pytest tests/integration/test_cli_integration.py -v
```

### 项目结构

```
desktop-control/
├── app/                    # 应用模块
│   ├── core/              # 核心模块
│   │   ├── config.py          # 配置中心
│   │   ├── lifecycle.py        # Hook 生命周期
│   │   ├── hook_manager.py     # Hook 管理器
│   │   └── logging_system.py   # 日志系统
│   │
│   ├── ufo/               # UFO 桌面自动化
│   ├── evolution/         # Evolution 进化引擎
│   ├── bridge/            # Browser Bridge
│   ├── skill_generator/    # Skill 生成系统
│   └── mcp/               # MCP 服务器
│
├── tests/                  # 测试套件
│   ├── unit/                   # 单元测试
│   └── integration/            # 集成测试
│
├── models/                 # 数据模型
├── cli.py                 # CLI 主入口
├── config.py              # 全局配置
└── requirements.txt       # 依赖列表
```

---

## 常见错误和解决方案

### 错误 1：`can't open file 'init_db_simple.py'`

**错误信息：**
```
python.exe: can't open file 'E:\workspace\skills\desktop-control-cli\desktop-control\init_db_simple.py': [Errno 2] No such file or directory
```

**原因：** 在错误的目录中运行命令（在 `desktop-control/` 子目录而不是项目根目录）

**解决方案：**
```bash
# 返回项目根目录
cd E:\workspace\skills\desktop-control-cli

# 然后运行命令
python init_db_simple.py
```

### 错误 2：`AttributeError: 'dict' object has no attribute 'list'`

**错误信息：**
```
File "...\cli.py", line 102, in detect_available_browsers
    name: __builtins__['list'](set(paths))
AttributeError: 'dict' object has no attribute 'list'
```

**原因：** 代码中浏览器检测函数有错误（已修复）

**解决方案：**
- ✅ 已在最新代码中修复
- 确保 `cli.py` 是最新版本
- 重新运行命令

### 错误 3：技能列表为空

**错误信息：**
```
[EMPTY] 没有活动技能
```

**原因：** 数据库未初始化

**解决方案：**
```bash
# 初始化数据库
python init_db_simple.py

# 验证
python cli.py evolution list-skills
```

### 错误 4：端口被占用

**错误信息：**
```
[ERROR] 浏览器启动失败: 端口已被占用
```

**解决方案：**
```bash
# 方法1：查看现有会话
python cli.py bridge list

# 方法2：关闭现有会话
python cli.py bridge close <session_id>

# 方法3：手动终止进程
netstat -ano | findstr :9222
taskkill /PID <进程ID> /F
```

### 错误 5：浏览器未找到

**错误信息：**
```
[WARN] chrome 浏览器未找到
[INFO] 自动回退: 使用 edge 浏览器
```

**说明：** 这不是错误，系统会自动回退到可用浏览器（如 Edge）

**解决方案：**
- ✅ 系统会自动使用可用浏览器
- 如需禁用自动回退：`python cli.py bridge create --no-auto-fallback`

---

### Q: UFO 操作失败怎么办？

```bash
# 启用详细日志查看错误
python cli.py --verbose ufo mouse click 100 200

# 检查系统状态
python cli.py ufo health
```

### Q: Bridge 无法创建会话？

```bash
# 检查 Bridge 服务状态
python cli.py bridge health

# 确保没有防火墙阻止
# 尝试使用不同的浏览器类型
python cli.py bridge create --browser-type edge
```

### Q: Evolution 技能生成失败？

```bash
# 检查分析结果
python cli.py evolution analyze --execution-id exec_001

# 查看技能列表
python cli.py evolution list-skills --limit 20
```

---

## 附录

### A. UFO 20 种可执行动作

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

---

### B. Evolution 进化类型对比

| 类型 | 用途 | 示例 |
|------|------|------|
| **FIX** | 修复进化 | 从点击失败中学习，自动调整坐标或添加等待 |
| **DERIVED** | 衍生进化 | 从"登录"技能衍生出"登录并截图"技能 |
| **CAPTURED** | 捕获进化 | 录制用户操作流程，自动生成可重复执行的技能 |

---

### C. Bridge 支持的浏览器

| 浏览器 | `--browser-type` 值 | 支持状态 |
|--------|-------------------|----------|
| Google Chrome | `chrome` | ✅ 完全支持 |
| Chromium | `chromium` | ✅ 完全支持 |
| Microsoft Edge | `edge` | ✅ 完全支持 |

---

### D. MCP 工具命名规范

```
{模块}_{动作}

示例：
- ufo_click
- ufo_type
- evolution_execute
- bridge_navigate
- bridge_screenshot
```

---

### E. 错误代码参考

| 错误代码 | 说明 | 解决方案 |
|---------|------|----------|
| `E001` | UFO 初始化失败 | 检查管理员权限 |
| `E002` | Bridge 会话创建失败 | 检查浏览器是否已安装 |
| `E003` | Evolution 分析失败 | 检查 execution-id 是否存在 |
| `E004` | MCP 服务器启动失败 | 检查端口是否被占用 |

---

## 版本历史

- **v1.0.0** (2026-04-15) - 初始版本，支持 UFO、Evolution、Bridge、MCP 四大核心功能

---

## 许可证

MIT License

---

**Desktop Control** - 让 Windows 桌面自动化更简单！

**文档最后更新：** 2026-04-15
