# -*- coding: utf-8 -*-
# 选择1.8米电缆长度
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
    
    # 点击1.8米 - (1429, 992)
    print("Clicking 1.8米 at (1429, 992)...")
    pyautogui.click(1429, 992)
    time.sleep(1.5)
    
    print("Done!")

except Exception as e:
    print(f"Error: {e}")
