# -*- coding: utf-8 -*-
# 尝试保存草稿
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
    
    # 找到保存草稿按钮
    print("Looking for 保存草稿 button...")
    
    buttons = jingmai.descendants(control_type="Button")
    for btn in buttons:
        try:
            name = btn.element_info.name or ""
            rect = btn.rectangle()
            if "草稿" in name or "保存" in name:
                print(f"  Found: '{name}' at ({rect.left}, {rect.top})")
                # 点击
                pyautogui.click(rect.left + 50, rect.top + 10)
                time.sleep(2)
                break
        except:
            pass
    
    # 也尝试点击下拉箭头
    print("\nLooking for dropdown arrows...")
    combos = jingmai.descendants(control_type="ComboBox")
    for combo in combos:
        try:
            name = combo.element_info.name or ""
            rect = combo.rectangle()
            if rect.left > 0:
                print(f"  Combo: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 直接点击ComboBox旁边的下拉按钮
    print("\nClicking dropdown arrow directly...")
    # 销售单位下拉箭头
    pyautogui.click(1828, 881)
    time.sleep(1)
    
    # 截图看结果
    print("Taking screenshot...")
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
