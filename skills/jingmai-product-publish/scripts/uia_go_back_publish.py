# -*- coding: utf-8 -*-
# 切回商品发布页面
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
    
    # 查找"发布商品"文本
    all_elements = jingmai.descendants()
    
    print("\n=== Looking for 发布商品 ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            if "发布" in name or "商品" in name:
                rect = elem.rectangle()
                ctype = elem.element_info.control_type
                print(f"  {ctype}: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 点击发布商品
    print("\nClicking 发布商品 at (172, 13)...")
    pyautogui.click(172, 13)
    time.sleep(2)
    
    print("Done!")

except Exception as e:
    print(f"Error: {e}")
