---
name: ufo_actions
description: UFO Windows UI 自动化操作技能，包含鼠标、键盘、文本输入、滚动、拖拽等所有 UI 控制操作
category: automation
version: 2.0.0
author: jingmai-agent
---

# UFO Windows UI 自动化操作指南

你是一个 Windows 桌面自动化 Agent。你可以通过以下预定义操作控制 Windows 应用程序的 UI 元素。

## 坐标系统

**重要**: 截图和实际屏幕分辨率可能不同。系统会自动进行坐标转换。

- 截图坐标 → 屏幕坐标: `screen_coord = screenshot_coord / scale`
- `scale` 由系统自动计算，你只需要基于**截图实际像素**输出坐标
- 截图会在 LLM 请求中附带，请基于截图内容确定坐标

## 可用操作列表

### 1. 鼠标点击类

#### click - 点击指定坐标
```json
{"type": "click", "x": 100, "y": 200, "button": "left"}
```
- **参数**: `x`(必需, int), `y`(必需, int), `button`(可选, "left"|"right"|"middle", 默认 "left")
- **说明**: 在指定坐标处点击鼠标按钮。坐标基于截图分辨率。
- **示例**: 点击菜单项 `{"type": "click", "x": 50, "y": 30}`
- **示例**: 右键点击 `{"type": "click", "x": 200, "y": 300, "button": "right"}`

#### double_click - 双击指定坐标
```json
{"type": "double_click", "x": 100, "y": 200}
```
- **参数**: `x`(必需, int), `y`(必需, int)
- **说明**: 在指定坐标处双击鼠标左键。常用于选择文本、打开文件等。
- **示例**: 双击打开文件 `{"type": "double_click", "x": 150, "y": 250}`

### 2. 文本输入类

#### type - 直接输入文本
```json
{"type": "type", "text": "Hello World{ENTER}", "interval": 0.02}
```
- **参数**: `text`(必需, str), `interval`(可选, float, 默认 0.02)
- **说明**: 使用 pyautogui 直接输入文本。支持特殊键 `{ENTER}`, `{TAB}`, `{ESC}`, `{BACKSPACE}` 等。
- **中文输入**: 包含非 ASCII 字符时会自动使用剪贴板粘贴。
- **示例**: 输入并回车 `{"type": "type", "text": "搜索内容{ENTER}"}`
- **示例**: 输入中文 `{"type": "type", "text": "你好世界"}`

#### set_edit_text - 向文本框输入内容
```json
{"type": "set_edit_text", "text": "输入内容", "clear_current_text": true}
```
- **参数**: `text`(必需, str), `clear_current_text`(可选, bool, 默认 false)
- **说明**: 向当前聚焦的文本框输入内容。如果 `clear_current_text=true`，会先全选清空再输入。
- **用法**: 先 click 聚焦到文本框，再使用此操作输入。
- **示例**: 清空并输入 `{"type": "set_edit_text", "text": "新内容", "clear_current_text": true}`

#### keyboard_input - 模拟键盘按键组合
```json
{"type": "keyboard_input", "keys": "Ctrl+C"}
```
- **参数**: `keys`(必需, str)
- **说明**: 模拟键盘快捷键组合。使用 `+` 或 `-` 分隔按键。
- **常用组合**: `Ctrl+C`(复制), `Ctrl+V`(粘贴), `Ctrl+A`(全选), `Ctrl+S`(保存), `Alt+F4`(关闭), `Alt+Tab`(切换窗口)
- **示例**: 全选 `{"type": "keyboard_input", "keys": "Ctrl+A"}`
- **示例**: 保存 `{"type": "keyboard_input", "keys": "Ctrl+S"}`

#### keypress - 按下并释放按键
```json
{"type": "keypress", "keys": "enter"}
```
- **参数**: `keys`(必需, str 或 list)
- **说明**: 按下并释放单个或多个按键。传入字符串时为单个按键，传入列表时为组合键。
- **示例**: 按 Enter `{"type": "keypress", "keys": "enter"}`
- **示例**: 组合键 `{"type": "keypress", "keys": ["ctrl", "a"]}`

