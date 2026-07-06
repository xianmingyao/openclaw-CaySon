# -*- coding: utf-8 -*-
# 填写剩余价格字段
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
    
    # 向右拖动滚动条
    for _ in range(3):
        pyautogui.mouseDown(1500, 915)
        time.sleep(0.2)
        pyautogui.moveTo(1800, 915)
        time.sleep(0.2)
        pyautogui.mouseUp()
        time.sleep(0.3)
    
    # 获取当前Edit位置
    edits = jingmai.descendants(control_type="Edit")
    
    print("\n=== Price Edit positions ===")
    for i, edit in enumerate(edits):
        try:
            name = edit.element_info.name or ""
            rect = edit.rectangle()
            if rect.width() > 0 and rect.top > 1000:
                print(f"  [{i}] '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 填写市场价 82.35
    print("\nFilling 市场价(82.35)...")
    pyautogui.click(1377, 1191)
    time.sleep(0.3)
    pyperclip.copy("82.35")
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.2)
    pyautogui.press('delete')
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.3)
    
    # 填写京东价 70
    print("Filling 京东价(70)...")
    pyautogui.click(1779, 1191)
    time.sleep(0.3)
    pyperclip.copy("70")
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.2)
    pyautogui.press('delete')
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
