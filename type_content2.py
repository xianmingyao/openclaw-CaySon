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
    width = right - left
    height = bottom - top
    print(f"Window: {title}")
    print(f"  Position: left={left}, top={top}")
    print(f"  Size: {width}x{height}")
    
    # Activate the window
    win32gui.SetForegroundWindow(hwnd)
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    time.sleep(0.5)
    
    # The main content area should be on the right side of the window
    # Let's click in the center-right area (where the editor typically is)
    # Assuming sidebar is about 300px wide, editor starts around x=350
    editor_x = left + 600  # Center of the content area
    editor_y = top + 400   # Middle of the window
    
    print(f"Clicking on editor area at ({editor_x}, {editor_y})...")
    dc.click(editor_x, editor_y)
    time.sleep(1)
    
    # Now press Ctrl+End to go to end of document
    print("Pressing Ctrl+End...")
    dc.hotkey("ctrl", "end")
    time.sleep(0.5)
    
    # Type the content
    content = """

=== 2026-03-28 新增内容 ===

## GitHub热门项目

1. get-shit-done - 39.3k stars - 元提示+上下文工程
2. learn-claude-code - 36.5k stars - 框架教程
3. claude-hud - 11.6k stars - 状态可视化
4. claude-code-action - 6.5k stars - CI/CD集成

### gstack - YC CEO开源项目
- 33.2k stars

## OpenClaw Skills
- agent-browser (已安装)
- self-improving (已安装)
- skill-vetter (已安装)

## 记忆系统
- 云端Milvus (8.137.122.11:19530)
- 本地ChromaDB"""

    print("Typing content...")
    dc.type_text(content, interval=0.005)
    print("Content typed!")
    
    time.sleep(2)
    dc.screenshot(filename="after_type2.png")
    print("Screenshot saved")
    
else:
    print("No Chrome window found!")
