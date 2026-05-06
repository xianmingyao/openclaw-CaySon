# -*- coding: utf-8 -*-
# 找到所有"请选择"的位置
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
    
    # 按Esc关闭当前下拉框
    pyautogui.press('escape')
    time.sleep(0.5)
    
    # 找所有"请选择"文本的位置
    print("Looking for all '请选择' texts...")
    all_elements = jingmai.descendants()
    
    hole_config_y = None
    voltage_y = None
    cable_y = None
    
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            ctype = elem.element_info.control_type
            
            # 找"请选择"文本
            if name == "请选择":
                print(f"  '{name}' at ({rect.left}, {rect.top}) [{ctype}]")
                
                # 根据x位置判断是哪个字段
                # 左侧是孔型配置(x~644)，中间是额定电压(x~1036)
                if rect.left < 800:
                    # 可能是孔型配置
                    # 检查上一行是否是"孔型配置"
                    pass
                elif rect.left > 900 and rect.left < 1200:
                    # 可能是额定电压或电缆长度
                    pass
        except:
            pass
    
    # 也打印包含"孔型"、"额定"、"电缆"的元素
    print("\nElements with keywords:")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if any(kw in name for kw in ['孔型配置', '额定电压', '电缆长度']):
                print(f"  '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
