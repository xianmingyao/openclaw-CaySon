# -*- coding: utf-8 -*-
# 向右滚动查看价格字段
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
    
    # 向上滚动到正确位置
    print("Scrolling up...")
    for i in range(10):
        pyautogui.scroll(3, x=1280, y=700)
        time.sleep(0.2)
    
    # 向右滚动查看价格字段
    print("Scrolling right...")
    for i in range(10):
        pyautogui.keyboard.press_right()
        time.sleep(0.2)
    
    # 获取价格相关字段
    all_elements = jingmai.descendants()
    
    print("\n=== 价格字段 ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if any(kw in name for kw in ["价", "市场价", "采购价", "京东价"]):
                print(f"  '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
