"""
QQ音乐自动化脚本 v3 - 直接URL搜索
打开QQ音乐搜索页面，播放周杰伦-发如雪
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

def activate_chrome():
    """激活Chrome窗口"""
    try:
        windows = gw.getWindowsWithTitle("Chrome")
        if windows:
            windows[0].activate()
            return True
        return False
    except Exception as e:
        print(f"[warn] Window activation failed: {e}")
        return False

def main():
    print("=== QQ Music Automation Script v3 ===")
    
    # 1. 关闭可能存在的Chrome窗口
    print("[Step 0] Closing existing Chrome windows...")
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], 
                      capture_output=True, timeout=5)
        time.sleep(1)
    except:
        pass
    
    # 2. 直接打开搜索URL
    print("[Step 1] Opening QQ Music search page...")
    search_url = 'https://y.qq.com/portal/search.html#search=song&key=%E5%8F%91%E5%A6%82%E9%9B%AA'
    subprocess.Popen([CHROME_PATH, '--new-window', search_url])
    time.sleep(6)  # 等待页面加载
    
    activate_chrome()
    screenshot('step1_search_page')
    
    # 3. 等待搜索结果加载
    print("[Step 2] Waiting for search results to load...")
    time.sleep(5)
    
    activate_chrome()
    screenshot('step2_results_loaded')
    
    # 4. 点击第一首歌曲（发如雪）
    print("[Step 3] Clicking the first song (Fa Ru Xue)...")
    # 搜索结果页面，歌曲列表的第一首
    # QQ音乐搜索结果页面的歌曲列表通常在页面中上部
    pyautogui.click(x=500, y=320)
    time.sleep(1)
    
    screenshot('step3_after_first_click')
    
    # 5. 双击确保播放
    print("[Step 4] Double-clicking to play...")
    pyautogui.doubleClick(x=500, y=320)
    time.sleep(2)
    
    screenshot('step4_playing')
    
    # 6. 确认播放状态
    print("[Step 5] Checking play status...")
    time.sleep(3)
    
    activate_chrome()
    screenshot('step5_final_check')
    
    print("=== Automation completed! ===")
    print("Please check the screenshots in:")
    print(SCREENSHOT_DIR)

if __name__ == "__main__":
    main()
