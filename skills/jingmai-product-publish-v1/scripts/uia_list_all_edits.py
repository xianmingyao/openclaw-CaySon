# -*- coding: utf-8 -*-
# 列出所有Edit元素
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
    
    # 获取所有Edit元素
    edits = jingmai.descendants(control_type="Edit")
    print(f"Found {len(edits)} Edit elements:")
    
    for i, edit in enumerate(edits):
        try:
            name = edit.element_info.name or ""
            rect = edit.rectangle()
            if rect.width() > 0:  # 只打印有尺寸的
                print(f"  [{i}] '{name}' at ({rect.left}, {rect.top}) size {rect.width()}x{rect.height()}")
        except:
            pass

except Exception as e:
    print(f"Error: {e}")
