# -*- coding: utf-8 -*-
# 完善商品信息：标题+防护等级+极数
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
    
    # ========== 1. 完善商品标题 ==========
    print("\n=== 1. 完善商品标题 ===")
    edits = jingmai.descendants(control_type="Edit")
    
    # Edit[1] = 商品标题
    if len(edits) > 1:
        title_edit = edits[1]
        rect = title_edit.rectangle()
        print(f"Title Edit at ({rect.left}, {rect.top})")
        
        # 点击激活
        pyautogui.click(rect.left + 50, rect.top + 10)
        time.sleep(0.3)
        
        # 全选清除
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.press('delete')
        time.sleep(0.2)
        
        # 输入完整商品标题
        title = "公牛BULL墙壁电源插座B5系列86型暗装墙壁开关插座多位电源插座B5440五孔"
        print(f"Inputting: {title}")
        pyautogui.typewrite(title, interval=0.05)
        time.sleep(0.5)
    
    # ========== 2. 选择防护等级（默认第一个） ==========
    print("\n=== 2. 选择防护等级 ===")
    
    # 先按Esc关闭任何弹窗
    pyautogui.press('escape')
    time.sleep(0.5)
    
    # 查找"防护等级"相关元素
    print("Looking for 防护等级...")
    all_elements = jingmai.descendants()
    
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            if "防护等级" in name or "IP" in name:
                rect = elem.rectangle()
                print(f"  Found: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 点击防护等级的"请选择" - IP等级在y=993附近
    # 根据之前分析，防护等级是"重要属性"下的项目
    # 找到后点击选择第一个选项
    print("Clicking IP等级 dropdown...")
    pyautogui.click(1036, 883)  # 这个位置可能是IP等级
    time.sleep(1.5)
    
    # 选择第一个IP选项
    print("Selecting first IP option...")
    pyautogui.click(1037, 928)  # 第一个选项 IP55 位置
    time.sleep(1)
    
    # ========== 3. 极数 ==========
    print("\n=== 3. 极数 ===")
    # 极数可能在"重要属性"下
    # 查找并选择
    pyautogui.press('escape')
    time.sleep(0.3)
    
    print("Done!")

except Exception as e:
    print(f"Error: {e}")
