# -*- coding: utf-8 -*-
# 使用剪贴板粘贴商品标题
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
    
    # 获取商品标题输入框
    edits = jingmai.descendants(control_type="Edit")
    title_edit = edits[1]
    rect = title_edit.rectangle()
    print(f"Title Edit at ({rect.left}, {rect.top})")
    
    # 点击激活
    pyautogui.click(rect.left + 50, rect.top + 10)
    time.sleep(0.5)
    
    # 全选
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.3)
    
    # 复制标题到剪贴板并粘贴
    title = "公牛BULL插座B5系列8位总控5米新国标防过载带儿童保护门插座B5440"
    pyperclip.copy(title)
    print(f"Copied to clipboard: {title}")
    
    # 粘贴
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(1)
    
    # 按Tab离开
    pyautogui.press("tab")
    time.sleep(0.5)
    
    print("Done!")

except Exception as e:
    print(f"Error: {e}")
