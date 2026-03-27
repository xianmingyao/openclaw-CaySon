# -*- coding: utf-8 -*-
"""
步骤6：使用键盘快捷键新建笔记
"""
import time
import sys

skills_path = r'E:\workspace\skills\desktop-control-1-0-0'
sys.path.insert(0, skills_path)

from __init__ import DesktopController

dc = DesktopController(failsafe=True)

print("=== 步骤6：使用键盘快捷键新建笔记 ===")

# 1. 激活 Chrome
print("1. 激活 Chrome...")
result = dc.activate_window("Chrome")
print(f"   激活结果: {result}")
time.sleep(0.5)

# 2. 使用 Ctrl+N 新建笔记
print("2. 按 Ctrl+N 新建笔记...")
dc.hotkey("ctrl", "n")
time.sleep(1.5)

# 3. 截图确认
print("3. 截图确认...")
dc.screenshot(filename=r"E:\workspace\step6_result.png")
print("   截图已保存")

# 4. 获取当前窗口
active = dc.get_active_window()
print(f"4. 当前活动窗口: {active}")

print("\n=== 请确认是否打开了新建笔记 ===")
