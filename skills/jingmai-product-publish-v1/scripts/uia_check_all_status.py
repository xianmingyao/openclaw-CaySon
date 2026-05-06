# -*- coding: utf-8 -*-
# 检查当前京麦状态
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
    
    # 检查Edit[1] - 商品标题
    edits = jingmai.descendants(control_type="Edit")
    if len(edits) > 1:
        title_edit = edits[1]
        rect = title_edit.rectangle()
        
        # 获取文本
        try:
            text = title_edit.text()
            print(f"商品标题: '{text}'")
        except:
            print("商品标题: (无法获取)")
    
    # 检查所有"请选择"和"请输入"
    all_elements = jingmai.descendants()
    
    print("\n=== 必填属性 ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if 800 <= rect.top <= 900:
                if "请选择" in name or "请输入" in name:
                    # 找label
                    for label in all_elements:
                        try:
                            lrect = label.rectangle()
                            if lrect.left < rect.left and lrect.left > 500 and abs(lrect.top - rect.top) < 30:
                                if label.element_info.control_type in ["Text", "Static"]:
                                    print(f"  {label.element_info.name}: {name}")
                                    break
                        except:
                            pass
        except:
            pass
    
    # 打印"重要属性"区域
    print("\n=== 重要属性 ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if 980 <= rect.top <= 1100:
                if "请选择" in name or "请输入" in name or "IP" in name or "极" in name:
                    print(f"  '{name}' at ({rect.left}, {rect.top})")
        except:
            pass

except Exception as e:
    print(f"Error: {e}")
