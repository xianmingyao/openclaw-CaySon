# -*- coding: utf-8 -*-
# 滚动并填写SKU字段
import platform
if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

try:
    from pywinauto import Desktop
    import pyautogui
    import time
    import pyperclip
    
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
    
    # 向下滚动
    print("Scrolling down...")
    for i in range(5):
        pyautogui.scroll(-3, x=1280, y=700)
        time.sleep(0.3)
    
    # 获取当前所有"请输入"和"请选择"
    all_elements = jingmai.descendants()
    
    print("\n=== 未填写字段 ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if (name in ["请选择", "请输入"] or "请" in name) and rect.width() > 0:
                print(f"  '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
