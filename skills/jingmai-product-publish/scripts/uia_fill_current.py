# -*- coding: utf-8 -*-
# 填写电流（SKU规格描述）
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
    
    # 关闭任何弹窗
    pyautogui.press('escape')
    time.sleep(0.5)
    
    # 根据截图，"电流"在规格描述表格中
    # 之前分析Edit[8]在(844, 1005)，可能是电流输入框
    edits = jingmai.descendants(control_type="Edit")
    
    print(f"Found {len(edits)} Edit elements")
    
    # 找电流输入框
    for i, edit in enumerate(edits):
        try:
            name = edit.element_info.name or ""
            rect = edit.rectangle()
            if 900 <= rect.top <= 1100:
                print(f"  [{i}] '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 点击并填写电流
    print("\nTrying to fill current...")
    # 根据图片，电流在规格描述表格中，可能在Edit[8]
    if len(edits) > 8:
        current_edit = edits[8]
        rect = current_edit.rectangle()
        print(f"Edit[8] at ({rect.left}, {rect.top})")
        
        # 点击激活
        pyautogui.click(rect.left + 50, rect.top + 10)
        time.sleep(0.3)
        
        # 填写10A
        pyautogui.typewrite("10", interval=0.1)
        time.sleep(0.5)
        print("Filled 10A")
    
    print("Done!")

except Exception as e:
    print(f"Error: {e}")
