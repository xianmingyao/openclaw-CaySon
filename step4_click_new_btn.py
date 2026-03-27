# -*- coding: utf-8 -*-
"""
步骤4：点击左上角新建按钮
"""
import time
import sys

skills_path = r'E:\workspace\skills\desktop-control-1-0-0'
sys.path.insert(0, skills_path)

from __init__ import DesktopController

dc = DesktopController(failsafe=True)

print("=== 步骤4：点击左上角新建按钮 ===")

# 1. 激活 Chrome
dc.activate_window("Chrome")
time.sleep(0.5)

# 2. 点击左上角的新建按钮
# 根据2560x1440屏幕，左上角大约在 (100, 50-100)
print("点击左上角' + 新建 '按钮...")
dc.click(x=100, y=80)
time.sleep(1.5)

# 3. 截图确认
dc.screenshot(filename=r"E:\workspace\step4_result.png")
print("截图已保存")

print("\n=== 请确认是否出现新建菜单 ===")
