# -*- coding: utf-8 -*-
# 点击建议标题
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
    
    # 查找建议标题 - 绿色框
    print("Looking for suggestion title...")
    all_elements = jingmai.descendants()
    
    # 打印y=400-550范围的元素
    print("Elements in y=400-550:")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            ctype = elem.element_info.control_type
            if 400 <= rect.top <= 550 and name and len(name.strip()) > 5:
                print(f"  {ctype}: '{name[:50]}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 尝试点击商品标题输入框
    print("\nClicking title input...")
    pyautogui.click(750, 425)
    time.sleep(0.5)
    
    # 按Ctrl+A全选
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.3)
    
    # 删除
    pyautogui.press('delete')
    time.sleep(0.3)
    
    # 输入新标题
    title = "公牛BULL插座86型暗装墙壁开关插座多位电源插座B5440系列"
    print(f"Typing: {title}")
    pyautogui.typewrite(title, interval=0.08)
    time.sleep(1)
    
    # 按Tab
    pyautogui.press("tab")
    time.sleep(0.5)
    
    print("Done!")

except Exception as e:
    print(f"Error: {e}")
