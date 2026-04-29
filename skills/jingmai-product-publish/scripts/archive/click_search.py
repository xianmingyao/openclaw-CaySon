# -*- coding: utf-8 -*-
"""点击京麦搜索框并输入"""
import win32gui
import win32api
import win32con
import time

# 京麦窗口HWND
hwnd = 1250920

# 设置焦点到京麦窗口
win32gui.SetForegroundWindow(hwnd)
time.sleep(0.5)

# 搜索框位置（根据截图分析，在页面顶部中央）
# 窗口2560x1392，搜索框大约在 (1280, 200) 附近
search_x = 1280
search_y = 200

# 发送点击事件
win32api.SetCursorPos((search_x, search_y))
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.1)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
print(f"Clicked at ({search_x}, {search_y})")
