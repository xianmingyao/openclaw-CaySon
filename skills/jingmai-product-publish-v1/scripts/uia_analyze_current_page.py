# -*- coding: utf-8 -*-
# 分析当前页面所有控件
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
    
    # 向下滚动让页面往下走，看到更多内容
    for i in range(5):
        pyautogui.scroll(-2, x=1280, y=700)
        time.sleep(0.2)
    
    # 获取所有可交互元素
    all_elements = jingmai.descendants()
    
    # 打印所有带*号的必填项
    print("\n=== 带*号的必填项 ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if "*" in name and rect.width() > 0:
                ctype = elem.element_info.control_type
                print(f"  {ctype}: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 打印所有Edit
    print("\n=== Edit输入框 ===")
    edits = jingmai.descendants(control_type="Edit")
    for edit in edits:
        try:
            name = edit.element_info.name or ""
            rect = edit.rectangle()
            if rect.width() > 50:
                print(f"  '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 打印所有ComboBox
    print("\n=== ComboBox下拉框 ===")
    combos = jingmai.descendants(control_type="ComboBox")
    for combo in combos:
        try:
            name = combo.element_info.name or ""
            rect = combo.rectangle()
            if rect.width() > 50:
                print(f"  '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
