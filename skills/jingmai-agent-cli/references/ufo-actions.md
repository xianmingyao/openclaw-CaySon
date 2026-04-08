# UFO Windows UI 自动化操作指南

Windows 桌面自动化 Agent 核心操作参考。

## 坐标系统

**重要**: 截图和实际屏幕分辨率可能不同，系统自动进行坐标转换。

- 截图坐标 → 屏幕坐标: `screen_coord = screenshot_coord / scale`
- `scale` 由系统自动计算，只需基于**截图实际像素**输出坐标

---

## 操作分类

### 1. 鼠标点击类

| 操作 | 参数 | 说明 |
|------|------|------|
| `click` | `x`, `y`, `button` | 点击指定坐标 |
| `double_click` | `x`, `y` | 双击指定坐标 |

**click 示例:**
```json
{"type": "click", "x": 100, "y": 200, "button": "left"}
{"type": "click", "x": 200, "y": 300, "button": "right"}
```

---

### 2. 文本输入类

| 操作 | 参数 | 说明 |
|------|------|------|
| `type` | `text`, `interval` | 直接输入文本，支持 `{ENTER}`, `{TAB}` 等 |
| `set_edit_text` | `text`, `clear_current_text` | 向文本框输入 |
| `keyboard_input` | `keys` | 键盘快捷键组合 |
| `keypress` | `keys` | 按下并释放按键 |

**type 示例:**
```json
{"type": "type", "text": "Hello World{ENTER}", "interval": 0.02}
{"type": "type", "text": "你好世界"}
```

**keyboard_input 示例:**
```json
{"type": "keyboard_input", "keys": "Ctrl+C"}
{"type": "keyboard_input", "keys": "Ctrl+S"}
```

---

### 3. 滚动类

| 操作 | 参数 | 说明 |
|------|------|------|
| `scroll` | `x`, `y`, `scroll_x`, `scroll_y` | 滚动鼠标滚轮 |
| `wheel_mouse_input` | `wheel_dist` | 滚轮滚动（无坐标） |

**scroll 示例:**
```json
{"type": "scroll", "x": 500, "y": 300, "scroll_y": -3}
{"type": "wheel_mouse_input", "wheel_dist": -3}
```

---

### 4. 鼠标移动类

| 操作 | 参数 | 说明 |
|------|------|------|
| `move` | `x`, `y` | 移动鼠标到指定坐标 |

---

### 5. 拖拽类

| 操作 | 参数 | 说明 |
|------|------|------|
| `drag` | `start_x`, `start_y`, `end_x`, `end_y`, `duration` | 拖拽 |
| `drag_on_coordinates` | `start_frac_*`, `end_frac_*`, `key_hold` | 分数坐标拖拽 |

**drag 示例:**
```json
{"type": "drag", "start_x": 100, "start_y": 100, "end_x": 300, "end_y": 300, "duration": 0.5}
```

**drag_on_coordinates 示例:**
```json
{"type": "drag_on_coordinates", "start_frac_x": 0.2, "start_frac_y": 0.5, "end_frac_x": 0.8, "end_frac_y": 0.5, "key_hold": "shift"}
```

---

### 6. 等待类

| 操作 | 参数 | 说明 |
|------|------|------|
| `wait` | `seconds` | 等待指定秒数 |
| `no_action` | - | 空操作 |

**wait 示例:**
```json
{"type": "wait", "seconds": 2}
{"type": "no_action"}
```

---

### 7. 控件级点击

| 操作 | 参数 | 说明 |
|------|------|------|
| `click_input` | `x`, `y`, `button`, `double`, `pressed` | 控件级点击，支持修饰键 |
| `click_on_coordinates` | `frac_x`, `frac_y`, `button`, `double` | 分数坐标点击 |

**click_input 示例:**
```json
{"type": "click_input", "x": 100, "y": 200, "pressed": "CONTROL"}
{"type": "click_input", "x": 200, "y": 150, "double": true}
```

**click_on_coordinates 示例:**
```json
{"type": "click_on_coordinates", "frac_x": 0.5, "frac_y": 0.3}
```

---

### 8. 信息获取

| 操作 | 参数 | 说明 |
|------|------|------|
| `texts` | - | 获取控件文本 |
| `summary` | `text` | 视觉摘要 |
| `annotation` | `control_labels` | 控件标注 |

**texts 示例:**
```json
{"type": "texts"}
```

---

### 9. 系统级操作

| 操作 | 参数 | 说明 |
|------|------|------|
| `run_command` | `command`, `shell` | 执行系统命令 |
| `check_process` | `process_name` | 检查进程 |
| `open_app` | `app_name`, `search_keyword` | 打开应用 |

**run_command 示例:**
```json
{"type": "run_command", "command": "dir C:\\", "shell": "cmd"}
{"type": "run_command", "command": "Get-Process", "shell": "powershell"}
```

**open_app 示例:**
```json
{"type": "open_app", "app_name": "notepad", "search_keyword": "记事本"}
{"type": "open_app", "app_name": "chrome", "search_keyword": "Chrome"}
```

---

## 特殊键格式

```
{ENTER}, {TAB}, {ESC}, {BACKSPACE}, {DELETE}
{HOME}, {END}, {PGUP}, {PGDN}
{UP}, {DOWN}
{F1}-{F12}
{SPACE}
```

---

## 操作组合模式

### 模式1: 点击 → 输入 → 回车
```
1. click(x, y)
2. type("搜索词{ENTER}")
```

### 模式2: 清空 → 输入
```
1. click(x, y)
2. set_edit_text("新内容", clear_current_text=true)
```

### 模式3: 复制粘贴
```
1. keyboard_input("Ctrl+A")
2. keyboard_input("Ctrl+C")
3. click(target_x, target_y)
4. keyboard_input("Ctrl+V")
```

### 模式4: 启动应用（推荐）
```
1. open_app(app_name="notepad", search_keyword="记事本")
2. wait(3)
3. click(search_x, search_y)
4. type("内容{ENTER}")
```

### 模式5: 检查进程后再决定
```
1. check_process(process_name="qqmusic")
2. open_app(...)  # 如果未运行
   或
2. click(...)     # 如果已运行
```

### 模式6: Ctrl+点击多选
```
1. click_input(x=100, y=200, pressed="CONTROL")
2. click_input(x=100, y=300, pressed="CONTROL")
```

### 模式7: Shift 拖拽选择
```
1. drag_on_coordinates(start_frac_x=0.2, start_frac_y=0.3, end_frac_x=0.8, end_frac_y=0.7, key_hold="shift")
```

---

## 重要规则

1. **每步只执行一个操作**，多个操作分多步输出
2. **坐标基于截图实际像素**，系统自动转换
3. **中文文本输入**自动通过剪贴板粘贴
4. **打开应用优先使用 `open_app`**，它会自动检测进程/激活窗口/启动应用
5. **操作涉及某个应用时，应先 `open_app` 确保应用已打开并可见**
