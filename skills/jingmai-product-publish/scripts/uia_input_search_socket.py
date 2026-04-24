# -*- coding: utf-8 -*-
# 在Edit[1]类目搜索框输入"插座"并搜索
import platform
if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

try:
    from pywinauto import Desktop
    import pyautogui
    import time
    
    desktop = Desktop(backend="uia")
    
    jingmai = None
    for w in desktop.windows():
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
        print("Window not found!")
        exit(1)
    
    print("Found window")
    jingmai.set_focus()
    time.sleep(0.5)
    
    # 使用Edit[1] - 类目搜索框 (551, 220)
    print("Clicking Edit[1] at (551, 220)...")
    pyautogui.click(551, 220)
    time.sleep(0.5)
    
    # 清除
    print("Clearing...")
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.2)
    pyautogui.press('delete')
    time.sleep(0.2)
    
    # 输入"插座"
    print("Inputting '插座'...")
    pyautogui.typewrite("插座", interval=0.1)
    time.sleep(0.5)
    
    # 按回车搜索
    print("Pressing Enter...")
    pyautogui.press("enter")
    time.sleep(3)
    
    print("Done!")

except Exception as e:
    print(f"Error: {e}")
