# -*- coding: utf-8 -*-
# 填写货期7天，并修正滚动方向
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
    
    # 向下滚动（页面向下走）scroll(-3, ...)
    print("Scrolling down (page goes down)...")
    for i in range(10):
        pyautogui.scroll(-3, x=1280, y=700)
        time.sleep(0.2)
    
    # 找到货期输入框
    all_elements = jingmai.descendants()
    
    print("\n=== Looking for 货期 ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if "货" in name or "7" in name:
                print(f"  '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 货期输入框通常在SKU表格中
    # 根据SKU表格分析，货期列在x≈1115位置（电压后面）
    print("\nFilling 货期(7天)...")
    pyautogui.click(1115, 1221)  # 货期输入框位置
    time.sleep(0.3)
    pyperclip.copy("7")
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.2)
    pyautogui.press('delete')
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
