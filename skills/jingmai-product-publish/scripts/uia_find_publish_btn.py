# -*- coding: utf-8 -*-
# 查找发布商品按钮位置
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
    
    # 查找所有按钮
    buttons = jingmai.descendants(control_type="Button")
    print(f"Found {len(buttons)} buttons:")
    
    for btn in buttons:
        try:
            name = btn.element_info.name or ""
            rect = btn.rectangle()
            if name and len(name.strip()) > 1:
                print(f"  '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 特别查找"发布商品"
    print("\nLooking for '发布商品'...")
    for btn in buttons:
        try:
            name = btn.element_info.name or ""
            if "发布" in name or "商品" in name:
                rect = btn.rectangle()
                print(f"  FOUND: '{name}' at ({rect.left}, {rect.top})")
                
                # 点击它
                pyautogui.click(rect.left + 100, rect.top + 10)
                time.sleep(2)
                print("  Clicked!")
                break
        except:
            pass

except Exception as e:
    print(f"Error: {e}")
