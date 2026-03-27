---
name: windows-control
description: Windows UI 自动化控制技能 - 通过 Python 脚本调用 jingmai-agent 的 action 系统，实现鼠标、键盘、窗口、文件等全链路 Windows 自动化控制
category: automation
version: 1.0.0
author: jingmai-agent
---

# Windows-Control 技能指南

通过 `exec` 工具调用 Python 脚本，执行 jingmai-agent 的 Action 系统，实现 Windows UI 全链路自动化控制。

## 快速开始

### 安装依赖
```bash
pip install pyautogui pyperclip Pillow psutil
```

### 基本调用模式
```python
# 方式 1: 通过 exec 调用 Python 脚本
exec(command="python -c \"from jingmai_agent.actions import ClickAction; ...\"", timeout=10)

# 方式 2: 直接调用 Windows API
exec(command="powershell -Command \"...\"", timeout=10)
```

---

## 操作分类索引

| 分类 | 操作数 | 说明 |
|------|--------|------|
| 🖱️ 鼠标操作 | 7 | 点击、双击、移动、拖拽 |
| ⌨️ 键盘操作 | 4 | 文本输入、快捷键 |
| 📜 滚动操作 | 2 | 滚轮滚动 |
| 🖥️ 窗口操作 | 1 | 打开/切换应用 |
| ⏱️ 系统操作 | 4 | 等待、命令、进程检测 |
| 📝 信息采集 | 3 | 文本提取、摘要、标注 |
| 🖼️ UI 采集 | 9 | 窗口信息、截图、控件树 |
| 🌐 Web 操作 | 12 | 浏览器自动化 |
| 📁 文件操作 | 17 | Shell/文件系统 |
| 📊 Office 操作 | 17 | Word/Excel/PPT |

---

## 1. 🖱️ 鼠标操作

### 1.1 click - 点击指定坐标
```python
# SKILL 调用示例 (exec command)
python -c "
import asyncio
from app.service.actions.mouse_actions import ClickAction
action = ClickAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(x=100, y=200, button='left'))
print(result)
"
```
- **参数**: `x`(int, 必需), `y`(int, 必需), `button`(str, 可选, 默认"left")
- **返回值**: `{"success": true, "metadata": {"coordinates": {"x": 100, "y": 200}}}`

### 1.2 double_click - 双击指定坐标
```python
python -c "
import asyncio
from app.service.actions.mouse_actions import DoubleClickAction
action = DoubleClickAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(x=150, y=250))
print(result)
"
```
- **参数**: `x`(int), `y`(int)

### 1.3 click_input - 控件级点击（支持修饰键）
```python
python -c "
import asyncio
from app.service.actions.mouse_actions import ClickInputAction
action = ClickInputAction()
action.set_context(1.0, (1920, 1080))
# Ctrl+点击
result = asyncio.run(action.execute(x=200, y=150, button='left', double=False, pressed='CONTROL'))
print(result)
"
```
- **参数**: `x`, `y`, `button`(可选), `double`(bool, 可选), `pressed`(str, 可选, "CONTROL"/"SHIFT"/"MENU")

### 1.4 click_on_coordinates - 分数坐标点击
```python
python -c "
import asyncio
from app.service.actions.mouse_actions import ClickOnCoordinatesAction
action = ClickOnCoordinatesAction()
action.set_context(1.0, (1920, 1080))
# 点击截图中心 (0.5, 0.5)
result = asyncio.run(action.execute(frac_x=0.5, frac_y=0.5, button='left', double=False))
print(result)
"
```
- **参数**: `frac_x`(float, 0.0~1.0), `frac_y`(float, 0.0~1.0), `button`(可选), `double`(可选)

### 1.5 move - 移动鼠标到指定坐标
```python
python -c "
import asyncio
from app.service.actions.mouse_actions import MoveAction
action = MoveAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(x=300, y=400))
print(result)
"
```
- **参数**: `x`(int), `y`(int)

