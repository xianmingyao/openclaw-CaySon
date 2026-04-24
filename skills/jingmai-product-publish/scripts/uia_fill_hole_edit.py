# -*- coding: utf-8 -*-
# 使用Edit[7]输入孔型配置
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
    
    # 获取Edit[7]
    edits = jingmai.descendants(control_type="Edit")
    hole_edit = edits[7]
    rect = hole_edit.rectangle()
    print(f"Edit[7] at ({rect.left}, {rect.top})")
    
    # 点击激活
    print("Clicking to activate...")
    pyautogui.click(rect.left + 50, rect.top + 10)
    time.sleep(0.5)
    
    # 清除
    print("Clearing...")
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.2)
    pyautogui.press('delete')
    time.sleep(0.2)
    
    # 使用set_edit_text输入
    print("Inputting '五孔'...")
    hole_edit.set_edit_text("五孔")
    time.sleep(1)
    
    print("Done!")

except Exception as e:
    print(f"Error: {e}")
