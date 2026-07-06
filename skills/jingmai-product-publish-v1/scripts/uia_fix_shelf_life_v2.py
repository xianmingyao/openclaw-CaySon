# -*- coding: utf-8 -*-
# 修正保质期字段 - 使用正确坐标
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
    
    # 向上滚动
    for i in range(15):
        pyautogui.scroll(3, x=1280, y=700)
        time.sleep(0.2)
    
    # 保质期Edit at (628, 860)
    print("Clicking 保质期 at (628, 860)...")
    pyautogui.click(628, 860)
    time.sleep(0.5)
    
    # 清除并输入365
    pyautogui.press('delete')
    time.sleep(0.2)
    pyautogui.press('delete')
    time.sleep(0.2)
    pyautogui.typewrite('365', interval=0.1)
    time.sleep(0.5)
    
    print("Done!")

except Exception as e:
    print(f"Error: {e}")
