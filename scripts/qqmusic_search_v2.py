#!/usr/bin/env python3
"""QQ音乐搜索 - 简化版"""
import win32gui
import win32process
import win32api
import pyautogui
import time
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

pid = 42772

def find_window(pid):
    def enum_cb(hwnd, ctx):
        try:
            _, wp = win32process.GetWindowThreadProcessId(hwnd)
            if wp == pid and win32gui.IsWindowVisible(hwnd):
                ctx.append(hwnd)
        except:
            pass
        return True
    windows = []
    win32gui.EnumWindows(enum_cb, windows)
    return windows[0] if windows else None

hwnd = find_window(pid)
if not hwnd:
    print('[FAIL] Window not found')
    exit()

rect = win32gui.GetWindowRect(hwnd)
print(f'Window: {rect}')

# 直接设置前景
print('[Step 1] Setting foreground...')
win32gui.SetForegroundWindow(hwnd)
time.sleep(1)

# 点击窗口顶部中央区域
print('[Step 2] Clicking top center...')
search_x = (rect[0] + rect[2]) // 2  # 窗口中央 x
search_y = rect[1] + 80  # 顶部往下80
print(f'Click at ({search_x}, {search_y})')
pyautogui.click(search_x, search_y)
time.sleep(0.5)

# 输入搜索词
print('[Step 3] Typing search...')
pyautogui.typewrite('发如雪', interval=0.1)
time.sleep(0.3)

print('[Step 4] Pressing Enter...')
pyautogui.press('enter')
time.sleep(2)

# 截图
pyautogui.screenshot('E:/workspace/knowledge/search_result_final.png')
print('[OK] Done')
