# -*- coding: utf-8 -*-
# 列出所有可输入元素
import platform
if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

try:
    from pywinauto import Desktop
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
    
    # Edit元素
    edits = jingmai.descendants(control_type="Edit")
    print(f"Edit elements ({len(edits)}):")
    for i, e in enumerate(edits):
        try:
            print(f"  [{i}] '{e.element_info.name}' at ({e.rectangle().left}, {e.rectangle().top})")
        except:
            pass
    
    # ComboBox元素（可能下拉框）
    combos = jingmai.descendants(control_type="ComboBox")
    print(f"ComboBox elements ({len(combos)}):")
    for i, c in enumerate(combos):
        try:
            print(f"  [{i}] '{c.element_info.name}' at ({c.rectangle().left}, {c.rectangle().top})")
        except:
            pass
    
    # TextBox元素
    textboxes = jingmai.descendants(control_type="TextBox")
    print(f"TextBox elements ({len(textboxes)}):")
    for i, t in enumerate(textboxes):
        try:
            print(f"  [{i}] '{t.element_info.name}' at ({t.rectangle().left}, {t.rectangle().top})")
        except:
            pass

except Exception as e:
    print(f"Error: {e}")
