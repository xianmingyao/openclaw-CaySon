# -*- coding: utf-8 -*-
"""
有道云笔记 - 尝试多种点击方法
"""
from pywinauto import Application
import time
import pyautogui
import win32gui
import win32con
import pyperclip

def activate_window_hwnd(hwnd):
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    time.sleep(0.2)
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.3)
    win32gui.BringWindowToTop(hwnd)
    time.sleep(0.2)

Hwnd = 8850664

print('=== 尝试各种方法 ===')

# 激活窗口
activate_window_hwnd(Hwnd)
time.sleep(0.5)

# 方法1：双击中间区域
print('1. 双击中间区域...')
pyautogui.doubleClick(960, 540)
time.sleep(2)
pyautogui.screenshot().save('E:\\workspace\\try1.png')

# 方法2：右键点击看看有没有菜单
print('2. 右键点击...')
activate_window_hwnd(Hwnd)
time.sleep(0.3)
pyautogui.rightClick(960, 540)
time.sleep(1)
pyautogui.screenshot().save('E:\\workspace\\try2.png')

# 方法3：按 Tab 导航然后回车
print('3. Tab + Enter...')
activate_window_hwnd(Hwnd)
time.sleep(0.3)
pyautogui.press('tab')
time.sleep(0.2)
pyautogui.press('enter')
time.sleep(2)
pyautogui.screenshot().save('E:\\workspace\\try3.png')

# 方法4：尝试使用 ctypes 发送鼠标事件
print('4. 使用 ctypes 发送鼠标事件...')
activate_window_hwnd(Hwnd)
time.sleep(0.3)

import ctypes

# 获取窗口位置
left, top, right, bottom = win32gui.GetWindowRect(Hwnd)
print(f'   窗口位置: ({left}, {top}, {right}, {bottom})')

# 计算屏幕坐标（相对于窗口）
window_x = (left + right) // 2
window_y = (top + bottom) // 2
print(f'   中间位置屏幕坐标: ({window_x}, {window_y})')

# 使用 ctypes 发送鼠标点击
user32 = ctypes.windll.user32

# 鼠标移动
user32.SetCursorPos(window_x, window_y)
time.sleep(0.1)

# 鼠标按下
user32.mouse_event(0x0002, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTDOWN
time.sleep(0.1)
# 鼠标释放
user32.mouse_event(0x0004, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTUP
time.sleep(0.1)
# 再次按下
user32.mouse_event(0x0002, 0, 0, 0, 0)
time.sleep(0.1)
user32.mouse_event(0x0004, 0, 0, 0, 0)

time.sleep(2)
pyautogui.screenshot().save('E:\\workspace\\try4.png')

print('=== 完成 ===')