### 1.6 drag - 从起点拖拽到终点
```python
python -c "
import asyncio
from app.service.actions.mouse_actions import DragAction
action = DragAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(start_x=100, start_y=100, end_x=400, end_y=300, duration=0.5))
print(result)
"
```
- **参数**: `start_x`, `start_y`, `end_x`, `end_y`, `duration`(float, 可选, 默认0.5)

### 1.7 drag_on_coordinates - 分数坐标拖拽
```python
python -c "
import asyncio
from app.service.actions.mouse_actions import DragOnCoordinatesAction
action = DragOnCoordinatesAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(
    start_frac_x=0.2, start_frac_y=0.3,
    end_frac_x=0.8, end_frac_y=0.7,
    duration=1.0, button='left', key_hold='shift'
))
print(result)
"
```
- **参数**: `start_frac_x`, `start_frac_y`, `end_frac_x`, `end_frac_y`, `duration`(可选), `button`(可选), `key_hold`(可选)

---

## 2. ⌨️ 键盘操作

### 2.1 type - 输入文本
```python
python -c "
import asyncio
from app.service.actions.keyboard_actions import TypeAction
action = TypeAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(text='Hello World{ENTER}', interval=0.02))
print(result)
"
```
- **参数**: `text`(str, 必需), `interval`(float, 可选)
- **特殊键**: `{ENTER}`, `{TAB}`, `{ESC}`, `{BACKSPACE}`, `{DELETE}`, `{HOME}`, `{END}`, `{PGUP}`, `{PGDN}`, `{UP}`, `{DOWN}`, `{F1}`~`{F12}`, `{SPACE}`
- **注意**: 包含中文时自动使用剪贴板粘贴

### 2.2 set_edit_text - 向文本框输入内容
```python
python -c "
import asyncio
from app.service.actions.keyboard_actions import SetEditTextAction
action = SetEditTextAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(text='新内容', clear_current_text=True))
print(result)
"
```
- **参数**: `text`(str), `clear_current_text`(bool, 可选)

### 2.3 keyboard_input - 模拟键盘组合键
```python
python -c "
import asyncio
from app.service.actions.keyboard_actions import KeyboardInputAction
action = KeyboardInputAction()
action.set_context(1.0, (1920, 1080))
# Ctrl+C 复制
result = asyncio.run(action.execute(keys='Ctrl+C'))
print(result)
"
```
- **参数**: `keys`(str, 如 "Ctrl+C", "Alt+Tab")
- **常用组合**: `Ctrl+C`, `Ctrl+V`, `Ctrl+A`, `Ctrl+S`, `Alt+F4`, `Alt+Tab`

### 2.4 keypress - 按下并释放按键
```python
python -c "
import asyncio
from app.service.actions.keyboard_actions import KeypressAction
action = KeypressAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(keys='enter'))
print(result)
"
```
- **参数**: `keys`(str 或 list)

---

## 3. 📜 滚动操作

### 3.1 scroll - 在指定坐标滚动
```python
python -c "
import asyncio
from app.service.actions.scroll_actions import ScrollAction
action = ScrollAction()
action.set_context(1.0, (1920, 1080))
# 向下滚动3页
result = asyncio.run(action.execute(scroll_x=0, scroll_y=-3, x=500, y=300))
print(result)
"
```
- **参数**: `scroll_x`(int, 可选), `scroll_y`(int, 可选, 负数向下), `x`(int, 可选), `y`(int, 可选)

### 3.2 wheel_mouse_input - 鼠标滚轮滚动
```python
python -c "
import asyncio
from app.service.actions.scroll_actions import WheelMouseInputAction
action = WheelMouseInputAction()
action.set_context(1.0, (1920, 1080))
# 向上滚动5个单位
result = asyncio.run(action.execute(wheel_dist=5))
print(result)
"
```
- **参数**: `wheel_dist`(int, 负数向下)

---

## 4. 🖥️ 窗口操作

