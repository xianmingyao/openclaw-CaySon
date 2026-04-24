# -*- coding: utf-8 -*-
"""
列出当前页面的所有类目选项
"""
import platform
if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

print("Listing all category options...")

try:
    from pywinauto import Desktop
    
    desktop = Desktop(backend="uia")
    all_windows = desktop.windows()
    
    jingmai = None
    for w in all_windows:
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
        print("Main window not found!")
        exit(1)
    
    # 查找所有ListItem或类似元素
    print("Looking for category ListItem elements...")
    
    # 尝试ListControl
    lists = jingmai.descendants(control_type="List")
    print(f"Found {len(lists)} List elements")
    
    for i, lst in enumerate(lists):
        try:
            rect = lst.rectangle()
            print(f"[{i}] List at ({rect.left}, {rect.top}) size {rect.width()}x{rect.height()}")
        except:
            pass
    
    # 查找Custom
    customs = jingmai.descendants(control_type="Custom")
    print(f"Found {len(customs)} Custom elements")
    
    # 查找Group
    groups = jingmai.descendants(control_type="Group")
    print(f"Found {len(groups)} Group elements")
    
    # 打印所有文本元素在y=271-600范围内（类目选择区域）
    print("\n--- Category area Text elements (y: 200-600) ---")
    texts = jingmai.descendants(control_type="Text")
    for txt in texts:
        try:
            name = txt.element_info.name or ""
            rect = txt.rectangle()
            if 200 < rect.top < 600 and name and len(name) > 1:
                print(f"'{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
