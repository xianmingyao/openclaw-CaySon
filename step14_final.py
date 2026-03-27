# -*- coding: utf-8 -*-
"""
步骤14：重新聚焦有道云笔记并直接输入
"""
import time
import sys

skills_path = r'E:\workspace\skills\desktop-control-1-0-0'
sys.path.insert(0, skills_path)

from __init__ import DesktopController

dc = DesktopController(failsafe=True)

print("=== 步骤14：重新聚焦有道云笔记 ===")

# 1. 激活有道云笔记
print("1. 激活有道云笔记...")
dc.activate_window("有道云笔记")
time.sleep(1)

# 2. 获取当前活动窗口
active = dc.get_active_window()
print(f"2. 当前活动窗口: {active}")

# 3. 截图看当前状态
print("3. 截图...")
dc.screenshot(filename=r"E:\workspace\step14_current.png")

# 4. 如果窗口正确激活，尝试移动鼠标到按钮位置
print("4. 移动鼠标到 + 新建 按钮...")
dc.move_mouse(85, 80)
time.sleep(0.3)

# 5. 获取位置
pos = dc.get_mouse_position()
print(f"5. 鼠标位置: {pos}")

# 6. 点击
print("6. 点击...")
dc.click()
time.sleep(1)

# 7. 截图
print("7. 截图...")
dc.screenshot(filename=r"E:\workspace\step14_after_click.png")

print("\n=== 请确认 ===")