### 4.1 open_app - 打开或切换到应用程序
```python
python -c "
import asyncio
from app.service.actions.window_actions import OpenAppAction
action = OpenAppAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(app_name='notepad', search_keyword='记事本'))
print(result)
"
```
- **参数**: `app_name`(str, 进程名), `search_keyword`(str, 可选, 中文搜索关键词)
- **返回值**: 包含 `action`(activated/restorored/launched) 和 `detail`

---

## 5. ⏱️ 系统操作

### 5.1 wait - 等待指定秒数
```python
python -c "
import asyncio
from app.service.actions.system_actions import WaitAction
action = WaitAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(seconds=2.0))
print(result)
"
```
- **参数**: `seconds`(float)

### 5.2 run_command - 执行系统命令
```python
python -c "
import asyncio
from app.service.actions.system_actions import RunCommandAction
action = RunCommandAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(command='dir C:\\\\', shell='cmd'))
print(result)
"
```
- **参数**: `command`(str), `shell`(str, 可选, "cmd"/"powershell")

### 5.3 check_process - 检查进程是否运行
```python
python -c "
import asyncio
from app.service.actions.system_actions import CheckProcessAction
action = CheckProcessAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(process_name='notepad'))
print(result)
"
```
- **参数**: `process_name`(str, 支持模糊匹配)

### 5.4 no_action - 空操作
```python
python -c "
import asyncio
from app.service.actions.system_actions import NoAction
action = NoAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute())
print(result)
"
```

---

## 6. 📝 信息采集

### 6.1 texts - 获取控件文本
```python
python -c "
import asyncio
from app.service.actions.info_actions import TextsAction
action = TextsAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute())
print(result)
"
```

### 6.2 summary - 视觉摘要
```python
python -c "
import asyncio
from app.service.actions.info_actions import SummaryAction
action = SummaryAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(text='当前界面显示一个文件管理器'))
print(result)
"
```
- **参数**: `text`(str, LLM 对当前截图的文字描述)

### 6.3 annotation - 控件标注
```python
python -c "
import asyncio
from app.service.actions.info_actions import AnnotationAction
action = AnnotationAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(control_labels=['1', '2', '3']))
print(result)
"
```
- **参数**: `control_labels`(list[str], 可选, 空列表标注所有)

---

## 7. 🖼️ UI 采集

### 7.1 get_desktop_app_info - 获取桌面窗口信息
```python
python -c "
import asyncio
from app.service.actions.ui_collect_actions import GetDesktopAppInfoAction
action = GetDesktopAppInfoAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute())
print(result)
"
```

### 7.2 get_desktop_app_target_info - 获取 TargetInfo
```python
python -c "
import asyncio
from app.service.actions.ui_collect_actions import GetDesktopAppTargetInfoAction
action = GetDesktopAppTargetInfoAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute())
print(result)
"
```

### 7.3 capture_window_screenshot - 截取活动窗口
```python
python -c "
import asyncio
from app.service.actions.ui_collect_actions import CaptureWindowScreenshotAction
action = CaptureWindowScreenshotAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute())
print(result)
"
```

### 7.4 capture_desktop_screenshot - 截取整个桌面
```python
python -c "
import asyncio
from app.service.actions.ui_collect_actions import CaptureDesktopScreenshotAction
action = CaptureDesktopScreenshotAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute())
print(result)
"
```

### 7.5 get_ui_tree - 获取 UI 控件树
```python
python -c "
import asyncio
from app.service.actions.ui_collect_actions import GetUITreeAction
action = GetUITreeAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(max_depth=10))
print(result)
"
```
- **参数**: `max_depth`(int, 可选, 默认10)

### 7.6 get_app_window_info - 获取活动窗口详情
```python
python -c "
import asyncio
from app.service.actions.ui_collect_actions import GetAppWindowInfoAction
action = GetAppWindowInfoAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute())
print(result)
"
```

### 7.7 get_app_window_controls_info - 获取窗口控件
```python
python -c "
import asyncio
from app.service.actions.ui_collect_actions import GetAppWindowControlsInfoAction
action = GetAppWindowControlsInfoAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(max_depth=8))
print(result)
"
```

