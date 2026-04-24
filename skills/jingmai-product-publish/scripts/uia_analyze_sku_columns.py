# -*- coding: utf-8 -*-
# 分析SKU表格列和数据位置
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
    
    # 向上滚动（让页面向下走）
    for i in range(15):
        pyautogui.scroll(3, x=1280, y=700)
        time.sleep(0.2)
    
    # 获取SKU表格的TabItem列
    all_elements = jingmai.descendants()
    
    print("\n=== SKU表格列 (TabItem y=1100-1200) ===")
    tabs = jingmai.descendants(control_type="TabItem")
    for tab in tabs:
        try:
            name = tab.element_info.name or ""
            rect = tab.rectangle()
            if 1100 <= rect.top <= 1200 and name and len(name) < 20:
                print(f"  '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 获取表头
    print("\n=== 表头 (Header y=1150-1250) ===")
    headers = jingmai.descendants(control_type="Header")
    for header in headers:
        try:
            name = header.element_info.name or ""
            rect = header.rectangle()
            if 1150 <= rect.top <= 1250 and rect.width() > 0:
                print(f"  '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 获取DataItem数据行
    print("\n=== 数据行 (DataItem y=1200-1300) ===")
    data_items = jingmai.descendants(control_type="DataItem")
    for item in data_items:
        try:
            name = item.element_info.name or ""
            rect = item.rectangle()
            if 1200 <= rect.top <= 1300 and rect.width() > 0:
                print(f"  '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
