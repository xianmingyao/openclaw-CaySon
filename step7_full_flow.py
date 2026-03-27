# -*- coding: utf-8 -*-
"""
步骤7：完整流程 - 重新导航并创建笔记
"""
import time
import sys

skills_path = r'E:\workspace\skills\desktop-control-1-0-0'
sys.path.insert(0, skills_path)

from __init__ import DesktopController

dc = DesktopController(failsafe=True)

print("=== 步骤7：完整流程创建笔记 ===")

# 1. 激活 Chrome
print("1. 激活 Chrome...")
dc.activate_window("Chrome")
time.sleep(0.5)

# 2. 按 F6 或 Ctrl+L 聚焦地址栏
print("2. 聚焦地址栏...")
dc.press("f6")
time.sleep(0.3)

# 3. 输入新的 URL
print("3. 输入 URL...")
url = "https://note.youdao.com/web/#/file/WEBa2b687261f801b0d8ba1335e93450410/empty"
dc.type_text(url)
time.sleep(0.3)

# 4. 按 Enter
print("4. 访问页面...")
dc.press("enter")
time.sleep(3)

# 5. 截图确认页面加载
print("5. 截图确认...")
dc.screenshot(filename=r"E:\workspace\step7_page_loaded.png")

# 6. 尝试用 Tab 键导航到新建按钮
print("6. 使用 Tab 键导航...")
for i in range(10):
    dc.press("tab")
    time.sleep(0.2)
    print(f"   Tab {i+1}/10")

time.sleep(1)

# 7. 按 Enter 点击
print("7. 按 Enter 点击...")
dc.press("enter")
time.sleep(2)

# 8. 截图
print("8. 截图确认...")
dc.screenshot(filename=r"E:\workspace\step7_after_enter.png")

print("\n=== 完成，请确认结果 ===")
