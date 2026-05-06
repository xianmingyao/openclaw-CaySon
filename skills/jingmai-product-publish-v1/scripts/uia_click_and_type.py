# -*- coding: utf-8 -*-
# 点击单元格并用键盘输入
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
    for i in range(15):
        pyautogui.scroll(3, x=1280, y=700)
        time.sleep(0.2)
    
    # 数据行y位置分析：TabItem表头在y=1269
    # 数据行可能在y=1300左右
    # 但根据实际观察，SKU表格的单元格可能是自定义控件
    # 需要先点击激活，再输入
    
    # 尝试点击货期列的数据单元格
    # 货期表头x=912，数据区应该在表头下方
    print("Clicking 货期 cell at (912, 1300)...")
    pyautogui.click(912, 1300)
    time.sleep(0.8)
    
    # 清除现有内容并输入7
    print("Clearing and typing 7...")
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.2)
    pyautogui.press('delete')
    time.sleep(0.2)
    pyautogui.typewrite('7', interval=0.1)
    time.sleep(0.5)
    
    # 按Tab移动到下一个字段
    pyautogui.press('tab')
    time.sleep(0.3)
    
    # 清除并输入市场价 82.35
    print("Typing 82.35...")
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.2)
    pyautogui.press('delete')
    time.sleep(0.2)
    pyautogui.typewrite('82.35', interval=0.1)
    time.sleep(0.5)
    
    # 按Tab移动
    pyautogui.press('tab')
    time.sleep(0.3)
    
    # 清除并输入采购价 66.5
    print("Typing 66.5...")
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.2)
    pyautogui.press('delete')
    time.sleep(0.2)
    pyautogui.typewrite('66.5', interval=0.1)
    time.sleep(0.5)
    
    # 按Tab移动
    pyautogui.press('tab')
    time.sleep(0.3)
    
    # 清除并输入京东价 70
    print("Typing 70...")
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.2)
    pyautogui.press('delete')
    time.sleep(0.2)
    pyautogui.typewrite('70', interval=0.1)
    time.sleep(0.5)
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
