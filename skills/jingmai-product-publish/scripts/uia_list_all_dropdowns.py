# -*- coding: utf-8 -*-
# 列出当前所有下拉框
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
    
    # 找所有ComboBox和"请选择"
    all_elements = jingmai.descendants()
    
    print("\n=== ComboBoxes (y=800-1100) ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            ctype = elem.element_info.control_type
            if ctype == "ComboBox" and 800 <= rect.top <= 1100:
                print(f"  ComboBox at ({rect.left}, {rect.top})")
        except:
            pass
    
    print("\n=== '请选择' texts (y=800-1100) ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if name == "请选择" and 800 <= rect.top <= 1100:
                print(f"  '请选择' at ({rect.left}, {rect.top})")
        except:
            pass
    
    print("\n=== Labels (必填属性相关) ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if 800 <= rect.top <= 1100 and len(name) > 1:
                # 检查是否是label
                ctype = elem.element_info.control_type
                if ctype in ["Text", "Static"]:
                    print(f"  Text '{name}' at ({rect.left}, {rect.top})")
        except:
            pass

except Exception as e:
    print(f"Error: {e}")
