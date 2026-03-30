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
    
    # Take screenshot to see current state
    dc.screenshot(filename="step1.png")
    
    # Click multiple times in the editor area to ensure focus
    for i in range(3):
        editor_x = left + 600
        editor_y = top + 350 + i * 50
        print(f"Clicking on editor at ({editor_x}, {editor_y})...")
        dc.click(editor_x, editor_y)
        time.sleep(0.5)
    
    time.sleep(1)
    dc.screenshot(filename="step2.png")
    
    # Press Ctrl+End to go to end of document
    print("Pressing Ctrl+End...")
    dc.hotkey("ctrl", "end")
    time.sleep(0.5)
    
    # Type the content
    content = """
=== 今日学习总结 2026-03-28 ===

## Claude Code生态5个必知的新工具

### 1. claude-code-action
- Star数：6.5k
- 功能：GitHub Action集成Claude Code到CI/CD
- 特点：140个发布版本，500+部署
- 源码：.claude, .github, base-action, docs, examples, scripts, src, test

### 2. get-shit-done - 39.3k stars - 元提示+上下文工程

### 3. learn-claude-code - 36.5k stars - 框架教程

### 4. claude-hud - 11.6k stars - 状态可视化

### 5. claude-subconscious - 记忆增强

## gstack - YC CEO开源项目
- Star数：33.2k
- 作者：Garry Tan（Y Combinator CEO）
- 功能：YC创业孵化管理平台，15个AI Agent

## OpenClaw Skills
- agent-browser (607K+) - 已安装
- self-improving (380K+) - 已安装
- skill-vetter - 已安装

## 记忆系统
- 云端Milvus (8.137.122.11:19530)
- 本地ChromaDB"""

    print("Typing content...")
    dc.type_text(content, interval=0.003)
    print("Content typed!")
    
    time.sleep(2)
    dc.screenshot(filename="step3.png")
    print("Screenshot saved")
    
else:
    print("No Chrome window found!")
