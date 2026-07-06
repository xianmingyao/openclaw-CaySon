# -*- coding: utf-8 -*-
# 关闭弹窗
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
    
    # 按ESC关闭弹窗
    print("Pressing ESC...")
    pyautogui.press('escape')
    time.sleep(1)
    
    # 如果弹窗还在，按确定按钮
    print("Looking for OK button...")
    buttons = jingmai.descendants(control_type="Button")
    for btn in buttons:
        try:
            name = btn.element_info.name or ""
            if "确定" in name or "OK" in name or "Cancel" in name:
                rect = btn.rectangle()
                print(f"Found: '{name}' at ({rect.left}, {rect.top})")
                pyautogui.click(rect.left + 30, rect.top + 10)
                time.sleep(1)
                break
        except:
            pass
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
