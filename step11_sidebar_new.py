# -*- coding: utf-8 -*-
"""
步骤11：点击左侧边栏新建按钮
"""
import time
import sys

skills_path = r'E:\workspace\skills\desktop-control-1-0-0'
sys.path.insert(0, skills_path)

from __init__ import DesktopController

dc = DesktopController(failsafe=True)

print("=== 步骤11：点击左侧边栏新建按钮 ===")

# 1. 激活有道云笔记
print("1. 激活有道云笔记...")
dc.activate_window("有道云笔记")
time.sleep(0.5)

# 2. 点击左侧边栏顶部的 + 新建 按钮
# 屏幕宽度2560，+ 新建按钮应该在左侧，大约 x=80-100
print("2. 点击左侧边栏顶部...")
dc.click(x=85, y=85)  # 左侧最上方
time.sleep(0.5)

# 3. 双击（有时候双击效果更好）
print("3. 双击...")
dc.double_click(x=85, y=85)
time.sleep(1.5)

# 4. 截图
print("4. 截图...")
dc.screenshot(filename=r"E:\workspace\step11_sidebar.png")

print("\n=== 请确认 ===")
