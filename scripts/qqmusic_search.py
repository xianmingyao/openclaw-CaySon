#!/usr/bin/env python3
"""QQ音乐搜索发如雪"""
import win32gui
import win32api
import time
import pyautogui
import sys
import io

# 解决Windows控制台GBK编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def find_qqmusic():
    """找到QQMusic窗口"""
    result = {}
    def enum_cb(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title and 'QQ' in title:
                rect = win32gui.GetWindowRect(hwnd)
                result['hwnd'] = hwnd
                result['title'] = title
                result['rect'] = rect
                print(f'Found: {title}')
        return True
    win32gui.EnumWindows(enum_cb, None)
    return result

def main():
    print('=' * 50)
    print('QQMusic Search Automation')
    print('=' * 50)
    
    print('\n[Step 1] Finding QQMusic window...')
    info = find_qqmusic()
    
    if not info:
        print('[FAIL] QQMusic not found!')
        return
    
    hwnd = info['hwnd']
    rect = info['rect']
    
    print('\n[Step 2] Activating window...')
    win32gui.SetForegroundWindow(hwnd)
    win32api.Sleep(1000)
    
    # 更新窗口位置
    rect = win32gui.GetWindowRect(hwnd)
    win_left, win_top, win_right, win_bottom = rect
    print(f'Window: {win_right-win_left} x {win_bottom-win_top}')
    
    print('\n[Step 3] Clicking search box...')
    # 搜索框位置 - QQMusic窗口顶部区域
    search_x = win_left + 400
    search_y = win_top + 55
    print(f'Click at ({search_x}, {search_y})')
    pyautogui.click(search_x, search_y)
    time.sleep(0.5)
    
    print('\n[Step 4] Typing search keyword...')
    pyautogui.typewrite('发如雪', interval=0.1)
    time.sleep(0.3)
    
    print('\n[Step 5] Pressing Enter...')
    pyautogui.press('enter')
    time.sleep(3)
    
    print('\n[Step 6] Clicking play button...')
    # 播放按钮位置 - 搜索结果中的第一个
    play_x = win_left + 180
    play_y = win_top + 250
    print(f'Click at ({play_x}, {play_y})')
    pyautogui.click(play_x, play_y)
    
    print('\n' + '=' * 50)
    print('Done!')

if __name__ == '__main__':
    main()