### 7.8 get_app_window_controls_target_info - 获取控件 TargetInfo
```python
python -c "
import asyncio
from app.service.actions.ui_collect_actions import GetAppWindowControlsTargetInfoAction
action = GetAppWindowControlsTargetInfoAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(max_depth=8))
print(result)
"
```

### 7.9 add_control_list - 添加控件列表
```python
python -c "
import asyncio
from app.service.actions.ui_collect_actions import AddControlListAction
action = AddControlListAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(controls=[
    {'name': '按钮1', 'control_type': 'Button', 'left': 100, 'top': 200, 'width': 80, 'height': 30}
]))
print(result)
"
```

---

## 8. 🌐 Web 操作

### 8.1 web_crawler - 网页爬虫
```python
python -c "
import asyncio
from app.service.actions.web_actions import WebCrawlerAction
action = WebCrawlerAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(url='https://example.com'))
print(result)
"
```

### 8.2 navigate_to_url - 导航到 URL
```python
python -c "
import asyncio
from app.service.actions.web_actions import NavigateToUrlAction
action = NavigateToUrlAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(url='https://example.com', wait_until='load'))
print(result)
"
```

### 8.3 click_element - 点击页面元素
```python
python -c "
import asyncio
from app.service.actions.web_actions import ClickElementAction
action = ClickElementAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(selector='#submit-btn'))
print(result)
"
```

### 8.4 type_text - 在输入框输入文本
```python
python -c "
import asyncio
from app.service.actions.web_actions import TypeTextAction
action = TypeTextAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(selector='#search-input', text='搜索内容', clear=True))
print(result)
"
```

### 8.5 get_page_content - 获取页面内容
```python
python -c "
import asyncio
from app.service.actions.web_actions import GetPageContentAction
action = GetPageContentAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(selector='body'))
print(result)
"
```

### 8.6 get_page_title - 获取页面标题
```python
python -c "
import asyncio
from app.service.actions.web_actions import GetPageTitleAction
action = GetPageTitleAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute())
print(result)
"
```

### 8.7 scroll_page - 滚动页面
```python
python -c "
import asyncio
from app.service.actions.web_actions import ScrollPageAction
action = ScrollPageAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(direction='down', amount=500))
print(result)
"
```

### 8.8 wait_for_element - 等待元素出现
```python
python -c "
import asyncio
from app.service.actions.web_actions import WaitForElementAction
action = WaitForElementAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(selector='.result-item', timeout=10.0))
print(result)
"
```

### 8.9 take_screenshot - 网页截图
```python
python -c "
import asyncio
from app.service.actions.web_actions import TakeScreenshotAction
action = TakeScreenshotAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(full_page=False, selector=''))
print(result)
"
```

### 8.10 execute_javascript - 执行 JavaScript
```python
python -c "
import asyncio
from app.service.actions.web_actions import ExecuteJavascriptAction
action = ExecuteJavascriptAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(script='return document.title'))
print(result)
"
```

### 8.11 get_element_text - 获取元素文本
```python
python -c "
import asyncio
from app.service.actions.web_actions import GetElementTextAction
action = GetElementTextAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(selector='.title'))
print(result)
"
```

### 8.12 get_element_attribute - 获取元素属性
```python
python -c "
import asyncio
from app.service.actions.web_actions import GetElementAttributeAction
action = GetElementAttributeAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(selector='a.link', attribute='href'))
print(result)
"
```

---

## 9. 📁 文件操作

### 9.1 run_shell - 执行 Shell 命令
```python
python -c "
import asyncio
from app.service.actions.shell_actions import RunShellAction
action = RunShellAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(command='dir', timeout=30))
print(result)
"
```

### 9.2 execute_command - 执行系统命令
```python
python -c "
import asyncio
from app.service.actions.shell_actions import ExecuteCommandAction
action = ExecuteCommandAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(command='Get-Process', shell='powershell', timeout=30))
print(result)
"
```

