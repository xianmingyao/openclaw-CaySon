# -*- coding: utf-8 -*-
# 查找并点击"中低压配电"
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
    
    # 搜索包含"中低压配电"或"插座"的元素
    print("Looking for keywords...")
    all_elements = jingmai.descendants()
    
    targets = []
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            ctype = elem.element_info.control_type
            # 在y=400-700范围内找（近期使用类目区域）
            if 400 < rect.top < 700:
                if "中低压" in name or "配电" in name or "插座" in name:
                    print(f"  {ctype} '{name}' at ({rect.left}, {rect.top})")
                    targets.append((elem, name, rect))
        except:
            pass
    
    # 也打印y=400-700范围内的所有文本元素
    print("\nAll elements in y=400-700:")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if 400 < rect.top < 700 and name and len(name) > 1:
                ctype = elem.element_info.control_type
                print(f"  {ctype} '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 点击第一个目标
    if targets:
        elem, name, rect = targets[0]
        print(f"\nClicking '{name}' at ({rect.left}, {rect.top})...")
        try:
            elem.invoke()
        except:
            pyautogui.click(rect.left + 50, rect.top + 5)
        time.sleep(2)
        print("Clicked!")

except Exception as e:
    print(f"Error: {e}")
