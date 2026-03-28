# -*- coding: utf-8 -*-
"""
查找有道云笔记 Chrome 窗口
"""
import win32gui
import win32con
import win32api
import time
import pyautogui

# 枚举所有窗口
all_windows = []
def callback(hwnd, windows):
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd)
        classname = win32gui.GetClassName(hwnd)
        if title and ('chrome' in title.lower() or 'youdao' in title.lower() or 'note' in title.lower()):
            all_windows.append({
                'hwnd': hwnd,
                'title': title,
                'class': classname
            })
win32gui.EnumWindows(callback, all_windows)

print(f"找到 {len(all_windows)} 个相关窗口:\n")
for w in all_windows:
    print(f"HWND: {w['hwnd']}")
    print(f"  Title: {w['title']}")
    print(f"  Class: {w['class']}")
    print()
