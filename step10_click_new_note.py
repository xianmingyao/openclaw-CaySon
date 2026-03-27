# -*- coding: utf-8 -*-
"""
步骤10：点击新建笔记按钮
"""
import time
import sys

skills_path = r'E:\workspace\skills\desktop-control-1-0-0'
sys.path.insert(0, skills_path)

from __init__ import DesktopController

dc = DesktopController(failsafe=True)

print("=== 步骤10：点击新建笔记按钮 ===")

# 1. 激活有道云笔记
print("1. 激活有道云笔记...")
dc.activate_window("有道云笔记")
time.sleep(0.5)

# 2. 获取屏幕尺寸
width, height = dc.get_screen_size()
print(f"2. 屏幕尺寸: {width}x{height}")

# 3. 点击中间的新建笔记按钮
# 页面中间，空文件夹提示下方
print("3. 点击'新建笔记'按钮...")
dc.click(x=1280, y=800)  # 中间偏下位置
time.sleep(1.5)

# 4. 截图
print("4. 截图...")
dc.screenshot(filename=r"E:\workspace\step10_new_note.png")

print("\n=== 请确认是否打开了新建笔记 ===")
