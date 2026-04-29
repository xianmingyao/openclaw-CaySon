# -*- coding: utf-8 -*-
# 点击搜索结果中的"工业品>中低压配电>插座"
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
    
    # 查找搜索结果 - "工业品 > 中低压配电 > 插座"
    print("Looking for search result...")
    all_elements = jingmai.descendants()
    
    # 先打印y=200-400范围的元素（搜索结果区域）
    print("Elements in y=200-400 (search result area):")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            ctype = elem.element_info.control_type
            if 200 <= rect.top <= 400 and name and len(name.strip()) > 1:
                print(f"  {ctype}: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 查找并点击"工业品"相关的搜索结果
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            # 搜索结果通常在y=200-350范围
            if 200 <= rect.top <= 350:
                if "工业品" in name and "中低压" in name:
                    print(f"\nFound: '{name}' at ({rect.left}, {rect.top})")
                    try:
                        elem.invoke()
                    except:
                        pyautogui.click(rect.left + 50, rect.top + 5)
                    time.sleep(2)
                    print("Clicked!")
                    break
        except:
            pass

except Exception as e:
    print(f"Error: {e}")
