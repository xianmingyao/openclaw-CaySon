# -*- coding: utf-8 -*-
# 在类目搜索框输入"中低压配电"并搜索
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
    
    # 找所有Edit
    edits = jingmai.descendants(control_type="Edit")
    print(f"Found {len(edits)} Edit elements:")
    
    # 找类目搜索框 - 通常在页面中部
    category_edit = None
    for i, edit in enumerate(edits):
        try:
            name = edit.element_info.name or ""
            rect = edit.rectangle()
            # 跳过顶部的AI搜索框
            if rect.top > 100 and "AI搜索" not in name:
                print(f"  [{i}] Category candidate: '{name}' at ({rect.left}, {rect.top}) size {rect.width()}x{rect.height()}")
                category_edit = edit
                break
            else:
                print(f"  [{i}] Top search: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    if category_edit:
        rect = category_edit.rectangle()
        print(f"\nUsing Edit at ({rect.left}, {rect.top})...")
        
        # 点击激活
        pyautogui.click(rect.left + 100, rect.top + 10)
        time.sleep(0.5)
        
        # 清除
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.press('delete')
        time.sleep(0.2)
        
        # 输入
        pyautogui.typewrite("中低压配电", interval=0.1)
        time.sleep(0.5)
        
        # 回车
        pyautogui.press("enter")
        time.sleep(3)
        
        print("Done!")
    else:
        print("Category Edit not found, trying all edits...")
        # 尝试所有Edit
        for i, edit in enumerate(edits):
            try:
                rect = edit.rectangle()
                print(f"  [{i}] '{edit.element_info.name}' at ({rect.left}, {rect.top})")
                if rect.top > 100:
                    # 点击测试
                    pyautogui.click(rect.left + 50, rect.top + 10)
                    time.sleep(0.3)
                    pyautogui.hotkey('ctrl', 'a')
                    pyautogui.press('delete')
                    pyautogui.typewrite("中低压配电", interval=0.1)
                    time.sleep(0.3)
                    pyautogui.press("enter")
                    time.sleep(2)
                    print(f"  Tried Edit[{i}]")
                    break
            except:
                pass

except Exception as e:
    print(f"Error: {e}")
