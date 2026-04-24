# -*- coding: utf-8 -*-
# 填写孔型配置
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
    
    # 找Edit[7] - 孔型配置
    if len(edits) > 7:
        hole_edit = edits[7]
        rect = hole_edit.rectangle()
        print(f"Edit[7] at ({rect.left}, {rect.top})")
        
        # 点击激活
        pyautogui.click(rect.left + 50, rect.top + 10)
        time.sleep(0.3)
        
        # 清除
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.press('delete')
        time.sleep(0.2)
        
        # 输入孔型配置
        hole_config = "五孔"
        print(f"Inputting: {hole_config}")
        pyautogui.typewrite(hole_config, interval=0.1)
        time.sleep(1)
        
        print("Done!")
    else:
        print(f"Only {len(edits)} Edit elements found")

except Exception as e:
    print(f"Error: {e}")
