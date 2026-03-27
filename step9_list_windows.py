# -*- coding: utf-8 -*-
"""
步骤9：列出所有窗口并切换
"""
import time
import sys

skills_path = r'E:\workspace\skills\desktop-control-1-0-0'
sys.path.insert(0, skills_path)

from __init__ import DesktopController

dc = DesktopController(failsafe=True)

print("=== 步骤9：列出所有窗口 ===")

# 1. 获取所有窗口
print("1. 获取所有窗口...")
windows = dc.get_all_windows()
print(f"   找到 {len(windows)} 个窗口:")
for i, title in enumerate(windows, 1):
    print(f"   {i}. {title}")

# 2. 尝试激活有道云笔记
print("\n2. 尝试激活有道云笔记...")
result = dc.activate_window("有道云笔记")
print(f"   结果: {result}")
time.sleep(0.5)

# 3. 获取当前活动窗口
active = dc.get_active_window()
print(f"3. 当前活动窗口: {active}")

# 4. 截图
print("\n4. 截图...")
dc.screenshot(filename=r"E:\workspace\step9_windows.png")

print("\n=== 完成 ===")
