"""
QQ音乐自动化 - 搜索并播放《发如雪》
使用 desktop-control 技能
"""
import pyautogui
import time
import os
import subprocess
import sys
import importlib.util

SCREENSHOT_DIR = r'E:\workspace\scripts\screenshots'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

DESKTOP_APP_PATH = r'E:\Program Files\Tencent\QQMusic\QQMusic.exe'

def load_skill():
    spec = importlib.util.spec_from_file_location("dc", 
        r'E:\workspace\skills\desktop-control-1-0-0\__init__.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules["dc"] = module
    spec.loader.exec_module(module)
    return module

def main():
    print("=== QQ音乐自动化 - 搜索发如雪 ===")
    
    dc = load_skill().DesktopController()
    
    # 1. 启动QQ音乐
    print("[1] 启动QQ音乐...")
    subprocess.Popen([DESKTOP_APP_PATH])
    time.sleep(6)
    
    # 2. 激活窗口
    print("[2] 激活QQ音乐窗口...")
    dc.activate_window_by_process("QQMusic")
    time.sleep(1)
    
    # 3. 关闭可能存在的弹窗
    print("[3] 关闭弹窗...")
    pyautogui.press('esc')
    time.sleep(0.5)
    dc.activate_window_by_process("QQMusic")
    time.sleep(0.5)
    
    # 4. 点击搜索框 (242, 22)
    print("[4] 点击搜索框...")
    dc.click(242, 22)
    time.sleep(1)
    
    # 5. 输入搜索词
    print("[5] 输入搜索词: 发如雪...")
    dc.type_text("faruxue", interval=0.08)
    time.sleep(0.5)
    
    # 6. 按回车搜索
    print("[6] 执行搜索...")
    dc.activate_window_by_process("QQMusic")
    time.sleep(0.5)
    dc.press("enter")
    time.sleep(5)
    
    # 7. 截图确认搜索结果
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'result_search.png'))
    
    # 8. 点击第一首歌（发如雪）
    print("[7] 点击《发如雪》...")
    dc.click(300, 436)
    time.sleep(1)
    
    # 9. 双击播放
    print("[8] 双击播放...")
    dc.double_click(300, 436)
    time.sleep(3)
    
    # 10. 最终确认
    print("[9] 最终确认...")
    dc.activate_window_by_process("QQMusic")
    time.sleep(3)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'result_final.png'))
    
    print("=== 完成 ===")
    print(f"截图保存于: {SCREENSHOT_DIR}")

if __name__ == "__main__":
    main()
