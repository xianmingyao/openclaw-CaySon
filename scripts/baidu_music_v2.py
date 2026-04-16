"""
百度音乐自动化脚本 v2 - 处理浏览器恢复
使用desktop-control技能搜索并播放周杰伦-发如雪
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

def handle_chrome_restore():
    """处理Chrome恢复提示"""
    # 查找并点击恢复按钮
    try:
        # 尝试点击Chrome窗口的恢复区域
        # 恢复按钮通常在右上角
        pyautogui.click(x=1200, y=50)  # 右上角区域
        time.sleep(0.5)
        pyautogui.press('enter')  # 可能默认选中了恢复
        time.sleep(1)
    except:
        pass

def main():
    print("=== Baidu Music Automation Script v2 ===")
    
    # 1. 关闭可能存在的Chrome窗口
    print("[Step 0] Closing existing Chrome windows...")
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], 
                      capture_output=True, timeout=5)
        time.sleep(1)
    except:
        pass
    
    # 2. 打开百度音乐搜索页面
    print("[Step 1] Opening Baidu Music search page...")
    search_url = 'https://music.baidu.com/search?key=%E5%91%A8%E6%9D%B0%E5%8C%85%E5%8F%91%E5%A6%82%E9%9B%AA'
    subprocess.Popen([CHROME_PATH, '--new-window', search_url])
    time.sleep(6)
    
    activate_window("Chrome")
    
    # 3. 处理Chrome恢复提示
    print("[Step 1.5] Handling Chrome restore prompt...")
    handle_chrome_restore()
    time.sleep(2)
    
    activate_window("Chrome")
    screenshot('step1_page_opened')
    
    # 4. 等待页面加载
    print("[Step 2] Waiting for page to fully load...")
    time.sleep(5)
    
    activate_window("Chrome")
    screenshot('step2_page_loaded')
    
    # 5. 关闭可能存在的弹窗
    print("[Step 3] Closing popup if exists...")
    pyautogui.press('esc')
    time.sleep(0.5)
    
    activate_window("Chrome")
    screenshot('step3_clean_state')
    
    # 6. 点击第一首歌曲
    print("[Step 4] Clicking first song...")
    pyautogui.click(x=500, y=300)
    time.sleep(1)
    
    screenshot('step4_song_clicked')
    
    # 7. 双击播放
    print("[Step 5] Double-clicking to play...")
    pyautogui.doubleClick(x=500, y=300)
    time.sleep(2)
    
    screenshot('step5_playing')
    
    # 8. 最终确认
    print("[Step 6] Final check...")
    time.sleep(3)
    
    activate_window("Chrome")
    screenshot('step6_final')
    
    print("=== Automation completed! ===")
    print("Check screenshots in:", SCREENSHOT_DIR)

if __name__ == "__main__":
    main()
