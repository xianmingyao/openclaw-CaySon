# -*- coding: utf-8 -*-
# 填写电流10A
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
    
    # 点击电流输入框 (713, 1213)
    print("Clicking current input at (713, 1213)...")
    pyautogui.click(713, 1213)
    time.sleep(0.5)
    
    # 全选清除
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.2)
    pyautogui.press('delete')
    time.sleep(0.2)
    
    # 使用剪贴板粘贴"10A"
    print("Filling 10A...")
    pyperclip.copy("10")
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    
    # 按Tab离开
    pyautogui.press("tab")
    time.sleep(0.5)
    
    print("Done!")

except Exception as e:
    print(f"Error: {e}")
