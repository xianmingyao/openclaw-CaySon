# -*- coding: utf-8 -*-
# 分析商品属性区域的元素
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
    
    # 获取所有元素，分析y=800-1100范围
    all_elements = jingmai.descendants()
    
    print("\n=== 分析 y=800-1100 区域 ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            ctype = elem.element_info.control_type
            if 800 <= rect.top <= 1100 and rect.width() > 0:
                # 只打印关键元素
                if any(keyword in name for keyword in ['孔型', '额定', '电缆', '电压', '配置', '长度', '请选择', '请输入', '属性']):
                    print(f"  {ctype}: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 打印所有ComboBox
    print("\n=== 所有ComboBox (y=800-1050) ===")
    combos = jingmai.descendants(control_type="ComboBox")
    for i, combo in enumerate(combos):
        try:
            name = combo.element_info.name or ""
            rect = combo.rectangle()
            if 800 <= rect.top <= 1050:
                print(f"  [{i}] '{name}' at ({rect.left}, {rect.top})")
        except:
            pass

except Exception as e:
    print(f"Error: {e}")
