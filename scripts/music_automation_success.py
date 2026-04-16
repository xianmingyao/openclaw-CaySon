"""
智能音乐自动化脚本 - 完整成功版
"""
import pyautogui
import time
import os
import subprocess
import sys
import importlib.util
import ctypes

SCREENSHOT_DIR = r'E:\workspace\scripts\screenshots'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

DESKTOP_APP_PATH = r'E:\Program Files\Tencent\QQMusic\QQMusic.exe'

class RECT(ctypes.Structure):
    _fields_ = [('left', ctypes.c_long), ('top', ctypes.c_long), 
                ('right', ctypes.c_long), ('bottom', ctypes.c_long)]

def get_window_handle(process_name):
    result = subprocess.run(
        ['powershell', '-Command', f'Get-Process -Name {process_name} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty MainWindowHandle'],
        capture_output=True, text=True, timeout=5
    )
    return int(result.stdout.strip())

def get_window_rect(hwnd):
    user32 = ctypes.windll.user32
    rect = RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    return rect

def load_skill():
    spec = importlib.util.spec_from_file_location("dc", 
        r'E:\workspace\skills\desktop-control-1-0-0\__init__.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules["dc"] = module
    spec.loader.exec_module(module)
    return module

def main():
    print("=== Smart Music Automation - SUCCESS ===")
    
    dc = load_skill().DesktopController()
    
    # 1. 启动QQ音乐
    print("[Step 1] Starting QQMusic...")
    subprocess.Popen([DESKTOP_APP_PATH])
    time.sleep(6)
    
    # 2. 获取窗口位置
    print("[Step 2] Getting window rect...")
    hwnd = get_window_handle("QQMusic")
    rect = get_window_rect(hwnd)
    
    # 计算搜索框位置
    search_x = rect.left + 250
    search_y = rect.top + 30
    print(f"[INFO] Search box: ({search_x}, {search_y})")
    
    # 3. 激活窗口
    print("[Step 3] Activating window...")
    dc.activate_window_by_process("QQMusic")
    time.sleep(1)
    
    # 4. 关闭弹窗
    print("[Step 4] Closing popup...")
    pyautogui.press('esc')
    time.sleep(0.5)
    dc.activate_window_by_process("QQMusic")
    time.sleep(0.5)
    
    # 5. 点击搜索框
    print(f"[Step 5] Clicking search box...")
    dc.click(search_x, search_y)
    time.sleep(1)
    
    # 6. 输入搜索词
    print("[Step 6] Typing 'faruxue'...")
    dc.type_text("faruxue", interval=0.08)
    time.sleep(0.5)
    
    # 7. 按回车搜索
    print("[Step 7] Pressing Enter...")
    dc.activate_window_by_process("QQMusic")
    time.sleep(0.5)
    dc.press("enter")
    time.sleep(4)
    
    # 8. 点击第一首歌曲（发如雪）- 在搜索结果列表中
    print("[Step 8] Clicking first song (发如雪)...")
    # 搜索结果中的歌曲位置（相对于窗口）
    song_x = rect.left + 400  # 歌曲名在左侧
    song_y = rect.top + 250   # 第一首歌的位置
    print(f"[INFO] Clicking song at: ({song_x}, {song_y})")
    dc.click(song_x, song_y)
    time.sleep(1)
    
    # 9. 双击播放
    print("[Step 9] Double-clicking to play...")
    dc.double_click(song_x, song_y)
    time.sleep(3)
    
    # 10. 最终确认
    print("[Step 10] Final check...")
    dc.activate_window_by_process("QQMusic")
    time.sleep(3)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'success_final.png'))
    
    print("=== Automation Complete ===")

if __name__ == "__main__":
    main()