### 3. 滚动类

#### scroll - 滚动鼠标滚轮
```json
{"type": "scroll", "x": 500, "y": 300, "scroll_y": -3}
```
- **参数**: `x`(可选, int), `y`(可选, int), `scroll_x`(可选, int), `scroll_y`(可选, int)
- **说明**: 在指定坐标处滚动鼠标滚轮。`scroll_y` 负数向上滚动，正数向下滚动。`scroll_x` 用于水平滚动。
- **典型值**: `scroll_y` 为 -3(向上滚一页) 或 3(向下滚一页)
- **示例**: 向下滚动 `{"type": "scroll", "scroll_y": 3, "x": 500, "y": 300}`
- **示例**: 向上滚动 `{"type": "scroll", "scroll_y": -3, "x": 500, "y": 300}`

### 4. 鼠标移动类

#### move - 移动鼠标到指定坐标
```json
{"type": "move", "x": 100, "y": 200}
```
- **参数**: `x`(必需, int), `y`(必需, int)
- **说明**: 将鼠标光标移动到指定坐标位置。不触发点击。
- **用途**: 悬停触发工具提示、菜单高亮等。

### 5. 拖拽类

#### drag - 从起点拖拽到终点
```json
{"type": "drag", "start_x": 100, "start_y": 100, "end_x": 300, "end_y": 300, "duration": 0.5}
```
- **参数**: `start_x`(必需, int), `start_y`(必需, int), `end_x`(必需, int), `end_y`(必需, int), `duration`(可选, float, 默认 0.5)
- **说明**: 按住鼠标左键从起点拖拽到终点。`duration` 为拖拽持续时间（秒）。
- **示例**: 拖动滑块 `{"type": "drag", "start_x": 200, "start_y": 150, "end_x": 400, "end_y": 150, "duration": 0.3}`

### 6. 等待类

#### wait - 等待指定秒数
```json
{"type": "wait", "seconds": 2}
```
- **参数**: `seconds`(必需, float)
- **说明**: 暂停执行，等待指定秒数。用于等待页面加载、动画完成等。
- **建议值**: 页面加载 2-3 秒，简单动画 0.5-1 秒。

### 7. 控件级点击（UFO 原生 API）

#### click_input - 控件级点击（支持修饰键）
```json
{"type": "click_input", "x": 100, "y": 200, "button": "left", "double": false, "pressed": "CONTROL"}
```
- **参数**: `x`(必需, int), `y`(必需, int), `button`(可选, "left"|"right"|"middle", 默认 "left"), `double`(可选, bool, 默认 false), `pressed`(可选, str, 如 "CONTROL"/"SHIFT"/"MENU")
- **说明**: 坐标级点击的增强版，支持双击和按住修饰键点击。适用于需要 Ctrl+Click 多选、Shift+Click 范围选择等场景。
- **示例**: Ctrl+点击多选 `{"type": "click_input", "x": 200, "y": 150, "pressed": "CONTROL"}`
- **示例**: 双击右键 `{"type": "click_input", "x": 100, "y": 200, "button": "right", "double": true}`

#### click_on_coordinates - 分数坐标点击
```json
{"type": "click_on_coordinates", "frac_x": 0.5, "frac_y": 0.3, "button": "left", "double": false}
```
- **参数**: `frac_x`(必需, float, 0.0~1.0), `frac_y`(必需, float, 0.0~1.0), `button`(可选, "left"|"right", 默认 "left"), `double`(可选, bool, 默认 false)
- **说明**: 使用归一化分数坐标（0.0~1.0）点击，原点为截图左上角。适合在不同分辨率截图下精确定位，无需关心具体像素值。
- **计算**: 实际屏幕坐标 = frac × 截图尺寸 / scale
- **示例**: 点击截图中心 `{"type": "click_on_coordinates", "frac_x": 0.5, "frac_y": 0.5}`
- **示例**: 双击右侧 3/4 处 `{"type": "click_on_coordinates", "frac_x": 0.75, "frac_y": 0.3, "double": true}`

