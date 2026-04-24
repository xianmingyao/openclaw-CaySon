# -*- coding: utf-8 -*-
# 填写SKU商品名称
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
    
    # 点击商品名称输入框 (644, 457)
    print("Clicking SKU name at (644, 457)...")
    pyautogui.click(644, 457)
    time.sleep(0.5)
    
    # 使用剪贴板粘贴
    sku_name = "公牛BULL插座B5系列8位总控5米新国标防过载B5440"
    print(f"Inputting: {sku_name}")
    pyperclip.copy(sku_name)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
