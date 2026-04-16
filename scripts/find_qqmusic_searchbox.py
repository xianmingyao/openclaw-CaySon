"""
截取QQ音乐界面并分析搜索框位置
"""
import pyautogui
import subprocess
import time
import sys
sys.path.insert(0, r'E:\workspace\skills\desktop-control-1-0-0')
import importlib.util

# 动态加载技能
def load_skill():
    spec = importlib.util.spec_from_file_location("dc", r'E:\workspace\skills\desktop-control-1-0-0\__init__.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules["dc"] = module
    spec.loader.exec_module(module)
    return module

dc = load_skill().DesktopController()

# 激活QQ音乐
print("激活QQ音乐窗口...")
dc.activate_window_by_process("QQMusic")
time.sleep(1)

# 截图
screenshot_path = r'E:\workspace\scripts\screenshots\qqmusic_only.png'
pyautogui.screenshot(screenshot_path)
print(f"截图保存到: {screenshot_path}")

# 获取鼠标位置帮助定位
print("\n请移动鼠标到QQ音乐界面的搜索框上...")
print("按Ctrl+C终止程序")

# 等待用户移动鼠标并点击
try:
    while True:
        x, y = pyautogui.position()
        print(f"\r鼠标位置: x={x}, y={y}", end="", flush=True)
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n\n程序结束")
