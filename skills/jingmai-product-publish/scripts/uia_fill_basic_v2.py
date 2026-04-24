# -*- coding: utf-8 -*-
# 填写商品基本信息
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
    
    # 向上滚动
    for i in range(10):
        pyautogui.scroll(3, x=1280, y=700)
        time.sleep(0.2)
    
    # 1. 填写商品标题
    print("1. Filling 商品标题...")
    pyautogui.click(750, 302)
    time.sleep(0.3)
    title = "公牛BULL插座B5系列8位总控5米新国标防过载商业专用B5440"
    pyperclip.copy(title)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    
    # 2. 选择品牌 - BULL
    print("2. Selecting 品牌 BULL...")
    pyautogui.click(628, 406)
    time.sleep(1)
    # 键盘选择
    for _ in range(3):
        pyautogui.press('down')
        time.sleep(0.2)
    pyautogui.press('enter')
    time.sleep(0.5)
    
    # 3. 填写型号
    print("3. Filling 型号 B5440...")
    pyautogui.click(1028, 406)
    time.sleep(0.3)
    pyperclip.copy("B5440")
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    
    # 4. 选择额定电压 250V~
    print("4. Selecting 额定电压 250V~...")
    pyautogui.click(1036, 758)
    time.sleep(1)
    for _ in range(3):
        pyautogui.press('down')
        time.sleep(0.2)
    pyautogui.press('enter')
    time.sleep(0.5)
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