### 9.3 change_directory - 切换目录
```python
python -c "
import asyncio
from app.service.actions.shell_actions import ChangeDirectoryAction
action = ChangeDirectoryAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(path='C:\\\\Users'))
print(result)
"
```

### 9.4 get_current_directory - 获取当前目录
```python
python -c "
import asyncio
from app.service.actions.shell_actions import GetCurrentDirectoryAction
action = GetCurrentDirectoryAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute())
print(result)
"
```

### 9.5 list_files - 列出目录文件
```python
python -c "
import asyncio
from app.service.actions.shell_actions import ListFilesAction
action = ListFilesAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(path='.', pattern='*.txt', recursive=False))
print(result)
"
```

### 9.6 create_directory - 创建目录
```python
python -c "
import asyncio
from app.service.actions.shell_actions import CreateDirectoryAction
action = CreateDirectoryAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(path='C:\\\\temp\\\\new_folder', exist_ok=True))
print(result)
"
```

### 9.7 remove_file - 删除文件或目录
```python
python -c "
import asyncio
from app.service.actions.shell_actions import RemoveFileAction
action = RemoveFileAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(path='C:\\\\temp\\\\old_file.txt', recursive=False))
print(result)
"
```

### 9.8 copy_file - 复制文件
```python
python -c "
import asyncio
from app.service.actions.shell_actions import CopyFileAction
action = CopyFileAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(source='C:\\\\src\\\\file.txt', destination='C:\\\\dst\\\\file.txt'))
print(result)
"
```

### 9.9 move_file - 移动/重命名文件
```python
python -c "
import asyncio
from app.service.actions.shell_actions import MoveFileAction
action = MoveFileAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(source='C:\\\\old\\\\file.txt', destination='C:\\\\new\\\\file.txt'))
print(result)
"
```

### 9.10 read_file - 读取文件内容
```python
python -c "
import asyncio
from app.service.actions.shell_actions import ReadFileAction
action = ReadFileAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(path='C:\\\\file.txt', encoding='utf-8', offset=0, limit=500))
print(result)
"
```

### 9.11 write_file - 写入文件内容
```python
python -c "
import asyncio
from app.service.actions.shell_actions import WriteFileAction
action = WriteFileAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(path='C:\\\\output.txt', content='文件内容', append=False))
print(result)
"
```

### 9.12 check_file_exists - 检查文件是否存在
```python
python -c "
import asyncio
from app.service.actions.shell_actions import CheckFileExistsAction
action = CheckFileExistsAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(path='C:\\\\file.txt'))
print(result)
"
```

### 9.13 get_file_info - 获取文件详情
```python
python -c "
import asyncio
from app.service.actions.shell_actions import GetFileInfoAction
action = GetFileInfoAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(path='C:\\\\file.txt'))
print(result)
"
```

### 9.14 find_files - 搜索文件
```python
python -c "
import asyncio
from app.service.actions.shell_actions import FindFilesAction
action = FindFilesAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(path='.', pattern='*.py', name_contains='action', max_results=50))
print(result)
"
```

### 9.15 get_environment_variable - 获取环境变量
```python
python -c "
import asyncio
from app.service.actions.shell_actions import GetEnvironmentVariableAction
action = GetEnvironmentVariableAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(name='PATH'))
print(result)
"
```

### 9.16 set_environment_variable - 设置环境变量
```python
python -c "
import asyncio
from app.service.actions.shell_actions import SetEnvironmentVariableAction
action = SetEnvironmentVariableAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(name='MY_VAR', value='my_value'))
print(result)
"
```

### 9.17 get_system_info - 获取系统信息
```python
python -c "
import asyncio
from app.service.actions.shell_actions import GetSystemInfoAction
action = GetSystemInfoAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute())
print(result)
"
```

---

## 10. 📊 Office 操作

### 10.1 Word 操作

#### save - 保存文档
```python
python -c "
import asyncio
from app.service.actions.office_actions import SaveAction
action = SaveAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute())
print(result)
"
```

