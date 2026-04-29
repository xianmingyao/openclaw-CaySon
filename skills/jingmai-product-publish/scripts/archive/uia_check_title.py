# -*- coding: utf-8 -*-
# 检查商品标题
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
    
    # 获取Edit[1] - 商品标题
    edits = jingmai.descendants(control_type="Edit")
    if len(edits) > 1:
        title_edit = edits[1]
        rect = title_edit.rectangle()
        print(f"Edit[1] (商品标题) at ({rect.left}, {rect.top})")
        
        # 获取文本
        try:
            text = title_edit.text()
            print(f"Title text: '{text}'")
            print(f"Title length: {len(text)}")
        except Exception as e:
            print(f"Error getting text: {e}")
    
    # 也检查页面上的标题相关元素
    print("\nPage elements around title area:")
    all_elements = jingmai.descendants()
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if 400 <= rect.top <= 500 and len(name) > 0:
                ctype = elem.element_info.control_type
                print(f"  {ctype}: '{name[:50]}' at ({rect.left}, {rect.top})")
        except:
            pass

except Exception as e:
    print(f"Error: {e}")
