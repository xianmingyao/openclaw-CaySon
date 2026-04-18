"""
Trae Dialog Monitor - 使用 desktop-control 技能
监听Trae弹窗并自动选择选项1
"""
import pyautogui
import time
import os
import sys
import importlib.util

SCREENSHOT_DIR = r'E:\workspace\scripts\screenshots'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def load_skill():
    """加载 desktop-control 技能"""
    spec = importlib.util.spec_from_file_location("dc", 
        r'E:\workspace\skills\desktop-control-1-0-0\__init__.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules["dc"] = module
    spec.loader.exec_module(module)
    return module.DesktopController()

def monitor_once(dc):
    """执行一次监听检测"""
    timestamp = int(time.time())
    screenshot_path = os.path.join(SCREENSHOT_DIR, f'trae_monitor_{timestamp}.png')
    pyautogui.screenshot(screenshot_path)
    print(f"[{time.strftime('%H:%M:%S')}] Screenshot saved")
    
    # 尝试激活 Trae 窗口
    dc.activate_window_by_process("Trae")
    time.sleep(0.2)
    
    # 按数字键 1 选择第一个选项
    dc.press('1')
    print(f"[{time.strftime('%H:%M:%S')}] Pressed '1' via desktop-control skill")
    return True

def main():
    print("=== Trae Dialog Monitor (desktop-control skill) ===")
    print("Monitoring every 60 seconds...")
    print("Press Ctrl+C to stop\n")
    
    dc = load_skill()
    print(f"DesktopController initialized. Screen: {dc.get_screen_size()}")
    
    # 执行一次
    monitor_once(dc)
    
    # 循环监听
    try:
        while True:
            time.sleep(60)
            monitor_once(dc)
    except KeyboardInterrupt:
        print("\n=== Monitor Stopped ===")

if __name__ == "__main__":
    main()