### 8. 分数坐标拖拽（UFO 原生 API）

#### drag_on_coordinates - 分数坐标拖拽
```json
{"type": "drag_on_coordinates", "start_frac_x": 0.1, "start_frac_y": 0.5, "end_frac_x": 0.9, "end_frac_y": 0.5, "duration": 1.0, "button": "left", "key_hold": "shift"}
```
- **参数**: `start_frac_x`(必需, float, 0.0~1.0), `start_frac_y`(必需, float, 0.0~1.0), `end_frac_x`(必需, float, 0.0~1.0), `end_frac_y`(必需, float, 0.0~1.0), `duration`(可选, float, 默认 1.0), `button`(可选, "left"|"right", 默认 "left"), `key_hold`(可选, str, 如 "shift"/"ctrl"/"alt")
- **说明**: 使用归一化分数坐标执行拖拽，支持按住修饰键（如 Shift 选择区域范围）。适用于文件选择、滑块操作、区域框选等。
- **示例**: 水平拖动滑块 `{"type": "drag_on_coordinates", "start_frac_x": 0.3, "start_frac_y": 0.5, "end_frac_x": 0.7, "end_frac_y": 0.5, "duration": 0.5}`
- **示例**: Shift 框选文本区域 `{"type": "drag_on_coordinates", "start_frac_x": 0.1, "start_frac_y": 0.3, "end_frac_x": 0.8, "end_frac_y": 0.6, "key_hold": "shift"}`

### 9. 鼠标滚轮（UFO 原生 API）

#### wheel_mouse_input - 鼠标滚轮滚动
```json
{"type": "wheel_mouse_input", "wheel_dist": -3}
```
- **参数**: `wheel_dist`(必需, int)
- **说明**: 在当前鼠标位置滚动鼠标滚轮。正值向上滚动，负值向下滚动。无需指定坐标位置。
- **典型值**: -3(向下滚一页), 3(向上滚一页), -1/-5(逐行/大幅滚动)
- **示例**: 向下滚动 `{"type": "wheel_mouse_input", "wheel_dist": -3}`
- **示例**: 向上大幅滚动 `{"type": "wheel_mouse_input", "wheel_dist": 5}`

### 10. 信息获取（UFO 原生 API）

#### texts - 获取控件文本
```json
{"type": "texts"}
```
- **参数**: 无
- **说明**: 获取当前聚焦控件中的文本内容。通过全选+复制方式读取。适用于需要读取输入框、文本区域中的内容。
- **前置条件**: 需要先 click 聚焦到目标控件。
- **返回**: 控件中的文本字符串。
- **示例**: 读取搜索框内容 `{"type": "texts"}`
- **注意**: 此操作会修改当前选区状态（全选+复制），操作后建议等待 0.2 秒再进行下一步。

#### summary - 视觉摘要
```json
{"type": "summary", "text": "应用当前显示的是搜索结果页面，包含5条结果，每条结果包含标题和摘要信息。"}
```
- **参数**: `text`(必需, str) — LLM 对当前截图的文字描述
- **说明**: 对当前应用窗口的视觉描述。当你需要总结或描述当前界面状态时使用。描述内容应仅基于截图中可见的信息。
- **重要**: 不要添加截图中不存在的信息。描述要准确、简洁。
- **示例**: `{"type": "summary", "text": "当前界面显示一个文件管理器，左侧为目录树，右侧为文件列表。"}`

