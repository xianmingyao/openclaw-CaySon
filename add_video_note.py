# -*- coding: utf-8 -*-
"""
追加视频情报到有道云笔记
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

print('=== 追加视频情报到笔记 ===')

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

print('3. 滚动到页面底部，找到之前创建的笔记...')

# 4. 尝试滚动页面找到笔记
activate(Hwnd)
time.sleep(0.3)
# 按 End 键滚动到页面底部
pyautogui.press('end')
time.sleep(1)

# 5. 点击笔记
print('4. 点击笔记标题...')
pyautogui.click(500, 200)  # 点击左侧列表区域
time.sleep(2)

# 6. 滚动到笔记末尾
print('5. 滚动到笔记末尾...')
pyautogui.press('end')
time.sleep(0.5)
pyautogui.press('end')
time.sleep(0.5)

# 7. 添加新内容
print('6. 添加视频情报内容...')

content = """

---

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
time.sleep(0.5)

# 8. 粘贴
print('7. 粘贴内容...')
pyautogui.hotkey('ctrl', 'v')
time.sleep(2)

# 9. 截图
print('8. 截图确认...')
pyautogui.screenshot().save('E:\\workspace\\note_video_added.png')
print('Done!')
