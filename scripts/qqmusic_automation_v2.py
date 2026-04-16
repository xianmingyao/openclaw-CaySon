"""
QQ音乐自动化脚本 v2 - 使用desktop-control技能
打开QQ音乐网页版，搜索周杰伦-发如雪并播放
"""
import pyautogui
import time
import os
import sys
import subprocess

# 配置PyAutoGUI
pyautogui.MINIMUM_DURATION = 0
pyautogui.MINIMUM_SLEEP = 0
pyautogui.PAUSE = 0.1

# 截图保存目录
SCREENSHOT_DIR = r'E:\workspace\scripts\screenshots'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def screenshot(name):
    """保存截图"""
    path = os.path.join(SCREENSHOT_DIR, f'{name}.png')
    pyautogui.screenshot(path)
    print(f"[screenshot] {path}")
    return path

def activate_window_by_title(title_part):
    """激活窗口"""
    try:
        import pygetwindow as gw
        windows = gw.getWindowsWithTitle(title_part)
        if windows:
            windows[0].activate()
            return True
        return False
    except Exception as e:
        print(f"[warn] Window activation failed: {e}")
        return False

def main():
    print("=== QQ Music Automation Script v2 ===")
    
    # 1. 首先关闭可能存在的Chrome窗口
    print("[Step 0] Closing existing Chrome windows...")
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], 
                      capture_output=True, timeout=5)
        time.sleep(1)
    except:
        pass
    
    # 2. 打开Chrome浏览器（新窗口）
    print("[Step 1] Opening Chrome browser...")
    chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
    subprocess.Popen([chrome_path, '--new-window', 'https://y.qq.com'])
    time.sleep(5)  # 等待Chrome启动
    
    # 激活Chrome窗口
    activate_window_by_title("Chrome")
    time.sleep(1)
    screenshot('step1_chrome_opened')
    
    # 3. 等待页面加载
    print("[Step 2] Waiting for QQ Music page to load...")
    time.sleep(5)
    
    # 激活Chrome窗口确保焦点
    activate_window_by_title("Chrome")
    time.sleep(1)
    screenshot('step2_page_loaded')
    
    # 4. 点击搜索框区域（QQ音乐首页的搜索框）
    print("[Step 3] Clicking search box...")
    # QQ音乐首页搜索框的大致位置（顶部中央）
    pyautogui.click(x=500, y=120)
    time.sleep(1)
    
    # 5. 输入搜索关键词
    print("[Step 4] Typing search keywords...")
    pyautogui.typewrite('fa ru xue', interval=0.08)
    time.sleep(0.5)
    
    # 6. 按回车搜索
    print("[Step 5] Pressing Enter to search...")
    pyautogui.press('enter')
    time.sleep(4)  # 等待搜索结果加载
    
    screenshot('step3_search_results')
    
    # 7. 点击第一首歌曲（搜索结果列表中的歌曲）
    print("[Step 6] Clicking first song in results...")
    # 搜索结果页面的第一首歌位置（页面中部）
    pyautogui.click(x=600, y=350)
    time.sleep(2)
    
    screenshot('step4_after_click')
    
    # 8. 双击确保播放
    print("[Step 7] Double-clicking to ensure play...")
    pyautogui.doubleClick(x=600, y=350)
    time.sleep(2)
    
    screenshot('step5_final')
    
    print("=== Automation completed! ===")
    print("Please check the screenshots in:")
    print(SCREENSHOT_DIR)

if __name__ == "__main__":
    main()
