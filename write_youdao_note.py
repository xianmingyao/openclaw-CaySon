# -*- coding: utf-8 -*-
"""
使用 desktop-control 操作 Chrome 写入有道云笔记学习总结
"""
import time
import sys
import os

# 添加 skills 路径
skills_path = r'E:\workspace\skills\desktop-control-1-0-0'
sys.path.insert(0, skills_path)

# 导入 DesktopController
from __init__ import DesktopController

# 初始化控制器
dc = DesktopController(failsafe=True)

print("=== 开始操作 Chrome ===")

# 1. 激活 Chrome 窗口
print("1. 激活 Chrome 窗口...")
dc.activate_window("Chrome")
time.sleep(1)

# 2. 获取屏幕尺寸
width, height = dc.get_screen_size()
print(f"   屏幕尺寸: {width}x{height}")

# 3. 打开有道云笔记
print("2. 打开有道云笔记...")
dc.hotkey("ctrl", "l")  # 聚焦地址栏
time.sleep(0.3)
dc.type_text("https://note.youdao.com/web/#/file/WEBa2b687261f801b0d8ba1335e93450410/empty")
dc.press("enter")
time.sleep(3)

# 4. 截图查看当前状态
print("3. 截图查看当前状态...")
dc.screenshot(filename=r"E:\workspace\step1_youdao.png")
print("   已保存截图到 step1_youdao.png")

# 5. 等待页面加载
time.sleep(2)

# 6. 获取鼠标位置
pos = dc.get_mouse_position()
print(f"   当前鼠标位置: {pos}")

print("\n=== 操作完成，请在 Chrome 中确认页面状态 ===")
