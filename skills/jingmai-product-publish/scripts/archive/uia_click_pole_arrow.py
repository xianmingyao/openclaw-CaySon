# -*- coding: utf-8 -*-
# 点击极数下拉框的箭头
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
    
    # 向上滚动一点
    for i in range(3):
        pyautogui.scroll(2, x=1280, y=700)
        time.sleep(0.2)
    
    # ========== 点击极数下拉框 ==========
    # 下拉箭头通常在下拉框右侧
    print("Clicking 极数 dropdown arrow at (1076, 648)...")
    pyautogui.click(1076, 648)  # 点击下拉箭头
    time.sleep(2)
    
    # 查找极数选项
    all_elements = jingmai.descendants()
    print("Looking for pole options...")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            # 极数选项可能在y=650-800范围
            if 650 <= rect.top <= 800 and len(name) <= 3:
                if name.isdigit():
                    print(f"  Found: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 尝试点击"3"极数选项（通常插座是3极）
    print("Trying to click 3 at (1060, 700)...")
    pyautogui.click(1060, 700)
    time.sleep(1)
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
