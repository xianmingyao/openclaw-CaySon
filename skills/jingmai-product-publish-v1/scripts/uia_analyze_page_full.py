# -*- coding: utf-8 -*-
# 分析当前页面完整结构
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
    
    # 向下滚动到正确位置
    for i in range(8):
        pyautogui.scroll(-3, x=1280, y=700)
        time.sleep(0.2)
    
    # 获取所有元素
    all_elements = jingmai.descendants()
    
    # 打印所有带*的必填项
    print("\n=== 必填项 (*标记) ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if "*" in name and rect.width() > 0:
                ctype = elem.element_info.control_type
                print(f"  {ctype}: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 打印ComboBox
    print("\n=== ComboBox下拉框 ===")
    combos = jingmai.descendants(control_type="ComboBox")
    for i, combo in enumerate(combos):
        try:
            name = combo.element_info.name or ""
            rect = combo.rectangle()
            if rect.width() > 0:
                print(f"  [{i}] '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 打印所有文本
    print("\n=== 文本 (y=800-1200) ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if 800 <= rect.top <= 1200 and name and len(name.strip()) > 0:
                ctype = elem.element_info.control_type
                if ctype == "Text":
                    print(f"  '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
