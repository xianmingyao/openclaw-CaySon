# -*- coding: utf-8 -*-
# 直接点击并用键盘输入
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
    
    # 1. 填写商品标题 - 先点击激活，用Ctrl+A选择，然后输入
    print("1. Filling 商品标题...")
    pyautogui.click(750, 302)
    time.sleep(0.5)
    # 用Ctrl+A全选
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.3)
    # 直接输入新内容
    pyautogui.typewrite("公牛BULL插座B5系列8位总控5米新国标防过载商业专用B5440", interval=0.05)
    time.sleep(0.5)
    
    # 2. 修正额定电压
    print("2. Fixing 额定电压...")
    pyautogui.click(1036, 758)
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.3)
    pyautogui.typewrite("250V~", interval=0.05)
    time.sleep(0.5)
    
    # 3. 填写孔型配置
    print("3. Filling 孔型配置...")
    pyautogui.click(844, 1165)
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.3)
    pyautogui.typewrite("8位", interval=0.05)
    time.sleep(0.5)
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
