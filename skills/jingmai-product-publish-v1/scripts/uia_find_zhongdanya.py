# -*- coding: utf-8 -*-
"""
全面搜索"中低压配电"和"插座"元素
"""
import platform
if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

print("Searching for category elements...")

try:
    from pywinauto import Desktop
    import pyautogui
    import time
    
    desktop = Desktop(backend="uia")
    all_windows = desktop.windows()
    
    jingmai = None
    for w in all_windows:
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
        print("Main window not found!")
        exit(1)
    
    print("Found main window")
    jingmai.set_focus()
    time.sleep(0.5)
    
    # 搜索所有元素类型
    all_elements = jingmai.descendants()
    print(f"Total elements: {len(all_elements)}")
    
    # 搜索关键词
    keywords = ["中低压配电", "插座", "工业品"]
    
    for keyword in keywords:
        print(f"\n=== Searching for '{keyword}' ===")
        count = 0
        for elem in all_elements:
            try:
                name = elem.element_info.name or ""
                ctype = elem.element_info.control_type or ""
                rect = elem.rectangle()
                
                if keyword in name:
                    # 排除已选类目路径中的（通常在顶部显示）
                    if rect.top < 200:
                        print(f"  [TOP BAR] {ctype}: '{name}' at ({rect.left}, {rect.top})")
                    else:
                        print(f"  [MAIN AREA] {ctype}: '{name}' at ({rect.left}, {rect.top})")
                    count += 1
            except:
                pass
        
        if count == 0:
            print(f"  Not found!")
        else:
            print(f"  Total: {count}")
    
    # 打印y=260-350范围内的所有可点击元素（类目区域）
    print("\n=== Clickable elements in category area (y: 260-350) ===")
    for elem in all_elements:
        try:
            ctype = elem.element_info.control_type
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            
            # 只看类目区域
            if 260 < rect.top < 350 and name and len(name.strip()) > 1:
                # 检查是否是可点击类型
                if ctype in ["Hyperlink", "Button", "Text", "Custom"]:
                    print(f"  {ctype}: '{name.strip()}' at ({rect.left}, {rect.top})")
        except:
            pass
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
