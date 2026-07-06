# -*- coding: utf-8 -*-
# 点击价格表头位置激活输入框
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
    for i in range(12):
        pyautogui.scroll(3, x=1280, y=700)
        time.sleep(0.2)
    
    # 多次拖动滚动条
    print("Dragging scrollbar multiple times...")
    for _ in range(3):
        pyautogui.mouseDown(1500, 915)
        time.sleep(0.2)
        pyautogui.moveTo(1800, 915)
        time.sleep(0.2)
        pyautogui.mouseUp()
        time.sleep(0.5)
    
    # 点击价格表头位置
    # 根据分析，市场价表头在x=1222，采购价在x=1338，京东价在x=1454
    # 数据行在y=1076-1120范围
    print("Clicking price header positions...")
    
    # 点击"市场价"表头
    pyautogui.click(1222, 1029)
    time.sleep(0.5)
    
    # 获取当前所有Edit
    edits = jingmai.descendants(control_type="Edit")
    print(f"\nFound {len(edits)} Edit elements after click")
    
    # 打印价格相关的Edit
    for i, edit in enumerate(edits):
        try:
            name = edit.element_info.name or ""
            rect = edit.rectangle()
            if rect.width() > 0 and rect.top > 1000:
                print(f"  [{i}] '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
