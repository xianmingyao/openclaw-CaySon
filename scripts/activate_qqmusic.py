#!/usr/bin/env python3
"""激活QQ音乐窗口"""
import win32gui
import win32api
import win32process
import time
import pyautogui
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

pid = 42772

def find_window_by_pid(target_pid):
    result = {}
    def enum_cb(hwnd, ctx):
        try:
            _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
            if window_pid == target_pid and win32gui.IsWindowVisible(hwnd):
                result['hwnd'] = hwnd
                result['title'] = win32gui.GetWindowText(hwnd)
                result['rect'] = win32gui.GetWindowRect(hwnd)
        except:
            pass
        return True
    win32gui.EnumWindows(enum_cb, None)
    return result

print('Finding window by PID...')
info = find_window_by_pid(pid)

if info:
    print('Found:', info['title'])
    print('Rect:', info['rect'])

    hwnd = info['hwnd']
    rect = info['rect']
    win_left, win_top = rect[0], rect[1]

    print('\nActivating window...')
    win32gui.SetForegroundWindow(hwnd)
    win32api.Sleep(1000)

    # 截图确认
    pyautogui.screenshot('E:/workspace/knowledge/qqmusic_activated.png')
    print('Screenshot saved')
else:
    print('Window not found!')
