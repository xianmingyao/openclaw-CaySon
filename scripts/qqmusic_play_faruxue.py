#!/usr/bin/env python3
"""QQ音乐搜索并播放发如雪"""
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

def main():
    print('=' * 50)
    print('QQMusic Search and Play')
    print('=' * 50)

    info = find_window_by_pid(pid)
    if not info:
        print('[FAIL] QQMusic window not found!')
        return

    hwnd = info['hwnd']
    rect = info['rect']
    win_left, win_top, win_right, win_bottom = rect

    print('\n[Step 1] Activating window...')
    win32gui.SetForegroundWindow(hwnd)
    win32api.Sleep(1000)
    print(f'Window active: {win_right-win_left}x{win_bottom-win_top}')

    print('\n[Step 2] Clicking search box...')
    # 搜索框位置 - 基于窗口坐标
    search_x = win_left + 380
    search_y = win_top + 55
    print(f'Click at ({search_x}, {search_y})')
    pyautogui.click(search_x, search_y)
    time.sleep(0.5)

    print('\n[Step 3] Typing search keyword...')
    pyautogui.typewrite('发如雪', interval=0.1)
    time.sleep(0.3)

    print('\n[Step 4] Pressing Enter...')
    pyautogui.press('enter')
    time.sleep(3)

    print('\n[Step 5] Taking screenshot...')
    pyautogui.screenshot('E:/workspace/knowledge/qqmusic_search_result.png')
    print('Screenshot saved')

    print('\n[Step 6] Clicking play button...')
    # 播放按钮位置 - 搜索结果列表中的第一个
    play_x = win_left + 180
    play_y = win_top + 250
    print(f'Click at ({play_x}, {play_y})')
    pyautogui.click(play_x, play_y)
    time.sleep(1)

    print('\n' + '=' * 50)
    print('Done!')

if __name__ == '__main__':
    main()
