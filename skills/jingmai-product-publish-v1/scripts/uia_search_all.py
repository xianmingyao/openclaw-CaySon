# -*- coding: utf-8 -*-
"""
搜索所有元素找"中低压配电"
"""
import platform
if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

print("Searching for '中低压配电'...")

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
    
    print("Found main window")
    
    # 搜索所有元素
    print("Searching all elements...")
    all_elements = jingmai.descendants()
    
    print(f"Total elements: {len(all_elements)}")
    
    # 找包含"中低压"或"配电"的元素
    matches = []
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            ctype = elem.element_info.control_type or ""
            if "中低压" in name or "配电" in name or "插座" in name:
                rect = elem.rectangle()
                matches.append((ctype, name, rect.left, rect.top))
        except:
            pass
    
    print(f"\nFound {len(matches)} matches:")
    for ctype, name, x, y in matches:
        print(f"  {ctype}: '{name}' at ({x}, {y})")
    
    # 也打印所有文本元素
    print("\n--- All Text elements ---")
    texts = jingmai.descendants(control_type="Text")
    print(f"Total Text elements: {len(texts)}")
    
    # 打印前面20个看看
    for i, txt in enumerate(texts[:50]):
        try:
            name = txt.element_info.name or ""
            rect = txt.rectangle()
            if name and len(name) > 1:  # 只打印有意义的
                print(f"[{i}] '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
