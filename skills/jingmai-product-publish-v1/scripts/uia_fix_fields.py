# -*- coding: utf-8 -*-
# 修正字段值
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
    
    edits = jingmai.descendants(control_type="Edit")
    combos = jingmai.descendants(control_type="ComboBox")
    
    # 1. 填写孔型配置
    print("1. Filling 孔型配置...")
    for edit in edits:
        try:
            rect = edit.rectangle()
            if rect.left == 844 and rect.top == 1288:
                edit.set_edit_text("8位（五孔×4+二孔×4）")
                print("   Success!")
                break
        except:
            pass
    
    time.sleep(0.5)
    
    # 2. 选择电缆长度 5米
    print("2. Selecting 电缆长度 5米...")
    for combo in combos:
        try:
            rect = combo.rectangle()
            if rect.left == 644 and rect.top == 686:
                pyautogui.click(rect.left + 80, rect.top + 10)
                time.sleep(0.5)
                for _ in range(5):
                    pyautogui.press('down')
                    time.sleep(0.15)
                pyautogui.press('enter')
                print("   Success!")
                break
        except:
            pass
    
    time.sleep(0.5)
    
    # 3. 选择极数 2P+E
    print("3. Selecting 极数 2P+E...")
    for combo in combos:
        try:
            rect = combo.rectangle()
            if rect.left == 1036 and rect.top == 686:
                pyautogui.click(rect.left + 80, rect.top + 10)
                time.sleep(0.5)
                for _ in range(2):
                    pyautogui.press('down')
                    time.sleep(0.15)
                pyautogui.press('enter')
                print("   Success!")
                break
        except:
            pass
    
    time.sleep(0.5)
    
    # 4. 选择防护等级 IP55 - 向上滚动找
    print("4. Selecting 防护等级 IP55...")
    for i in range(5):
        pyautogui.scroll(2, x=1280, y=700)
        time.sleep(0.2)
    
    time.sleep(0.5)
    combos = jingmai.descendants(control_type="ComboBox")
    
    for combo in combos:
        try:
            name = combo.element_info.name or ""
            if "防护" in name:
                rect = combo.rectangle()
                print(f"   Found at ({rect.left}, {rect.top})")
                pyautogui.click(rect.left + 80, rect.top + 10)
                time.sleep(0.5)
                for _ in range(4):
                    pyautogui.press('down')
                    time.sleep(0.15)
                pyautogui.press('enter')
                print("   Success!")
                break
        except:
            pass
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
