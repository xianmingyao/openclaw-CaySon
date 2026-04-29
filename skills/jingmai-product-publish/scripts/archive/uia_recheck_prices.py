# -*- coding: utf-8 -*-
# 重新分析价格字段位置
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
    
    # 向上滚动到正确位置
    for i in range(12):
        pyautogui.scroll(3, x=1280, y=700)
        time.sleep(0.2)
    
    # 获取所有包含"价"的元素
    all_elements = jingmai.descendants()
    
    print("\n=== 包含'价'的元素 ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if "价" in name:
                ctype = elem.element_info.control_type
                print(f"  {ctype}: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 获取所有TabItem（SKU表格列）
    print("\n=== SKU表格列 (y=900-1000) ===")
    tabs = jingmai.descendants(control_type="TabItem")
    for tab in tabs:
        try:
            name = tab.element_info.name or ""
            rect = tab.rectangle()
            if 900 <= rect.top <= 1000 and name:
                print(f"  '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
