# -*- coding: utf-8 -*-
# 使用pywinauto的Edit控件填写其他字段
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
    
    # 1. 填写孔型配置 (Edit at 844, 1288)
    print("1. Filling 孔型配置...")
    for edit in edits:
        try:
            rect = edit.rectangle()
            if rect.left == 844 and rect.top == 1288:
                edit.set_edit_text("8位（五孔×4+二孔×4）")
                print(f"  Success!")
                break
        except:
            pass
    
    # 2. 选择额定电压 250V~
    print("2. Selecting 额定电压...")
    combos = jingmai.descendants(control_type="ComboBox")
    for combo in combos:
        try:
            rect = combo.rectangle()
            if rect.left == 1036 and rect.top == 881:
                # 点击展开
                pyautogui.click(rect.left + 100, rect.top + 10)
                time.sleep(1)
                # 找选项
                items = combo.items()
                for item in items:
                    if "250V" in str(item):
                        item.select()
                        print(f"  Selected: {item}")
                        break
                break
        except:
            pass
    
    # 3. 选择电缆长度 5米
    print("3. Selecting 电缆长度...")
    for combo in combos:
        try:
            rect = combo.rectangle()
            if rect.left == 644 and rect.top == 1026:
                pyautogui.click(rect.left + 100, rect.top + 10)
                time.sleep(1)
                items = combo.items()
                for item in items:
                    if "5米" in str(item):
                        item.select()
                        print(f"  Selected: {item}")
                        break
                break
        except:
            pass
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
