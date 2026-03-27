# -*- coding: utf-8 -*-
"""
步骤3：点击新建笔记按钮（调整位置）
"""
import time
import sys

skills_path = r'E:\workspace\skills\desktop-control-1-0-0'
sys.path.insert(0, skills_path)

from __init__ import DesktopController

dc = DesktopController(failsafe=True)

print("=== 步骤3：点击新建笔记按钮 ===")

# 1. 激活 Chrome
dc.activate_window("Chrome")
time.sleep(0.5)

# 2. 根据屏幕尺寸2560x1440，计算按钮位置
# 新建笔记按钮应该在页面中间偏下
# 页面宽度2560，中间大约1280
# 页面高度1440，按钮大约在720-800位置

print("尝试点击蓝色'新建笔记'按钮...")
dc.click(x=1280, y=760)  # 更精确的位置
time.sleep(1)

# 3. 再截图确认
dc.screenshot(filename=r"E:\workspace\step3_after_click.png")
print("截图已保存")

print("\n=== 请确认是否打开了新建笔记界面 ===")
