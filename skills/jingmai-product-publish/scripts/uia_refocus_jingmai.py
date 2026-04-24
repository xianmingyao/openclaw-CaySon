# -*- coding: utf-8 -*-
# 重新聚焦京麦窗口
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
    
    print(f"Found window: {jingmai.window_text()}")
    print(f"Rect: {jingmai.rectangle()}")
    
    # 聚焦窗口
    jingmai.set_focus()
    time.sleep(1)
    
    # 截图
    print("Taking screenshot...")
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