#### word_save_as - Word 另存为
```python
python -c "
import asyncio
from app.service.actions.office_actions import WordSaveAsAction
action = WordSaveAsAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(path='C:\\\\output.pdf', format='pdf'))
print(result)
"
```

#### word_set_font - 设置字体
```python
python -c "
import asyncio
from app.service.actions.office_actions import WordSetFontAction
action = WordSetFontAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(font_name='微软雅黑', size=14, bold=True))
print(result)
"
```

#### word_insert_table - 插入表格
```python
python -c "
import asyncio
from app.service.actions.office_actions import WordInsertTableAction
action = WordInsertTableAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(rows=3, cols=3, data=[['姓名', '年龄'], ['张三', 25]]))
print(result)
"
```

### 10.2 Excel 操作

#### excel_save_as - Excel 另存为
```python
python -c "
import asyncio
from app.service.actions.office_actions import ExcelSaveAsAction
action = ExcelSaveAsAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(path='C:\\\\output.csv', format='csv'))
print(result)
"
```

#### excel_table2markdown - 转 Markdown
```python
python -c "
import asyncio
from app.service.actions.office_actions import ExcelTable2MarkdownAction
action = ExcelTable2MarkdownAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute())
print(result)
"
```

#### excel_insert_table - 插入数据
```python
python -c "
import asyncio
from app.service.actions.office_actions import ExcelInsertTableAction
action = ExcelInsertTableAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(data=[[1, 2], [3, 4]], start_cell='A1'))
print(result)
"
```

### 10.3 PPT 操作

#### ppt_save_as - PPT 另存为
```python
python -c "
import asyncio
from app.service.actions.office_actions import PPTSaveAsAction
action = PPTSaveAsAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(path='C:\\\\output.pdf', format='pdf'))
print(result)
"
```

#### ppt_set_background_color - 设置背景色
```python
python -c "
import asyncio
from app.service.actions.office_actions import PPTSetBackgroundColorAction
action = PPTSetBackgroundColorAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(color='0070C0', slide_index=1))
print(result)
"
```

---

## 常用操作组合

### 打开应用并操作
```python
# 1. 打开记事本
python -c "
import asyncio
from app.service.actions.window_actions import OpenAppAction
action = OpenAppAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(app_name='notepad', search_keyword='记事本'))
print(result)
"

# 2. 等待窗口加载
python -c "
import asyncio
from app.service.actions.system_actions import WaitAction
action = WaitAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(seconds=2.0))
print(result)
"

# 3. 输入文本
python -c "
import asyncio
from app.service.actions.keyboard_actions import TypeAction
action = TypeAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(text='Hello World{ENTER}'))
print(result)
"
```

### 点击并输入
```python
# 1. 点击输入框
python -c "
import asyncio
from app.service.actions.mouse_actions import ClickAction
action = ClickAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(x=400, y=200))
print(result)
"

# 2. 输入内容
python -c "
import asyncio
from app.service.actions.keyboard_actions import SetEditTextAction
action = SetEditTextAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(text='新内容', clear_current_text=True))
print(result)
"

# 3. 按回车确认
python -c "
import asyncio
from app.service.actions.keyboard_actions import KeypressAction
action = KeypressAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(keys='enter'))
print(result)
"
```

### 窗口信息采集
```python
# 1. 获取桌面窗口列表
python -c "
import asyncio
from app.service.actions.ui_collect_actions import GetDesktopAppInfoAction
action = GetDesktopAppInfoAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute())
print(result)
"

# 2. 截取桌面截图
python -c "
import asyncio
from app.service.actions.ui_collect_actions import CaptureDesktopScreenshotAction
action = CaptureDesktopScreenshotAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute())
print(result)
"
```

---

## 依赖说明

### Python 依赖
```txt
pyautogui>=0.9.54
pyperclip>=1.8.2
Pillow>=10.0.0
psutil>=5.9.0
```

### Windows 依赖
- pywin32 (用于 Office COM 操作)
- UIAutomation (Windows 内置)

### 安装命令
```bash
pip install pyautogui pyperclip Pillow psutil pywin32
```
