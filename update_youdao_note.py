# -*- coding: utf-8 -*-
"""
更新有道云笔记 - 添加视频情报
"""
from pywinauto import Application
import time
import pyautogui
import win32gui
import win32con
import pyperclip

Hwnd = 8850664

def activate(hwnd):
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    time.sleep(0.2)
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.3)

print('=== 更新有道云笔记 ===')

# 1. 激活窗口
print('1. 激活窗口...')
activate(Hwnd)
time.sleep(0.5)

# 2. 导航到技术知识库
print('2. 导航到技术知识库...')
app = Application(backend='win32')
app.connect(handle=Hwnd)
dlg = app.window(handle=Hwnd)

dlg.type_keys('{F6}')
time.sleep(0.3)
dlg.type_keys('https://note.youdao.com/web/#/file/WEBa2b687261f801b0d8ba1335e93450410/empty')
time.sleep(0.3)
dlg.type_keys('{ENTER}')
time.sleep(5)

print('3. 查找并更新笔记...')

# 复制新内容到剪贴板
content = """

## 📺 抖音视频情报补充

### 小白debug - SubAgents/Agent Teams/Swarm
- **视频标题：** SubAgents/Agent Teams/Swarm是什么 7分钟看懂100个Agent团战的技术原理
- **作者：** 小白debug（41.4万粉丝）
- **链接：** https://v.douyin.com/LE35hYZIiwI/
- **数据：** 121.8万点赞

### 核心概念

#### SubAgents（子代理）
- 专注于单个任务的工作单元
- 结果仅汇报给主智能体
- 所有协调工作由主智能体统一管理

#### Agent Teams（代理团队）
- 多个独立上下文实现并行工作
- 需要成本控制（团队规模越大成本越高）
- 主智能体负责所有协调

#### Agent Swarm（代理集群）
- OpenAI 实验性框架
- 轻量级多智能体工具集
- 核心：智能体 + 交接机制
- 不同Agent像高效团队一样协同工作

**学习价值：** ⭐⭐⭐⭐⭐ 多智能体架构必看
"""

pyperclip.copy(content)
print('4. 内容已复制到剪贴板')

# 5. 粘贴
print('5. 粘贴内容...')
activate(Hwnd)
time.sleep(0.3)
pyautogui.hotkey('ctrl', 'v')
time.sleep(2)

print('6. 截图确认...')
pyautogui.screenshot().save('E:\\workspace\\note_updated.png')
print('Done!')
