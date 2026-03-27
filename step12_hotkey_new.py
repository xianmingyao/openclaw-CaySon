# -*- coding: utf-8 -*-
"""
步骤12：使用键盘快捷键创建新笔记
"""
import time
import sys

skills_path = r'E:\workspace\skills\desktop-control-1-0-0'
sys.path.insert(0, skills_path)

from __init__ import DesktopController

dc = DesktopController(failsafe=True)

print("=== 步骤12：使用键盘快捷键创建新笔记 ===")

# 1. 激活有道云笔记
print("1. 激活有道云笔记...")
dc.activate_window("有道云笔记")
time.sleep(0.5)

# 2. 获取当前活动窗口
active = dc.get_active_window()
print(f"2. 当前活动窗口: {active}")

# 3. 尝试不同的键盘快捷键
print("3. 尝试 Ctrl+Shift+N...")
dc.hotkey("ctrl", "shift", "n")
time.sleep(2)

# 4. 截图
print("4. 截图...")
dc.screenshot(filename=r"E:\workspace\step12_hotkey.png")

print("\n=== 请确认 ===")
