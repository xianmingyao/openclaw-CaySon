# -*- coding: utf-8 -*-
# 填写型号 - B5440
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
    
    # 获取所有Edit
    edits = jingmai.descendants(control_type="Edit")
    print(f"Found {len(edits)} Edit elements")
    
    # Edit[2] = 型号
    if len(edits) > 2:
        model_edit = edits[2]
        rect = model_edit.rectangle()
        print(f"Edit[2] (型号) at ({rect.left}, {rect.top})")
        
        # 点击激活
        pyautogui.click(rect.left + 50, rect.top + 10)
        time.sleep(0.3)
        
        # 清除
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.press('delete')
        time.sleep(0.2)
        
        # 输入型号
        model = "B5440"
        print(f"Inputting model: {model}")
        
        # 使用set_edit_text
        try:
            model_edit.set_edit_text(model)
        except:
            pyautogui.typewrite(model, interval=0.05)
        
        time.sleep(1)
        print("Done!")
    else:
        print("Not enough Edit elements!")

except Exception as e:
    print(f"Error: {e}")
