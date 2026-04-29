# -*- coding: utf-8 -*-
# 查找近期使用类目中的蓝色链接并点击
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
    
    # 查找所有Hyperlink
    print("All Hyperlinks in window:")
    links = jingmai.descendants(control_type="Hyperlink")
    for i, link in enumerate(links):
        try:
            name = link.element_info.name or ""
            rect = link.rectangle()
            if name and len(name) > 1:
                print(f"  [{i}] '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 查找y=600-750范围的所有元素
    print("\nAll clickable elements in y=600-750:")
    all_elements = jingmai.descendants()
    clickable_types = ["Hyperlink", "Button", "ListItem", "Custom", "Text"]
    
    targets = []
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            ctype = elem.element_info.control_type
            if 600 <= rect.top <= 750 and name and len(name.strip()) > 1:
                if ctype in clickable_types:
                    targets.append((elem, name, rect, ctype))
                    print(f"  {ctype}: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 点击第一个目标（近期使用类目第一项）
    if targets:
        elem, name, rect, ctype = targets[0]
        print(f"\nClicking first target: '{name}' at ({rect.left}, {rect.top})...")
        try:
            elem.invoke()
        except:
            pyautogui.click(rect.left + 50, rect.top + 5)
        time.sleep(2)
        print("Clicked!")
    
    # 如果没找到，尝试点击 (550, 660)
    if not targets:
        print("\nNo targets found, trying (550, 660)...")
        pyautogui.click(550, 660)
        time.sleep(2)

except Exception as e:
    print(f"Error: {e}")
