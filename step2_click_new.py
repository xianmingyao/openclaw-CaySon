# -*- coding: utf-8 -*-
"""
步骤2：点击新建笔记按钮
"""
import time
import sys

skills_path = r'E:\workspace\skills\desktop-control-1-0-0'
sys.path.insert(0, skills_path)

from __init__ import DesktopController

dc = DesktopController(failsafe=True)

print("=== 步骤2：点击新建笔记按钮 ===")

# 1. 激活 Chrome
dc.activate_window("Chrome")
time.sleep(0.5)

# 2. 获取当前鼠标位置
pos = dc.get_mouse_position()
print(f"当前鼠标位置: {pos}")

# 3. 点击页面中间位置（新建笔记按钮应该在附近）
# 根据截图，按钮在页面中下方
print("点击新建笔记按钮位置...")
dc.click(x=1280, y=720)  # 中间位置
time.sleep(1)

# 4. 截图查看
dc.screenshot(filename=r"E:\workspace\step2_clicked.png")
print("截图已保存")

print("\n=== 完成，请确认是否打开了新建笔记 ===")
