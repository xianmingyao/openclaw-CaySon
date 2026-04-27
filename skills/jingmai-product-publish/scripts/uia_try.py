# -*- coding: utf-8 -*-
"""使用pywinauto操作京麦"""
import sys
sys.path.insert(0, r'E:\workspace\skills\jingmai-product-publish\scripts')

import time
from pywinauto import Application

# 京麦窗口HWND
JM_HWND = 1250920

if __name__ == "__main__":
    print("=== 使用pywinauto操作京麦 ===")
    
    try:
        # 连接到京麦进程
        app = Application(backend='win32').connect(handle=JM_HWND)
        print(f"Connected to window: {JM_HWND}")
        
        # 获取主窗口
        dlg = app.window(handle=JM_HWND)
        print(f"Window: {dlg.window_text()}")
        
        # 打印可用方法
        print("\n=== 窗口控件列表 (前20个) ===")
        try:
            children = dlg.children()
            for i, child in enumerate(children[:20]):
                try:
                    print(f"  {i}: {child.control_type() or 'unknown'} - '{child.window_text()[:30] if child.window_text() else '(no text)'}' - {child.class_name()}")
                except Exception as e:
                    print(f"  {i}: Error getting child info: {e}")
        except Exception as e:
            print(f"Error getting children: {e}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
