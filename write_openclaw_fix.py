import sys
import time
import pyperclip
sys.path.insert(0, r"E:\workspace\skills\desktop-control-1-0-0")
from __init__ import DesktopController
import win32gui
import win32con

dc = DesktopController(failsafe=True)

# Get Chrome window info
def get_window_info(title_substring):
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title_substring in title and "Chrome" in title:
                rect = win32gui.GetWindowRect(hwnd)
                windows.append((title, rect, hwnd))
        return True
    
    windows = []
    win32gui.EnumWindows(callback, windows)
    return windows

# Find the Youdao Chrome window
print("Finding Chrome windows...")
chrome_windows = get_window_info("有道云笔记")
if not chrome_windows:
    chrome_windows = get_window_info("Chrome")

if chrome_windows:
    title, rect, hwnd = chrome_windows[0]
    left, top, right, bottom = rect
    print(f"Window: {title}")
    
    # Activate the window
    win32gui.SetForegroundWindow(hwnd)
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    time.sleep(0.5)
    
    # Click on the editor area
    editor_x = left + 600
    editor_y = top + 400
    print(f"Clicking on editor at ({editor_x}, {editor_y})...")
    dc.click(editor_x, editor_y)
    time.sleep(1)
    
    # Select all and delete existing content
    print("Selecting all content...")
    dc.hotkey("ctrl", "a")
    time.sleep(0.5)
    dc.press("delete")
    time.sleep(0.5)
    
    # Copy content to clipboard
    content = """OpenClaw 问题修复指南

## 好消息：核心已正常运行

• OpenClaw Gateway 已成功启动
• 证据：[gateway] listening on ws://127.0.0.1:18789

## 当前报错原因（两个小问题）

1. 飞书插件版本不兼容
   - 原因：函数不存在

2. Discord 插件网络超时
   - 原因：国内无法访问

## 10秒清理方案

第一步：删除损坏的插件
• 命令：rd /s /q "C:\\Users\\...\\.openclaw\\extensions\\feishu"

第二步：覆盖配置文件
• 将 plugins 配置重置为空白状态
• 清空 paths、entries、allow 列表
• 清空 discord 配置

## 验证与结果

重新启动：openclaw gateway

预期效果：
• 系统完全干净，无报错
• 核心功能恢复：
  - RAG（检索增强生成）
  - 自动化
  - Skills（技能）
  - Vector DB（向量库）

## 方法论总结

1. 隔离主程序与插件
   - 确认核心网关正常是第一步

2. 快速剔除法
   - 第三方插件不兼容或网络限制
   - 直接删除插件 + 重置配置

3. 配置重置
   - 通过命令行直接写入正确配置
   - 避免手动编辑可能带来的错误"""

    pyperclip.copy(content)
    print("Content copied to clipboard")
    
    # Paste using Ctrl+V
    print("Pasting content...")
    dc.hotkey("ctrl", "v")
    print("Content pasted!")
    
    time.sleep(2)
    dc.screenshot(filename="openclaw_fix.png")
    print("Screenshot saved")
    
else:
    print("No Chrome window found!")
