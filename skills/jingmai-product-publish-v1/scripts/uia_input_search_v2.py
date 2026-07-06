# -*- coding: utf-8 -*-
"""
点击顶部搜索框并输入"插座"
"""
import platform
if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

print("Clicking top search box and typing '插座'...")

try:
    from pywinauto import Desktop
    import pyautogui
    import time
    
    desktop = Desktop(backend="uia")
    all_windows = desktop.windows()
    
    jingmai = None
    for w in all_windows:
        try:
            title = w.window_text()
            if title == "jd_465d1abd3ee76":
                rect = w.rectangle()
                if rect.width() == 2560 and rect.height() == 1392:
                    jingmai = w
                    break
        except:
            pass
    
    if not jingmai:
        print("Main window not found!")
        exit(1)
    
    print("Found main window")
    jingmai.set_focus()
    time.sleep(0.5)
    
    # 找顶部搜索框 (269, 58) - 这是屏幕坐标
    # 根据截图，搜索框在顶部，识别坐标约(270, 60)
    # 识别尺寸1280x800 vs 实际2560x1392，x比例2, y比例1.74
    # 但UIA返回的已经是屏幕坐标，不需要转换
    
    search_x = 269 + 100  # 搜索框中间偏左
    search_y = 58 + 10    # 搜索框中间
    
    print(f"Clicking at ({search_x}, {search_y})...")
    pyautogui.click(search_x, search_y)
    time.sleep(1)
    
    print("Typing '插座'...")
    # 全选清除
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.3)
    pyautogui.press('delete')
    time.sleep(0.3)
    
    # 输入"插座"
    pyautogui.typewrite("插座", interval=0.15)
    time.sleep(2)
    
    print("Done!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
