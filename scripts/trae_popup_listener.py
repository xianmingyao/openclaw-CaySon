#!/usr/bin/env python
"""Trae CN 弹窗监听器 - 检测并自动关闭 ruff check 弹窗"""
import pyautogui
import time
import pygetwindow as gw
import sys

print('=== Trae CN 弹窗监听已启动 ===')
print('每60秒检测一次 ruff check 弹窗')
print('按 Ctrl+C 停止')
print()

def check_and_close_popup():
    """检测并关闭弹窗"""
    try:
        # 激活 Trae CN 窗口
        windows = gw.getAllWindows()
        trae_window = None
        for w in windows:
            if 'Trae CN' in w.title or 'trae' in w.title.lower():
                trae_window = w
                break
        
        if trae_window:
            try:
                trae_window.activate()
                time.sleep(0.5)
            except:
                pass
        
        # 截图检测
        screenshot_path = r'E:\workspace\scripts\screenshots\popup_check.png'
        pyautogui.screenshot(screenshot_path)
        
        # 尝试在屏幕中央区域查找蓝色按钮
        # ruff check 弹窗通常有蓝色确认按钮
        try:
            # 屏幕中央区域
            region = (600, 200, 1400, 800)
            btn = pyautogui.locateCenterOnScreen(
                screenshot_path, 
                region=region, 
                confidence=0.6
            )
            if btn:
                print(f'{time.strftime("%H:%M:%S")} 检测到弹窗!')
                pyautogui.press('1')
                time.sleep(0.5)
                pyautogui.screenshot(r'E:\workspace\scripts\screenshots\popup_closed.png')
                print('已按 1 关闭弹窗')
                return True
        except Exception as e:
            # 没找到按钮也正常
            pass
        
        return False
        
    except Exception as e:
        print(f'检测异常: {e}')
        return False

# 运行一次测试
print('测试检测功能...')
check_and_close_popup()
print('监听循环开始，每60秒检测一次...')
print()

# 主循环
while True:
    try:
        time.sleep(60)
        check_and_close_popup()
    except KeyboardInterrupt:
        print('\n监听已停止')
        sys.exit(0)
    except Exception as e:
        print(f'循环异常: {e}')
        time.sleep(60)
