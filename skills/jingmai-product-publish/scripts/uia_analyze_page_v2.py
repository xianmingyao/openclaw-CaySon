# -*- coding: utf-8 -*-
# 分析当前页面结构
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
    
    # 找所有"请选择"的位置
    print("=== All '请选择' elements ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if name == "请选择" and rect.width() > 0:
                print(f"  at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 找"230V"和"1.8米"的位置
    print("\n=== Current values ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if "230V" in name or "250V" in name or "1.8" in name or "5米" in name:
                print(f"  '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 找ComboBox
    print("\n=== ComboBox elements (y=800-1100) ===")
    combos = jingmai.descendants(control_type="ComboBox")
    for i, combo in enumerate(combos):
        try:
            rect = combo.rectangle()
            if 800 <= rect.top <= 1100:
                print(f"  [{i}] at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 找Edit元素
    print("\n=== Edit elements (y=800-1100) ===")
    edits = jingmai.descendants(control_type="Edit")
    for i, edit in enumerate(edits):
        try:
            name = edit.element_info.name or ""
            rect = edit.rectangle()
            if 800 <= rect.top <= 1100 and rect.width() > 0:
                print(f"  [{i}] '{name}' at ({rect.left}, {rect.top})")
        except:
            pass

except Exception as e:
    print(f"Error: {e}")
