"""
智能音乐自动化脚本 v5 - 使用PowerShell激活UWP窗口
使用desktop-control技能
"""
import pyautogui
import time
import os
import subprocess
import sys

# 配置PyAutoGUI
pyautogui.MINIMUM_DURATION = 0
pyautogui.MINIMUM_SLEEP = 0
pyautogui.PAUSE = 0.1

# 截图保存目录
SCREENSHOT_DIR = r'E:\workspace\scripts\screenshots'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# 桌面端应用路径
DESKTOP_APP_PATH = r'E:\Program Files\Tencent\QQMusic\QQMusic.exe'
CHROME_PATH = r'C:\Program Files\Google\Chrome\Application\chrome.exe'

def screenshot(name):
    """保存截图"""
    path = os.path.join(SCREENSHOT_DIR, f'{name}.png')
    pyautogui.screenshot(path)
    print(f"[screenshot] {path}")
    return path

def activate_app_by_name(app_name):
    """通过应用名称激活窗口"""
    try:
        # 使用PowerShell激活窗口
        ps_script = f'''
Add-Type @" 
using System; 
using System.Runtime.InteropServices; 
using System.Collections.Generic; 
using System.Text; 
public class Win32 {{ 
    [DllImport("user32.dll")] 
    public static extern bool SetForegroundWindow(IntPtr hWnd); 
    [DllImport("user32.dll")] 
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow); 
    [DllImport("user32.dll")] 
    public static extern bool IsIconic(IntPtr hWnd); 
    public const int SW_RESTORE = 9; 
}} 
"@
$apps = Get-Process | Where-Object {{$_.MainWindowTitle -like "*{app_name}*"}} 
if ($apps) {{
    $hwnd = $apps[0].MainWindowHandle 
    if ($hwnd -ne 0) {{
        if ([Win32]::IsIconic($hwnd)) {{ 
            [Win32]::ShowWindow($hwnd, [Win32]::SW_RESTORE) 
        }}
        [Win32]::SetForegroundWindow($hwnd) | Out-Null
        Write-Output "Activated: $($apps[0].MainWindowTitle)"
    }} else {{
        Write-Output "No window handle found"
    }}
}} else {{
    Write-Output "Process not found"
}}
'''
        result = subprocess.run(
            ['powershell', '-Command', ps_script],
            capture_output=True,
            text=True,
            timeout=10
        )
        print(f"[DEBUG] PowerShell: {result.stdout.strip()}")
        time.sleep(1)
        return True
    except Exception as e:
        print(f"[ERROR] Activation failed: {e}")
        return False

def check_desktop_app():
    """检测桌面端应用是否存在"""
    return os.path.exists(DESKTOP_APP_PATH)

def close_popup():
    """关闭弹窗"""
    pyautogui.press('esc')
    time.sleep(0.3)

def search_and_play_desktop():
    """使用桌面端进行搜索和播放"""
    print("=== Using Desktop App (QQMusic) ===")
    
    # 1. 启动QQ音乐桌面端
    print("[Step 1] Starting QQMusic desktop app...")
    subprocess.Popen([DESKTOP_APP_PATH])
    time.sleep(8)  # 等待应用启动
    
    # 2. 尝试激活窗口
    print("[Step 2] Activating QQMusic window...")
    activate_app_by_name("QQMusic")
    screenshot('desktop_step1_app_started')
    
    # 3. 关闭可能存在的弹窗
    print("[Step 3] Closing popup...")
    close_popup()
    time.sleep(1)
    
    activate_app_by_name("QQMusic")
    screenshot('desktop_step2_popup_closed')
    
    # 4. 聚焦搜索框
    print("[Step 4] Focusing search box...")
    pyautogui.press('f')
    time.sleep(0.2)
    pyautogui.press('enter')
    time.sleep(0.5)
    
    screenshot('desktop_step3_search_focused')
    
    # 5. 输入搜索词
    print("[Step 5] Typing search keywords...")
    pyautogui.typewrite('fa ru xue', interval=0.1)
    time.sleep(0.5)
    
    screenshot('desktop_step4_typed')
    
    # 6. 按回车搜索
    print("[Step 6] Pressing Enter to search...")
    pyautogui.press('enter')
    time.sleep(5)
    
    activate_app_by_name("QQMusic")
    screenshot('desktop_step5_search_results')
    
    # 7. 点击搜索结果中的歌曲（第一首）
    print("[Step 7] Clicking first song in results...")
    pyautogui.click(x=550, y=220)
    time.sleep(1)
    
    screenshot('desktop_step6_song_clicked')
    
    # 8. 双击播放
    print("[Step 8] Double-clicking to play...")
    pyautogui.doubleClick(x=550, y=220)
    time.sleep(2)
    
    screenshot('desktop_step7_playing')
    
    # 9. 最终确认
    print("[Step 9] Final check...")
    time.sleep(3)
    
    activate_app_by_name("QQMusic")
    screenshot('desktop_step8_final')

def search_and_play_web():
    """使用网页版进行搜索和播放"""
    print("=== Using Web Version (KuGou) ===")
    
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], 
                      capture_output=True, timeout=5)
        time.sleep(1)
    except:
        pass
    
    print("[Step 1] Opening KuGou homepage...")
    subprocess.Popen([CHROME_PATH, '--new-window', 'https://www.kugou.com/'])
    time.sleep(6)
    
    activate_app_by_name("Chrome")
    close_popup()
    time.sleep(1)
    
    activate_app_by_name("Chrome")
    screenshot('web_step1_popup_closed')
    
    print("[Step 3] Clicking search box...")
    pyautogui.click(x=350, y=75)
    time.sleep(1)
    
    screenshot('web_step2_search_focused')
    
    print("[Step 4] Typing search keywords...")
    pyautogui.typewrite('fa ru xue', interval=0.1)
    time.sleep(0.5)
    
    screenshot('web_step3_typed')
    
    print("[Step 5] Pressing Enter to search...")
    pyautogui.press('enter')
    time.sleep(5)
    
    activate_app_by_name("Chrome")
    screenshot('web_step4_search_results')
    
    print("[Step 6] Clicking first song...")
    pyautogui.click(x=480, y=280)
    time.sleep(1)
    
    screenshot('web_step5_song_clicked')
    
    print("[Step 7] Double-clicking to play...")
    pyautogui.doubleClick(x=480, y=280)
    time.sleep(2)
    
    screenshot('web_step6_playing')
    
    print("[Step 8] Final check...")
    time.sleep(3)
    
    activate_app_by_name("Chrome")
    screenshot('web_step7_final')

def main():
    print("=== Smart Music Automation v5 ===")
    print(f"Checking for desktop app: {DESKTOP_APP_PATH}")
    
    if check_desktop_app():
        print("[OK] Desktop app found! Will use desktop version.")
        search_and_play_desktop()
    else:
        print("[WARN] Desktop app not found. Using web version.")
        search_and_play_web()
    
    print("=== Automation completed! ===")
    print("Check screenshots in:", SCREENSHOT_DIR)

if __name__ == "__main__":
    main()
