# -*- coding: utf-8 -*-
"""
列出当前所有Edit元素
"""
import platform
if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

print("Listing all Edit elements...")

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
    
    # 找所有Edit
    edits = jingmai.descendants(control_type="Edit")
    print(f"Found {len(edits)} Edit elements:")
    
    for i, edit in enumerate(edits):
        try:
            name = edit.element_info.name or ""
            rect = edit.rectangle()
            print(f"[{i}] '{name}' at ({rect.left}, {rect.top}) size {rect.width()}x{rect.height()}")
        except Exception as e:
            print(f"[{i}] Error: {e}")
    
    # 找所有Button
    print("\nFound buttons:")
    buttons = jingmai.descendants(control_type="Button")
    for i, btn in enumerate(buttons[:20]):
        try:
            name = btn.element_info.name or ""
            rect = btn.rectangle()
            if name:
                print(f"[{i}] '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
