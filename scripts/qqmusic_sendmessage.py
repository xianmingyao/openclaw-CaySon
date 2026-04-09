#!/usr/bin/env python3
"""QQ音乐搜索 - 使用Windows API SendMessage"""
import win32gui
import win32process
import win32api
import win32con
import time
import pyautogui
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def find_window_by_pid(pid):
    def enum_cb(hwnd, ctx):
        try:
            _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
            if window_pid == pid and win32gui.IsWindowVisible(hwnd):
                ctx.append(hwnd)
        except:
            pass
        return True
    windows = []
    win32gui.EnumWindows(enum_cb, windows)
    return windows[0] if windows else None

pid = 42772
hwnd = find_window_by_pid(pid)

if not hwnd:
    print('[FAIL] Window not found')
    exit()

rect = win32gui.GetWindowRect(hwnd)
print(f'Window: {rect}')

# 激活窗口
print('\n[Step 1] Activating window...')
win32gui.SetForegroundWindow(hwnd)
time.sleep(0.5)

# 尝试使用 WM_ACTIVATE
win32gui.SendMessage(hwnd, win32con.WM_ACTIVATE, 1, 0)
time.sleep(0.3)

# 点击窗口内部以激活
pyautogui.click(rect[0] + 500, rect[1] + 500)
time.sleep(0.3)

# 发送 Ctrl+F
print('\n[Step 2] Sending Ctrl+F...')
win32api.keybd_event(0x11, 0, 0, 0)  # Ctrl down
win32api.keybd_event(0x46, 0, 0, 0)  # F down
time.sleep(0.05)
win32api.keybd_event(0x46, 0, win32con.KEYEVENTF_KEYUP, 0)  # F up
win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)  # Ctrl up
time.sleep(0.5)

# 直接发送文本消息到窗口
print('\n[Step 3] Sending text...')
# 使用 WM_CHAR 发送字符
text = '发如雪'
for char in text:
    win32api.SendMessage(hwnd, win32con.WM_CHAR, ord(char), 0)
    time.sleep(0.1)

time.sleep(0.3)

# 发送回车
print('\n[Step 4] Sending Enter...')
win32api.keybd_event(0x0D, 0, 0, 0)  # Enter down
time.sleep(0.05)
win32api.keybd_event(0x0D, 0, win32con.KEYEVENTF_KEYUP, 0)  # Enter up
time.sleep(2)

print('\n[OK] Done')
