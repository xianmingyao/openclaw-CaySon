# -*- coding: utf-8 -*-
# 使用set_edit_text方法输入
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
    
    # 获取Edit[1]
    edits = jingmai.descendants(control_type="Edit")
    search_edit = edits[1]
    rect = search_edit.rectangle()
    print(f"Edit[1] at ({rect.left}, {rect.top}) size {rect.width()}x{rect.height()}")
    
    # 使用set_edit_text
    print("Using set_edit_text...")
    search_edit.set_edit_text("插座")
    time.sleep(1)
    
    # 按回车
    print("Pressing Enter...")
    pyautogui.press("enter")
    time.sleep(3)
    
    print("Done!")

except Exception as e:
    print(f"Error: {e}")
