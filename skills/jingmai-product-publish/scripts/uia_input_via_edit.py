# -*- coding: utf-8 -*-
# 使用pywinauto的Edit控件直接输入
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
    
    # 向上滚动
    for i in range(10):
        pyautogui.scroll(3, x=1280, y=700)
        time.sleep(0.2)
    
    # 获取所有Edit控件
    edits = jingmai.descendants(control_type="Edit")
    
    print(f"Found {len(edits)} Edit elements")
    
    # 找商品标题输入框
    title_edit = None
    for edit in edits:
        try:
            name = edit.element_info.name or ""
            rect = edit.rectangle()
            if "商品标题" in name or (rect.left == 750 and rect.top == 425):
                title_edit = edit
                print(f"Found title Edit: '{name}' at ({rect.left}, {rect.top})")
                break
        except:
            pass
    
    if title_edit:
        print("Inputting title via Edit...")
        try:
            # 尝试使用set_edit_text
            title_edit.set_edit_text("公牛BULL插座B5系列8位总控5米新国标防过载商业专用B5440")
            print("Success with set_edit_text!")
        except Exception as e:
            print(f"set_edit_text failed: {e}")
            # 备选：点击并用键盘输入
            rect = title_edit.rectangle()
            pyautogui.click(rect.left + 100, rect.top + 10)
            time.sleep(0.5)
            pyautogui.typewrite("公牛BULL插座B5系列8位总控5米新国标防过载商业专用B5440", interval=0.05)
    else:
        print("Title Edit not found!")
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
