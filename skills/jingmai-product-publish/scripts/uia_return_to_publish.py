# -*- coding: utf-8 -*-
# 回到商品发布页面
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
    
    # 点击商品发布链接
    print("Looking for 商品发布...")
    
    links = jingmai.descendants(control_type="Hyperlink")
    for link in links:
        try:
            name = link.element_info.name or ""
            rect = link.rectangle()
            if "发布" in name:
                print(f"  Found: '{name}' at ({rect.left}, {rect.top})")
                pyautogui.click(rect.left + 50, rect.top + 10)
                time.sleep(2)
                break
        except:
            pass
    
    # 点击顶部标签
    texts = jingmai.descendants(control_type="Text")
    for text in texts:
        try:
            name = text.element_info.name or ""
            rect = text.rectangle()
            if "商品发布" in name:
                print(f"  Text: '{name}' at ({rect.left}, {rect.top})")
                pyautogui.click(rect.left + 50, rect.top + 10)
                time.sleep(2)
                break
        except:
            pass
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
