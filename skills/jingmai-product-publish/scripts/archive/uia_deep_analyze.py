# -*- coding: utf-8 -*-
# 深度分析页面结构，找电流输入框
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
    
    # 找所有与"电流"相关的元素
    all_elements = jingmai.descendants()
    
    print("=== Elements containing '电流' ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if "电流" in name:
                ctype = elem.element_info.control_type
                print(f"  {ctype}: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 找y=1000-1100范围内的所有元素
    print("\n=== All elements in y=1000-1100 ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            ctype = elem.element_info.control_type
            if 1000 <= rect.top <= 1100 and name and len(name.strip()) > 0:
                print(f"  {ctype}: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 找y=1200-1350范围内的按钮（发布相关）
    print("\n=== Buttons in y=1200-1350 ===")
    buttons = jingmai.descendants(control_type="Button")
    for btn in buttons:
        try:
            name = btn.element_info.name or ""
            rect = btn.rectangle()
            if 1200 <= rect.top <= 1350 and name and len(name.strip()) > 1:
                print(f"  '{name}' at ({rect.left}, {rect.top})")
        except:
            pass

except Exception as e:
    print(f"Error: {e}")
