# -*- coding: utf-8 -*-
# 深度分析页面结构
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
    
    # 获取所有元素
    all_elements = jingmai.descendants()
    
    # 搜索所有包含"孔"的元素
    print("=== Elements containing '孔' ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if "孔" in name:
                ctype = elem.element_info.control_type
                print(f"  {ctype}: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 打印y=800-900范围的所有Text元素
    print("\n=== All Text elements in y=800-900 ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            ctype = elem.element_info.control_type
            if ctype == "Text" and 800 <= rect.top <= 900:
                print(f"  '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 打印y=800-900范围的Edit元素
    print("\n=== All Edit elements in y=800-900 ===")
    edits = jingmai.descendants(control_type="Edit")
    for i, edit in enumerate(edits):
        try:
            name = edit.element_info.name or ""
            rect = edit.rectangle()
            if 800 <= rect.top <= 900:
                print(f"  [{i}] '{name}' at ({rect.left}, {rect.top})")
        except:
            pass

except Exception as e:
    print(f"Error: {e}")
