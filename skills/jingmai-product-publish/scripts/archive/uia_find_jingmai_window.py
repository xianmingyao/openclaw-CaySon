# -*- coding: utf-8 -*-
# 找到京麦窗口并聚焦
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
                    print(f"Found window: {title}")
                    print(f"  Size: {rect.width()}x{rect.height()}")
                    print(f"  Position: ({rect.left}, {rect.top})")
                    
                    # 聚焦窗口
                    jingmai.set_focus()
                    time.sleep(0.5)
                    print("  Focused!")
                    
                    # 截图
                    print("  Taking screenshot...")
                    break
        except:
            pass
    
    if not jingmai:
        print("Window not found!")
    else:
        print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
