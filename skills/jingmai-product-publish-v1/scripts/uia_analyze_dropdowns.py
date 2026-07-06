# -*- coding: utf-8 -*-
# 重新分析页面结构
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
    
    # 向上滚动到正确位置
    print("Scrolling up...")
    for i in range(5):
        pyautogui.scroll(3, x=1280, y=700)
        time.sleep(0.2)
    
    # 获取所有"请选择"元素
    all_elements = jingmai.descendants()
    
    print("\n=== All '请选择' elements ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if name == "请选择" and rect.width() > 0:
                print(f"  at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 找ComboBox
    print("\n=== ComboBox elements ===")
    combos = jingmai.descendants(control_type="ComboBox")
    for i, combo in enumerate(combos):
        try:
            rect = combo.rectangle()
            if rect.width() > 0:
                print(f"  [{i}] at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 找重要属性区域
    print("\n=== Elements containing '防护' or '极数' ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            if "防护" in name or "极数" in name:
                rect = elem.rectangle()
                print(f"  '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
