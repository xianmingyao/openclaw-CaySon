# -*- coding: utf-8 -*-
# 填写SKU价格
import platform
if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

try:
    from pywinauto import Desktop
    import pyautogui
    import time
    import pyperclip
    
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
    for i in range(10):
        pyautogui.scroll(3, x=1280, y=700)
        time.sleep(0.2)
    
    # 获取Edit元素
    edits = jingmai.descendants(control_type="Edit")
    
    print(f"Found {len(edits)} Edit elements")
    
    # 打印所有Edit的位置
    print("\n=== Edit elements ===")
    for i, edit in enumerate(edits):
        try:
            name = edit.element_info.name or ""
            rect = edit.rectangle()
            if rect.width() > 0:
                print(f"  [{i}] '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
