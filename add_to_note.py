# -*- coding: utf-8 -*-
"""
追加视频情报到今日学习总结笔记
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

print('=== 追加内容到今日学习总结 ===')

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

# 3. 点击左侧列表中的"今日学习总结"笔记
print('3. 点击今日学习总结笔记...')
# 点击左侧列表中的笔记标题
pyautogui.click(450, 180)  # 笔记标题位置
time.sleep(2)

# 4. 截图确认
pyautogui.screenshot().save('E:\\workspace\\note_clicked.png')

# 5. 滚动到笔记末尾
print('4. 滚动到笔记末尾...')
for i in range(15):
    pyautogui.press('pagedown')
    time.sleep(0.15)
time.sleep(1)

# 6. 添加分隔线
print('5. 添加内容...')

# 尝试直接输入
dlg.type_keys('{ENTER}')
time.sleep(0.2)
dlg.type_keys('---')
time.sleep(0.2)
dlg.type_keys('{ENTER}')

# 7. 添加视频情报
content = """
## 📺 抖音视频情报

### 小白debug - SubAgents/Agent Teams/Swarm
- **视频标题：** SubAgents/Agent Teams/Swarm是什么 7分钟看懂100个Agent团战的技术原理
- **作者：** 小白debug（41.4万粉丝）
- **链接：** https://v.douyin.com/LE35hYZIiwI/
- **数据：** 121.8万点赞

#### 核心概念

**SubAgents（子代理）**
- 专注于单个任务的工作单元
- 结果仅汇报给主智能体

**Agent Teams（代理团队）**
- 多个独立上下文实现并行工作
- 主智能体负责所有协调

**Agent Swarm（代理集群）**
- OpenAI 实验性框架
- 核心：智能体 + 交接机制

**学习价值：** ⭐⭐⭐⭐⭐
"""

pyperclip.copy(content)
time.sleep(0.5)

# 8. 粘贴
print('6. 粘贴内容...')
pyautogui.hotkey('ctrl', 'v')
time.sleep(2)

# 9. 截图确认
pyautogui.screenshot().save('E:\\workspace\\note_final_result.png')
print('Done!')
