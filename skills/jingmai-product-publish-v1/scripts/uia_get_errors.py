# -*- coding: utf-8 -*-
# 查看报错反馈
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
    
    # 获取所有元素，查找报错信息
    all_elements = jingmai.descendants()
    
    print("=== 查找报错信息 ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            ctype = elem.element_info.control_type
            
            # 查找报错相关的关键词
            if any(kw in name for kw in ['报错', '错误', '请输入', '必填', '未填写', '失败']):
                if len(name) > 2:
                    print(f"  {ctype}: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 打印左侧导航栏附近的元素
    print("\n=== 左侧导航栏 (x<400) ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if rect.left < 400 and name and len(name.strip()) > 1:
                print(f"  '{name}' at ({rect.left}, {rect.top})")
        except:
            pass

except Exception as e:
    print(f"Error: {e}")
