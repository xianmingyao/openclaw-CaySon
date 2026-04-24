# -*- coding: utf-8 -*-
# 使用pywinauto点击编辑按钮
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
    
    # 获取所有Button
    buttons = jingmai.descendants(control_type="Button")
    
    print(f"Found {len(buttons)} buttons")
    
    # 找编辑按钮
    edit_btn = None
    for btn in buttons:
        try:
            name = btn.element_info.name or ""
            if "编辑" in name:
                edit_btn = btn
                rect = btn.rectangle()
                print(f"Found 编辑 at ({rect.left}, {rect.top})")
                break
        except:
            pass
    
    if edit_btn:
        print("Clicking edit button...")
        # 使用invoke方法
        try:
            edit_btn.invoke()
        except:
            # 备选：使用点击
            rect = edit_btn.rectangle()
            pyautogui.click(rect.left + 20, rect.top + 10)
        time.sleep(3)
        print("Done!")
    else:
        print("Edit button not found!")

except Exception as e:
    print(f"Error: {e}")
