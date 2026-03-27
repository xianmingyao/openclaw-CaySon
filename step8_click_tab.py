# -*- coding: utf-8 -*-
"""
步骤8：点击有道云笔记标签页
"""
import time
import sys

skills_path = r'E:\workspace\skills\desktop-control-1-0-0'
sys.path.insert(0, skills_path)

from __init__ import DesktopController

dc = DesktopController(failsafe=True)

print("=== 步骤8：点击有道云笔记标签页 ===")

# 1. 激活 Chrome
print("1. 激活 Chrome...")
dc.activate_window("Chrome")
time.sleep(0.5)

# 2. 点击标签栏位置 (假设有道云笔记在第二个标签)
# 屏幕宽度2560，标签栏大约在 y=40 的位置
# 第一个标签后，第二个标签大约在 x=200
print("2. 点击第二个标签页...")
dc.click(x=200, y=40)
time.sleep(1)

# 3. 截图
print("3. 截图确认...")
dc.screenshot(filename=r"E:\workspace\step8_tab.png")

# 4. 获取当前活动窗口
active = dc.get_active_window()
print(f"4. 当前活动窗口: {active}")

print("\n=== 请确认是否切换到了有道云笔记 ===")
