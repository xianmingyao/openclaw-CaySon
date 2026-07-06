# -*- coding: utf-8 -*-
# 搜索包含完整路径"工业品 > 中低压配电 > 插座"的元素
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
    
    # 搜索所有包含"工业品"的元素
    print("Searching for '工业品' in all elements...")
    all_elements = jingmai.descendants()
    
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            ctype = elem.element_info.control_type
            
            # 检查是否包含关键词
            if "工业品" in name or "中低压" in name or "配电" in name:
                print(f"  {ctype}: '{name}' at ({rect.left}, {rect.top})")
                
                # 如果找到"工业品 > 中低压配电 > 插座"这样的完整路径，立即点击
                if "工业品" in name and "中低压" in name and "配电" in name:
                    print(f"\n*** FOUND COMPLETE PATH! Clicking at ({rect.left}, {rect.top})...")
                    try:
                        elem.invoke()
                    except:
                        pyautogui.click(rect.left + 50, rect.top + 5)
                    time.sleep(3)
                    print("Clicked!")
                    break
        except:
            pass
    
    # 如果没找到完整路径，尝试点击各个部分
    print("\nTrying individual parts...")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if rect.top >= 640 and rect.top <= 700:
                if "工业品" in name:
                    print(f"Clicking '工业品' at ({rect.left}, {rect.top})...")
                    pyautogui.click(rect.left + 30, rect.top + 5)
                    time.sleep(2)
                    break
        except:
            pass

except Exception as e:
    print(f"Error: {e}")