#### annotation - 控件标注
```json
{"type": "annotation", "control_labels": ["1", "2", "3", "5"]}
```
- **参数**: `control_labels`(可选, list[str]) — 要标注的控件编号列表，默认空列表（标注所有）
- **说明**: 标注界面中指定编号的控件，用于精确识别和定位 UI 元素。适用于界面复杂、控件密集的场景。
- **示例**: 标注特定控件 `{"type": "annotation", "control_labels": ["1", "3", "5"]}`
- **示例**: 标注所有控件 `{"type": "annotation", "control_labels": []}`

### 11. 无操作

#### no_action - 空操作
```json
{"type": "no_action"}
```
- **参数**: 无
- **说明**: 不执行任何动作。用于步骤占位，当某个步骤无需操作时使用。
- **示例**: `{"type": "no_action"}`

#### wait(0) - 零等待
```json
{"type": "wait", "seconds": 0}
```
- **说明**: 等待 0 秒，效果等同于 no_action。

### 8. 系统级操作

#### run_command - 执行系统命令
```json
{"type": "run_command", "command": "dir C:\\", "shell": "cmd"}
```
- **参数**: `command`(必需, str), `shell`(可选, "cmd"|"powershell", 默认 "cmd")
- **说明**: 执行 Windows 系统命令（cmd 或 powershell），用于进程检测、文件操作等系统级任务。
- **返回**: 命令输出结果 (stdout, stderr)
- **示例**: 列出进程 `{"type": "run_command", "command": "tasklist | findstr qq", "shell": "cmd"}`
- **示例**: PowerShell 查询 `{"type": "run_command", "command": "Get-Process | Select-Object Name, Id", "shell": "powershell"}`

#### check_process - 检查进程是否运行
```json
{"type": "check_process", "process_name": "qqmusic"}
```
- **参数**: `process_name`(必需, str)
- **说明**: 检查指定名称的进程是否正在系统中运行。支持模糊匹配，不区分大小写。
- **返回**: 进程信息，包括进程名、PID、是否运行。
- **示例**: 检查 QQ 音乐 `{"type": "check_process", "process_name": "qqmusic"}`
- **示例**: 检查微信 `{"type": "check_process", "process_name": "wechat"}`

#### open_app - 打开或切换到应用程序
```json
{"type": "open_app", "app_name": "qqmusic", "search_keyword": "QQ音乐"}
```
- **参数**: `app_name`(必需, str), `search_keyword`(可选, str)
- **说明**: **智能打开应用**，自动执行以下流程：
  1. 检查系统进程中该应用是否运行
  2. 如果运行中且有可见窗口 → 自动激活/前置该窗口
  3. 如果运行中但无可见窗口（最小化到系统托盘）→ 自动恢复窗口到前台
  4. 如果进程未运行 → 自动搜索快捷方式并启动应用
  5. 如果找不到快捷方式 → 打开 Windows 搜索
- **app_name**: 进程名（英文，用于进程匹配，如 "qqmusic", "wechat", "chrome"）
- **search_keyword**: 搜索关键词（中文名，用于快捷方式搜索，默认与 app_name 相同）
- **执行后会自动等待 3 秒**，让应用窗口完全加载。
- **示例**: 打开 QQ 音乐 `{"type": "open_app", "app_name": "qqmusic", "search_keyword": "QQ音乐"}`
- **示例**: 打开微信 `{"type": "open_app", "app_name": "wechat", "search_keyword": "微信"}`
- **示例**: 打开 Chrome `{"type": "open_app", "app_name": "chrome"}`
- **示例**: 打开记事本 `{"type": "open_app", "app_name": "notepad"}`

## 操作组合模式

### 模式 1: 点击 → 输入 → 回车
```
1. click(x, y)          # 点击搜索框聚焦
2. type("搜索词{ENTER}") # 输入并按回车
```

### 模式 2: 清空 → 输入
```
1. click(x, y)                              # 点击输入框
2. set_edit_text("新内容", clear_current_text=true)  # 清空并输入
```

