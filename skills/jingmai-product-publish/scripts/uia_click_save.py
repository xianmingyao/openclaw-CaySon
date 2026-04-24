# -*- coding: utf-8 -*-
# 点击保存草稿
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
    for i in range(10):
        pyautogui.scroll(3, x=1280, y=700)
        time.sleep(0.2)
    
    # 查找MenuItem
    menu_items = jingmai.descendants(control_type="MenuItem")
    
    print("\n=== MenuItems ===")
    for item in menu_items:
        try:
            name = item.element_info.name or ""
            rect = item.rectangle()
            if rect.width() > 0:
                print(f"  '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 点击保存草稿 MenuItem
    print("\nClicking 保存草稿...")
    for item in menu_items:
        try:
            name = item.element_info.name or ""
            if "草稿" in name or "保存" in name:
                rect = item.rectangle()
                pyautogui.click(rect.left + 50, rect.top + 10)
                time.sleep(3)
                print(f"Clicked: {name}")
                break
        except:
            pass
    
    print("Done!")

except Exception as e:
    print(f"Error: {e}")
