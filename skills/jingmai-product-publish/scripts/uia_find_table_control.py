# -*- coding: utf-8 -*-
# 使用pywinauto直接查找Table/SKU控件
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
    for i in range(15):
        pyautogui.scroll(3, x=1280, y=700)
        time.sleep(0.2)
    
    # 查找Table控件
    print("\n=== Looking for Table controls ===")
    tables = jingmai.descendants(control_type="Table")
    for table in tables:
        try:
            name = table.element_info.name or ""
            rect = table.rectangle()
            print(f"  Table: '{name}' at ({rect.left}, {rect.top}) size({rect.width()}x{rect.height()})")
        except:
            pass
    
    # 查找Custom控件
    print("\n=== Looking for Custom controls ===")
    customs = jingmai.descendants(control_type="Custom")
    for custom in customs:
        try:
            name = custom.element_info.name or ""
            rect = custom.rectangle()
            if rect.width() > 100 and rect.height() > 50:
                print(f"  Custom: '{name}' at ({rect.left}, {rect.top}) size({rect.width()}x{rect.height()})")
        except:
            pass
    
    # 查找包含"SKU"文本的元素
    print("\n=== Elements containing 'SKU' ===")
    all_elements = jingmai.descendants()
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            if "SKU" in name or "规格描述" in name or "规格信息" in name:
                rect = elem.rectangle()
                ctype = elem.element_info.control_type
                print(f"  {ctype}: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
