# -*- coding: utf-8 -*-
"""使用pywinauto查找京麦搜索框"""
import sys
sys.path.insert(0, r'E:\workspace\skills\jingmai-product-publish\scripts')

import time
from pywinauto import Application
from pywinauto.win32functions import GetClientRect
import win32gui
import win32api
import win32con

JM_HWND = 1250920

if __name__ == "__main__":
    print("=== 查找京麦搜索框 ===")
    
    try:
        app = Application(backend='win32').connect(handle=JM_HWND)
        dlg = app.window(handle=JM_HWND)
        
        # 尝试多种方式查找搜索框
        search_x, search_y = None, None
        
        # 方法1: 尝试查找Edit控件
        try:
            edits = dlg.children(control_type='Edit')
            print(f"Found {len(edits)} Edit controls")
            for i, edit in enumerate(edits):
                try:
                    rect = edit.rectangle()
                    print(f"  Edit {i}: {rect}")
                    # 检查是否在合理位置（窗口上半部分）
                    if rect.top < 500:
                        search_x = (rect.left + rect.right) // 2
                        search_y = (rect.top + rect.bottom) // 2
                        print(f"  -> This looks like search box!")
                except Exception as e:
                    print(f"  Edit {i} error: {e}")
        except Exception as e:
            print(f"Finding Edit controls failed: {e}")
        
        # 方法2: 尝试查找所有输入框
        try:
            combos = dlg.children(control_type='ComboBox')
            print(f"Found {len(combos)} ComboBox controls")
            for i, combo in enumerate(combos):
                try:
                    rect = combo.rectangle()
                    print(f"  Combo {i}: {rect}")
                except Exception as e:
                    print(f"  Combo {i} error: {e}")
        except Exception as e:
            print(f"Finding ComboBox controls failed: {e}")
        
        # 打印所有Text控件
        try:
            texts = dlg.children(control_type='Text')
            print(f"Found {len(texts)} Text controls")
            for i, text in enumerate(texts[:30]):
                try:
                    rect = text.rectangle()
                    txt = text.window_text()
                    if txt and len(txt) < 50:
                        print(f"  Text {i}: '{txt}' at {rect}")
                except:
                    pass
        except Exception as e:
            print(f"Finding Text controls failed: {e}")
        
        # 如果找到了搜索框，打印位置
        if search_x and search_y:
            print(f"\nSearch box position: ({search_x}, {search_y})")
        else:
            print("\nSearch box not found by automation")
            
        # 方法3: 根据京麦页面布局，搜索框通常在页面顶部中央
        # 从截图分析，搜索框大约在 (1200, 160) 左右
        print("\nUsing fallback position based on page layout...")
        search_x = 1200
        search_y = 160
        print(f"Fallback position: ({search_x}, {search_y})")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