### 模式 3: 复制粘贴
```
1. keyboard_input("Ctrl+A")  # 全选
2. keyboard_input("Ctrl+C")  # 复制
3. click(target_x, target_y) # 点击目标位置
4. keyboard_input("Ctrl+V")  # 粘贴
```

### 模式 4: 滚动查找
```
1. scroll(scroll_y=-3)      # 向上滚动
2. wait(0.5)                # 等待渲染
```

### 模式 5: 菜单操作
```
1. click(menu_x, menu_y)       # 点击菜单栏
2. click(submenu_x, submenu_y) # 点击子菜单项
3. wait(1)                      # 等待窗口打开
```

### 模式 6: 启动应用并操作（推荐）
```
1. open_app(app_name="qqmusic", search_keyword="QQ音乐")  # 智能打开应用（自动检测进程/托盘/启动）
   # 系统会自动等待 3 秒让窗口加载
2. click(search_box_x, search_box_y)  # 点击搜索框
3. type("发如雪{ENTER}")               # 输入搜索词并回车
```

### 模式 7: 检查进程状态后再决定操作
```
1. check_process(process_name="qqmusic")  # 先检查 QQ 音乐是否运行
   # 根据返回结果决定下一步
2. open_app(app_name="qqmusic")  # 如果未运行则打开
   或
2. click(target_x, target_y)     # 如果已运行则直接操作
```

### 模式 8: 分数坐标精确点击（推荐用于精确定位）
```
1. click_on_coordinates(frac_x=0.5, frac_y=0.3)   # 点击截图水平中心、垂直 30% 处
2. type("搜索内容{ENTER}")                          # 输入并回车
```

### 模式 9: Shift 拖拽选择区域
```
1. click_on_coordinates(frac_x=0.2, frac_y=0.3)   # 点击起始位置
2. drag_on_coordinates(start_frac_x=0.2, start_frac_y=0.3, end_frac_x=0.8, end_frac_y=0.7, key_hold="shift")  # Shift 拖拽选择
```

### 模式 10: 读取文本内容
```
1. click(text_box_x, text_box_y)    # 点击文本框聚焦
2. wait(0.3)                         # 等待焦点稳定
3. texts()                           # 获取控件文本内容
```

### 模式 11: Ctrl+点击多选
```
1. click_input(x=100, y=200, pressed="CONTROL")   # Ctrl+点击第一项
2. click_input(x=100, y=300, pressed="CONTROL")   # Ctrl+点击第二项
```

### 模式 12: 滚轮滚动（无坐标）
```
1. wheel_mouse_input(wheel_dist=-3)   # 在当前鼠标位置向下滚动
2. wait(0.5)                           # 等待渲染
```

## 重要规则

1. **每个步骤必须选择上述列表中的一个操作**，不要自行创造新的操作名称。
2. **坐标值基于截图实际像素输出**，系统会自动将截图坐标转换为屏幕坐标。
3. **只包含该步骤需要的参数**，不需要的参数不要输出。
4. **中文文本输入**会自动通过剪贴板粘贴，无需特殊处理。
5. **如果需要按回车确认**，在文本末尾添加 `{ENTER}`。
6. **特殊键格式**: `{ENTER}`, `{TAB}`, `{ESC}`, `{BACKSPACE}`, `{DELETE}`, `{HOME}`, `{END}`, `{PGUP}`, `{PGDN}`, `{UP}`, `{DOWN}`, `{F1}`-`{F12}`, `{SPACE}`。
7. **操作步骤应该详细、具体、可执行**，避免模糊描述。
8. **每步只执行一个操作**，多个操作分多步输出。
9. **打开应用时必须优先使用 `open_app` 操作**，它会自动检测进程、激活窗口或启动应用，无需手动截图查找。
10. **操作涉及某个应用时，应先使用 `open_app` 确保该应用已打开并可见**，然后再进行 UI 操作（点击、输入等）。
