# -*- coding: utf-8 -*-
"""
步骤5：查找并点击新建按钮
"""
import time
import sys

skills_path = r'E:\workspace\skills\desktop-control-1-0-0'
sys.path.insert(0, skills_path)

from __init__ import DesktopController

dc = DesktopController(failsafe=True)

print("=== 步骤5：精确查找并点击新建按钮 ===")

# 1. 激活 Chrome
dc.activate_window("Chrome")
time.sleep(0.5)

# 2. 先移动到侧边栏区域 (左侧)
print("移动到侧边栏区域...")
dc.move_mouse(80, 80)
time.sleep(0.5)

# 3. 获取位置
pos = dc.get_mouse_position()
print(f"当前鼠标位置: {pos}")

# 4. 点击
print("点击...")
dc.click()
time.sleep(1)

# 5. 再截图确认
dc.screenshot(filename=r"E:\workspace\step5_result.png")
print("截图已保存")

print("\n=== 请确认 ===")
