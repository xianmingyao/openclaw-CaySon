#!/usr/bin/env python3
"""QQ音乐搜索发如雪 - 最终版"""
import win32gui
import win32process
import win32api
import win32con
import win32ui
from PIL import Image
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

def main():
    hwnd = find_window(pid)
    if not hwnd:
        print('[FAIL] Window not found')
        return

    rect = win32gui.GetWindowRect(hwnd)
    win_left, win_top, win_right, win_bottom = rect
    print(f'Window: ({win_left}, {win_top}) to ({win_right}, {win_bottom})')
    print(f'Size: {win_right-win_left} x {win_bottom-win_top}')

    # 激活窗口
    print('\n[Step 1] Activating window...')
    win32gui.SetForegroundWindow(hwnd)
    win32api.Sleep(1000)

    # 尝试点击搜索框 - 窗口顶部中央
    print('\n[Step 2] Clicking search box...')
    search_x = win_left + 525
    search_y = win_top + 55
    print(f'Click at ({search_x}, {search_y})')
    pyautogui.click(search_x, search_y)
    time.sleep(0.5)

    # 截图确认
    pyautogui.screenshot('E:/workspace/knowledge/step1_click.png')

    print('\n[Step 3] Typing search keyword...')
    pyautogui.typewrite('发如雪', interval=0.1)
    time.sleep(0.3)

    print('\n[Step 4] Pressing Enter...')
    pyautogui.press('enter')
    time.sleep(3)

    print('\n[Step 5] Clicking first result...')
    # 点击搜索结果中的第一首歌
    play_x = win_left + 180
    play_y = win_top + 280
    print(f'Click at ({play_x}, {play_y})')
    pyautogui.click(play_x, play_y)
    time.sleep(1)

    # 截图最终结果
    pyautogui.screenshot('E:/workspace/knowledge/step2_result.png')

    print('\n[OK] Done!')

if __name__ == '__main__':
    main()
