# -*- coding: utf-8 -*-
"""使用UIAuto点击京麦搜索框"""
import sys
sys.path.insert(0, r'E:\workspace\skills\jingmai-product-publish\scripts')

from pywinauto import Application, timings
import win32gui
import time

# 连接到京麦进程
jm_hwnd = 1250920
print(f"连接京麦窗口 HWND: {jm_hwnd}")

# 尝试使用UIA backend连接
try:
    app = Application(backend='uia').connect(handle=jm_hwnd)
    print("UIA连接成功")
    
    # 获取主窗口
    dlg = app.window(handle=jm_hwnd)
    print(f"窗口标题: {dlg.window_text()}")
    
    # 打印所有可用的控件
    print("\n=== 查找搜索框 ===")
    
    # 尝试多种方式找搜索框
    for name in ['搜索', 'Search', '搜索框', 'edit', 'Text']:
        try:
            ctrl = dlg.child_window(title=name, control_type="Edit")
            if ctrl.exists(timeout=1):
                print(f"找到: {name}")
                ctrl.set_focus()
                ctrl.type_keys("插座")
                print("已输入: 插座")
                break
        except:
            pass
    
    # 打印子窗口信息用于调试
    print("\n=== 子窗口列表 ===")
    try:
        children = dlg.children()
        for child in children[:10]:
            try:
                print(f"  - {child.control_type()}: {child.window_text()[:30] if child.window_text() else '(empty)'}")
            except:
                pass
    except Exception as e:
        print(f"获取子窗口失败: {e}")
        
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
