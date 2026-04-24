# -*- coding: utf-8 -*-
# 点击"下一步"按钮
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
    
    # 查找"下一步"按钮
    print("Looking for '下一步' button...")
    buttons = jingmai.descendants(control_type="Button")
    
    for btn in buttons:
        try:
            name = btn.element_info.name or ""
            if "下一步" in name:
                rect = btn.rectangle()
                print(f"Found: '{name}' at ({rect.left}, {rect.top})")
                try:
                    btn.invoke()
                except:
                    pyautogui.click(rect.left + 100, rect.top + 10)
                time.sleep(2)
                print("Clicked!")
                break
        except:
            pass

except Exception as e:
    print(f"Error: {e}")
