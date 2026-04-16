"""
网易云音乐自动化脚本 - 使用desktop-control技能
打开网易云音乐，搜索周杰伦-发如雪并播放
"""
import pyautogui
import time
import os
import subprocess
import pygetwindow as gw

# 配置PyAutoGUI
pyautogui.MINIMUM_DURATION = 0
pyautogui.MINIMUM_SLEEP = 0
pyautogui.PAUSE = 0.1

# 截图保存目录
SCREENSHOT_DIR = r'E:\workspace\scripts\screenshots'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

CHROME_PATH = r'C:\Program Files\Google\Chrome\Application\chrome.exe'

def screenshot(name):
    """保存截图"""
    path = os.path.join(SCREENSHOT_DIR, f'{name}.png')
    pyautogui.screenshot(path)
    print(f"[screenshot] {path}")
    return path

def activate_window(title_part):
    """激活窗口"""
    try:
        windows = gw.getWindowsWithTitle(title_part)
        if windows:
            windows[0].activate()
            time.sleep(0.5)
            return True
        return False
    except Exception as e:
        print(f"[warn] Window activation failed: {e}")
        return False

def main():
    print("=== Cloud Music Automation Script ===")
    
    # 1. 关闭可能存在的Chrome窗口
    print("[Step 0] Closing existing Chrome windows...")
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], 
                      capture_output=True, timeout=5)
        time.sleep(1)
    except:
        pass
    
    # 2. 打开网易云音乐网页版
    print("[Step 1] Opening Cloud Music website...")
    cloudmusic_url = 'https://music.163.com/#/search/m/?s=%E5%91%A8%E6%9D%B0%E5%8C%85%20%E5%8F%91%E5%A6%82%E9%9B%AA&type=1'
    subprocess.Popen([CHROME_PATH, '--new-window', cloudmusic_url])
    time.sleep(6)
    
    activate_window("Chrome")
    screenshot('step1_page_opened')
    
    # 3. 等待搜索结果加载
    print("[Step 2] Waiting for search results...")
    time.sleep(5)
    
    activate_window("Chrome")
    screenshot('step2_results_loaded')
    
    # 4. 关闭可能存在的弹窗
    print("[Step 3] Closing popup if exists...")
    pyautogui.press('esc')
    time.sleep(0.5)
    
    activate_window("Chrome")
    screenshot('step3_popup_closed')
    
    # 5. 点击搜索结果中的歌曲
    print("[Step 4] Clicking the song in results...")
    # 网易云音乐搜索结果页面的歌曲位置
    # 第一首歌的大致位置
    pyautogui.click(x=520, y=340)
    time.sleep(1)
    
    screenshot('step4_song_clicked')
    
    # 6. 双击播放
    print("[Step 5] Double-clicking to play...")
    pyautogui.doubleClick(x=520, y=340)
    time.sleep(2)
    
    screenshot('step5_playing')
    
    # 7. 等待播放
    print("[Step 6] Waiting for playback...")
    time.sleep(3)
    
    activate_window("Chrome")
    screenshot('step6_final')
    
    print("=== Automation completed! ===")
    print("Check screenshots in:", SCREENSHOT_DIR)

if __name__ == "__main__":
    main()
