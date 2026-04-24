# -*- coding: utf-8 -*-
# 分析草稿列表页面结构
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
    
    # 获取所有元素
    all_elements = jingmai.descendants()
    
    # 打印超链接
    print("\n=== Hyperlinks ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if name and len(name.strip()) > 0:
                ctype = elem.element_info.control_type
                if ctype == "Hyperlink":
                    print(f"  '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 打印按钮
    print("\n=== Buttons ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if name and len(name.strip()) > 0:
                ctype = elem.element_info.control_type
                if ctype == "Button":
                    print(f"  '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
