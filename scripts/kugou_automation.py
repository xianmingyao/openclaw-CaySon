"""
酷狗音乐自动化脚本 - 使用desktop-control技能
打开酷狗音乐网页版，搜索周杰伦-发如雪并播放
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
    print("=== KuGou Music Automation Script ===")
    
    # 1. 关闭可能存在的Chrome窗口
    print("[Step 0] Closing existing Chrome windows...")
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], 
                      capture_output=True, timeout=5)
        time.sleep(1)
    except:
        pass
    
    # 2. 打开酷狗音乐网页版
    print("[Step 1] Opening KuGou website...")
    kugou_url = 'https://www.kugou.com/yy/html/search.html'
    subprocess.Popen([CHROME_PATH, '--new-window', kugou_url])
    time.sleep(6)
    
    activate_window("Chrome")
    screenshot('step1_page_opened')
    
    # 3. 关闭可能存在的弹窗
    print("[Step 2] Closing popup if exists...")
    pyautogui.press('esc')
    time.sleep(0.5)
    pyautogui.click(x=960, y=50)  # 点击页面右上角关闭按钮
    time.sleep(1)
    
    activate_window("Chrome")
    screenshot('step2_popup_closed')
    
    # 4. 点击搜索框并输入搜索词
    print("[Step 3] Clicking search box and typing...")
    # 搜索框位置（页面顶部中央）
    pyautogui.click(x=450, y=100)
    time.sleep(0.5)
    
    # 清除搜索框内容
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.2)
    pyautogui.press('delete')
    time.sleep(0.3)
    
    # 输入搜索词
    pyautogui.typewrite('周杰伦 发如雪', interval=0.08)
    time.sleep(0.5)
    
    screenshot('step3_search_input')
    
    # 5. 按回车搜索
    print("[Step 4] Pressing Enter to search...")
    pyautogui.press('enter')
    time.sleep(4)
    
    activate_window("Chrome")
    screenshot('step4_search_results')
    
    # 6. 点击第一首歌曲
    print("[Step 5] Clicking first song...")
    pyautogui.click(x=500, y=300)
    time.sleep(1)
    
    screenshot('step5_song_clicked')
    
    # 7. 双击播放
    print("[Step 6] Double-clicking to play...")
    pyautogui.doubleClick(x=500, y=300)
    time.sleep(2)
    
    screenshot('step6_playing')
    
    # 8. 最终确认
    print("[Step 7] Final check...")
    time.sleep(3)
    
    activate_window("Chrome")
    screenshot('step7_final')
    
    print("=== Automation completed! ===")
    print("Check screenshots in:", SCREENSHOT_DIR)

if __name__ == "__main__":
    main()
