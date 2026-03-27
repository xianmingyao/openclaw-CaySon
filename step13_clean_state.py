# -*- coding: utf-8 -*-
"""
步骤13：清理窗口状态后重试
"""
import time
import sys

skills_path = r'E:\workspace\skills\desktop-control-1-0-0'
sys.path.insert(0, skills_path)

from __init__ import DesktopController

dc = DesktopController(failsafe=True)

print("=== 步骤13：清理窗口状态 ===")

# 1. 最小化所有窗口
print("1. 按 Win+M 最小化所有窗口...")
dc.hotkey("win", "m")
time.sleep(0.5)

# 2. 激活有道云笔记
print("2. 激活有道云笔记...")
result = dc.activate_window("有道云笔记")
print(f"   结果: {result}")
time.sleep(1)

# 3. 获取当前活动窗口
active = dc.get_active_window()
print(f"3. 当前活动窗口: {active}")

# 4. 点击左侧 + 新建
print("4. 点击 + 新建...")
dc.click(x=80, y=75)  # 左侧最上方
time.sleep(1)

# 5. 截图
print("5. 截图...")
dc.screenshot(filename=r"E:\workspace\step13_result.png")

print("\n=== 请确认 ===")
