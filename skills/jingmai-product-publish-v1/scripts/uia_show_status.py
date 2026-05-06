# -*- coding: utf-8 -*-
# 查看当前状态和可填写项
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
    
    # 打印y=800-1300范围的元素（商品属性区域）
    print("\n=== Elements in y=800-1300 (属性区域) ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            ctype = elem.element_info.control_type
            if 800 <= rect.top <= 1300 and name and len(name.strip()) > 1:
                print(f"  {ctype}: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 打印所有按钮
    print("\n=== Buttons ===")
    buttons = jingmai.descendants(control_type="Button")
    for btn in buttons:
        try:
            name = btn.element_info.name or ""
            if name and len(name.strip()) > 1:
                rect = btn.rectangle()
                print(f"  '{name}' at ({rect.left}, {rect.top})")
        except:
            pass

except Exception as e:
    print(f"Error: {e}")
