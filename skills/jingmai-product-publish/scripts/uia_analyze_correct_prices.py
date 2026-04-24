# -*- coding: utf-8 -*-
# 重新分析正确的价格字段位置
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
    
    # 获取SKU表格的所有列标题
    all_elements = jingmai.descendants()
    
    print("\n=== SKU表格列标题 ===")
    tabs = jingmai.descendants(control_type="TabItem")
    for tab in tabs:
        try:
            name = tab.element_info.name or ""
            rect = tab.rectangle()
            if 900 <= rect.top <= 1050 and name:
                print(f"  '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 打印表头
    print("\n=== 表头 (Header) ===")
    headers = jingmai.descendants(control_type="Header")
    for header in headers:
        try:
            name = header.element_info.name or ""
            rect = header.rectangle()
            if rect.width() > 0:
                print(f"  '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 打印所有文本
    print("\n=== 关键文本 (y=1000-1200) ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if 1000 <= rect.top <= 1200 and name and len(name.strip()) > 1:
                ctype = elem.element_info.control_type
                if ctype in ["Text", "TabItem", "Header"]:
                    print(f"  {ctype}: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
