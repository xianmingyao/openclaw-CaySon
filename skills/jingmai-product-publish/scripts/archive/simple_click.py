# -*- coding: utf-8 -*-
"""京麦搜索 - 精确坐标点击"""
import win32gui
import win32api
import win32con
import time
import ctypes

user32 = ctypes.windll.user32

# 京麦窗口HWND
JM_HWND = 1250920

# 获取窗口在屏幕上的位置
rect = win32gui.GetWindowRect(JM_HWND)
print(f"窗口区域: {rect}")
# rect = (0, 0, 2560, 1392) 说明窗口占满从(0,0)开始的区域

# 激活窗口
win32gui.SetForegroundWindow(JM_HWND)
time.sleep(0.5)

# 搜索框在窗口内的位置（根据页面布局）
# 从截图看，搜索框大约在 窗口顶部往下 150-200像素 的位置
# 水平居中偏上，大约在 1100-1200 的位置

# 使用绝对屏幕坐标
screen_x, screen_y = 1100, 170

print(f"点击屏幕坐标: ({screen_x}, {screen_y})")

# 点击
win32api.SetCursorPos((screen_x, screen_y))
time.sleep(0.1)
win32api.mouse_event(win32con.MOUSEEVENTF_ABSOLUTE | win32con.MOUSEEVENTF_LEFTDOWN, screen_x * 65535 // 2560, screen_y * 65535 // 1392, 0, 0)
time.sleep(0.1)
win32api.mouse_event(win32con.MOUSEEVENTF_ABSOLUTE | win32con.MOUSEEVENTF_LEFTUP, screen_x * 65535 // 2560, screen_y * 65535 // 1392, 0, 0)
time.sleep(0.3)

# 输入文字
import pyperclip
pyperclip.copy("插座")
time.sleep(0.1)

# Ctrl+V
win32api.keybd_event(0x11, 0, 0, 0)  # Ctrl
time.sleep(0.05)
win32api.keybd_event(0x56, 0, 0, 0)  # V
time.sleep(0.05)
win32api.keybd_event(0x56, 0, win32con.KEYEVENTF_KEYUP, 0)
win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
time.sleep(0.3)

# 回车
win32api.keybd_event(0x0D, 0, 0, 0)
time.sleep(0.05)
win32api.keybd_event(0x0D, 0, win32con.KEYEVENTF_KEYUP, 0)

print("完成")
