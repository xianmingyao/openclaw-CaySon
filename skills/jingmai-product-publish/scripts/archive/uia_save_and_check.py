# -*- coding: utf-8 -*-
# 保存草稿
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
    
    # 找保存草稿
    menu_items = jingmai.descendants(control_type="MenuItem")
    
    for item in menu_items:
        try:
            name = item.element_info.name or ""
            if "草稿" in name:
                print(f"Found: '{name}'")
                item.invoke()
                print("Saved!")
                break
        except:
            pass
    
    time.sleep(2)
    print("Done!")

except Exception as e:
    print(f"Error: {e}")
