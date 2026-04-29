# -*- coding: utf-8 -*-
# 点击近期使用类目中的第一项
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
    
    # 查找所有在y=640-700范围的元素
    all_elements = jingmai.descendants()
    
    # 打印详细信息
    print("Detailed elements in y=640-700:")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if 640 <= rect.top <= 700 and name:
                ctype = elem.element_info.control_type
                # 检查是否是可点击的
                is_clickable = ctype in ["Hyperlink", "Button", "ListItem", "Custom"]
                clickable_mark = "[CLICKABLE]" if is_clickable else ""
                print(f"  {ctype} '{name}' at ({rect.left}, {rect.top}) {clickable_mark}")
        except:
            pass
    
    # 尝试查找ListItem
    print("\nLooking for ListItem...")
    listitems = jingmai.descendants(control_type="ListItem")
    print(f"Found {len(listitems)} ListItems")
    for i, item in enumerate(listitems[:10]):
        try:
            name = item.element_info.name or ""
            rect = item.rectangle()
            print(f"  [{i}] '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 尝试点击"工业品" - 使用更精确的位置
    print("\nClicking at (620, 660)...")
    pyautogui.click(620, 660)
    time.sleep(2)
    
    # 也尝试点击 (592, 654) 中心
    print("Also clicking at (592, 660)...")
    pyautogui.click(592, 660)
    time.sleep(2)
    
    print("Done!")

except Exception as e:
    print(f"Error: {e}")
