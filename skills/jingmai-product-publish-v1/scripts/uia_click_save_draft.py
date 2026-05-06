# -*- coding: utf-8 -*-
# 点击保存草稿
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
    
    # 点击"保存草稿"菜单
    print("Clicking 保存草稿 at (1275, 1336)...")
    pyautogui.click(1275, 1336)
    time.sleep(2)
    
    # 截图看结果
    print("Done!")

except Exception as e:
    print(f"Error: {e}")
