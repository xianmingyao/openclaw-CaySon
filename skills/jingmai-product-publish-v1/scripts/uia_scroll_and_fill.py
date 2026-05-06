# -*- coding: utf-8 -*-
# 滚动页面并继续填写
import platform
if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

try:
    from pywinauto import Desktop
    import pyautogui
    import time
    import pyperclip
    
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
    
    # ========== 1. 先关闭弹窗，聚焦窗口 ==========
    print("\n=== 1. 聚焦窗口 ===")
    pyautogui.press('escape')
    time.sleep(0.5)
    pyautogui.click(100, 100)  # 点击空白处关闭弹窗
    time.sleep(0.5)
    
    # ========== 2. 滚动到正确位置查看必填属性 ==========
    print("\n=== 2. 滚动到必填属性区域 ===")
    # 向上滚动到必填属性区域
    for i in range(3):
        pyautogui.scroll(5, x=1280, y=700)
        time.sleep(0.3)
    
    # ========== 3. 分析当前页面结构 ==========
    print("\n=== 3. 分析页面结构 ===")
    all_elements = jingmai.descendants()
    
    # 找所有"请选择"和"请输入"
    print("Looking for unfilled fields...")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if name in ["请选择", "请输入"] and rect.width() > 0:
                print(f"  '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # ========== 4. 尝试填写孔型配置为"8位" ==========
    print("\n=== 4. 填写孔型配置 ===")
    # 找孔型配置输入框
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            # 孔型配置label在y=848附近
            if "孔型" in name:
                print(f"  Found label: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 找Edit[7] - 孔型配置输入框
    edits = jingmai.descendants(control_type="Edit")
    if len(edits) > 7:
        hole_edit = edits[7]
        rect = hole_edit.rectangle()
        print(f"  Edit[7] at ({rect.left}, {rect.top})")
        
        # 点击并填写
        pyautogui.click(rect.left + 50, rect.top + 10)
        time.sleep(0.3)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.press('delete')
        time.sleep(0.2)
        
        pyperclip.copy("8")
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)
        print("  Filled: 8")
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
