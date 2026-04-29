# -*- coding: utf-8 -*-
# 重新填写商品标题
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
    
    # Edit[1] = 商品标题 (750, 425)
    title_edit = edits[1]
    rect = title_edit.rectangle()
    print(f"Edit[1] at ({rect.left}, {rect.top})")
    
    # 点击激活
    print("Clicking to activate...")
    pyautogui.click(rect.left + 50, rect.top + 10)
    time.sleep(0.5)
    
    # 全选清除
    print("Clearing...")
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.3)
    pyautogui.press('delete')
    time.sleep(0.3)
    
    # 直接使用pyautogui输入
    title = "公牛BULL插座B5440系列86型暗装墙壁开关插座多位电源插座"
    print(f"Typing title: {title}")
    pyautogui.typewrite(title, interval=0.08)
    time.sleep(1)
    
    # 按Tab键移动到下一个字段
    pyautogui.press("tab")
    time.sleep(0.5)
    
    print("Done!")

except Exception as e:
    print(f"Error: {e}")
