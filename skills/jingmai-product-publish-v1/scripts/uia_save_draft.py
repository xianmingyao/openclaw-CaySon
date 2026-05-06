# -*- coding: utf-8 -*-
# 保存草稿
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
    for i in range(15):
        pyautogui.scroll(3, x=1280, y=700)
        time.sleep(0.2)
    
    # 查找保存/草稿按钮
    all_elements = jingmai.descendants()
    
    print("\n=== 查找保存/草稿按钮 ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if any(kw in name for kw in ["保存", "草稿", "存", "draft", "save"]):
                ctype = elem.element_info.control_type
                print(f"  {ctype}: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 查找发布按钮
    print("\n=== 查找发布按钮 ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if any(kw in name for kw in ["发布", "发布商品"]):
                ctype = elem.element_info.control_type
                print(f"  {ctype}: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 查找取消按钮
    print("\n=== 查找取消/返回按钮 ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if any(kw in name for kw in ["取消", "返回", "上一步"]):
                ctype = elem.element_info.control_type
                print(f"  {ctype}: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
