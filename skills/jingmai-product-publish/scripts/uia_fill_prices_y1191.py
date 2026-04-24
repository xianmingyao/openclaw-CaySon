# -*- coding: utf-8 -*-
# 填写价格（y=1191）
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
    
    # 填写市场价 82.35 (1377, 1191)
    print("Filling 市场价(82.35)...")
    pyautogui.click(1377, 1191)
    time.sleep(0.3)
    pyperclip.copy("82.35")
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.2)
    pyautogui.press('delete')
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.3)
    
    # 填写采购价 66.5 (1517, 1191)
    print("Filling 采购价(66.5)...")
    pyautogui.click(1517, 1191)
    time.sleep(0.3)
    pyperclip.copy("66.5")
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.2)
    pyautogui.press('delete')
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.3)
    
    # 填写京东价 70 (1779, 1191)
    print("Filling 京东价(70)...")
    pyautogui.click(1779, 1191)
    time.sleep(0.3)
    pyperclip.copy("70")
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.2)
    pyautogui.press('delete')
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
