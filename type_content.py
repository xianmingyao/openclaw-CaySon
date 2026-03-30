import sys
import time
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
    
    # Press End key to go to end of document
    print("Pressing End key...")
    dc.press("end")
    time.sleep(0.5)
    
    # Type the content
    content = """

=== 2026-03-28 新增内容 ===

## GitHub热门项目

### 程序员Sunday推荐 - Claude Code生态

1. get-shit-done - 39.3k stars - 元提示+上下文工程
2. learn-claude-code - 36.5k stars - 框架教程
3. claude-hud - 11.6k stars - 状态可视化
4. claude-code-action - 6.5k stars - CI/CD集成

### gstack - YC CEO开源项目
- 33.2k stars
- https://github.com/gstack-projects/gstack

## OpenClaw Skills

| 技能 | 状态 |
|------|------|
| agent-browser | 已安装 |
| self-improving | 已安装 |
| skill-vetter | 已安装 |

## 记忆系统
- 云端Milvus (8.137.122.11:19530)
- 本地ChromaDB

## 下一步学习计划
- gstack 源码研究
- get-shit-done 元提示工程"""

    print("Typing content...")
    dc.type_text(content, interval=0.01)
    print("Content typed!")
    
    time.sleep(2)
    dc.screenshot(filename="after_type.png")
    print("Screenshot saved")
    
else:
    print("No Chrome window found!")
