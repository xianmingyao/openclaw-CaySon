# -*- coding: utf-8 -*-
# 使用set_edit_text填写商品标题
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
    
    # 获取所有Edit
    edits = jingmai.descendants(control_type="Edit")
    
    # Edit[1] = 商品标题
    if len(edits) > 1:
        title_edit = edits[1]
        rect = title_edit.rectangle()
        print(f"Edit[1] (商品标题) at ({rect.left}, {rect.top})")
        
        # 使用set_edit_text
        title = "公牛BULL插座B5440系列86型暗装墙壁开关插座多位电源插座"
        print(f"Setting title: {title}")
        title_edit.set_edit_text(title)
        time.sleep(1)
        print("Done!")
    else:
        print("Not enough Edit elements!")

except Exception as e:
    print(f"Error: {e}")
