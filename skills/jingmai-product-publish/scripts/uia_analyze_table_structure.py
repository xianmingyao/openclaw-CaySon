# -*- coding: utf-8 -*-
# 分析SKU表格完整结构
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
    
    # 向上滚动
    for i in range(15):
        pyautogui.scroll(3, x=1280, y=700)
        time.sleep(0.2)
    
    # 获取所有元素
    all_elements = jingmai.descendants()
    
    # 打印y=1000-1400范围内的所有可交互元素
    print("\n=== Interactive elements in SKU area (y=1000-1400) ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            ctype = elem.element_info.control_type
            if 1000 <= rect.top <= 1400 and rect.width() > 0 and name:
                # 只打印关键字段
                if ctype in ["Edit", "ComboBox", "Button", "TabItem", "DataItem"]:
                    print(f"  {ctype}: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 特别打印DataItem
    print("\n=== All DataItems ===")
    data_items = jingmai.descendants(control_type="DataItem")
    for item in data_items:
        try:
            name = item.element_info.name or ""
            rect = item.rectangle()
            if rect.width() > 0:
                print(f"  '{name}' at ({rect.left}, {rect.top}, {rect.width()}x{rect.height()})")
        except:
            pass
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
