"""
智能音乐自动化脚本 final - 修复搜索框焦点问题
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

def activate_qqmusic():
    """激活QQ音乐窗口"""
    try:
        ps_script = '''
Add-Type @" 
using System; 
using System.Runtime.InteropCommunications; 
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
$proc = Get-Process -Name "QQMusic" -ErrorAction SilentlyContinue
if ($proc -and $proc.MainWindowHandle -ne 0) {{
    $hwnd = $proc.MainWindowHandle 
    if ([Win32]::IsIconic($hwnd)) {{ [Win32]::ShowWindow($hwnd, [Win32]::SW_RESTORE) }}
    [Win32]::SetForegroundWindow($hwnd) | Out-Null
    Write-Output "SUCCESS"
}} else {{ Write-Output "FAILED" }}
'''
        result = subprocess.run(['powershell', '-Command', ps_script], 
                              capture_output=True, text=True, timeout=10)
        print(f"[DEBUG] Activation: {result.stdout.strip()}")
        time.sleep(1)
        return "SUCCESS" in result.stdout
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def check_desktop_app():
    """检测桌面端应用是否存在"""
    return os.path.exists(DESKTOP_APP_PATH)

def search_and_play_desktop():
    """使用桌面端进行搜索和播放"""
    print("=== Using Desktop App (QQMusic) FINAL ===")
    
    # 1. 启动QQ音乐桌面端
    print("[Step 1] Starting QQMusic desktop app...")
    subprocess.Popen([DESKTOP_APP_PATH])
    time.sleep(6)  # 等待应用启动
    
    # 2. 激活窗口
    print("[Step 2] Activating QQMusic window...")
    activate_qqmusic()
    screenshot('desktop_step1_app_started')
    
    # 3. 关闭可能存在的弹窗
    print("[Step 3] Closing popup...")
    pyautogui.press('esc')
    time.sleep(0.5)
    
    activate_qqmusic()
    screenshot('desktop_step2_popup_closed')
    
    # 4. 点击搜索框 - QQ音乐搜索框在顶部中央
    print("[Step 4] Clicking search box...")
    # 根据QQ音乐界面，搜索框在顶部居中位置
    # 尝试多个可能的位置
    pyautogui.click(x=420, y=45)  # 搜索框位置
    time.sleep(1)
    
    screenshot('desktop_step3_clicked_search')
    
    # 5. 确认搜索框获得焦点
    print("[Step 5] Verifying search box focus...")
    time.sleep(0.5)
    
    screenshot('desktop_step4_focused')
    
    # 6. 输入搜索词 - 使用paste避免输入法问题
    print("[Step 6] Typing search keywords...")
    pyautogui.typewrite('faruxue', interval=0.08)  # 不用空格
    time.sleep(0.5)
    
    screenshot('desktop_step5_typed')
    
    # 7. 按回车搜索
    print("[Step 7] Pressing Enter to search...")
    pyautogui.press('enter')
    time.sleep(5)
    
    activate_qqmusic()
    screenshot('desktop_step6_search_results')
    
    # 8. 点击搜索结果中的歌曲（第一首）
    print("[Step 8] Clicking first song in results...")
    pyautogui.click(x=550, y=220)
    time.sleep(1)
    
    screenshot('desktop_step7_song_clicked')
    
    # 9. 双击播放
    print("[Step 9] Double-clicking to play...")
    pyautogui.doubleClick(x=550, y=220)
    time.sleep(2)
    
    screenshot('desktop_step8_playing')
    
    # 10. 最终确认
    print("[Step 10] Final check...")
    time.sleep(3)
    
    activate_qqmusic()
    screenshot('desktop_step9_final')

def main():
    print("=== Smart Music Automation FINAL ===")
    print(f"Checking for desktop app: {DESKTOP_APP_PATH}")
    
    if check_desktop_app():
        print("[OK] Desktop app found!")
        search_and_play_desktop()
    else:
        print("[WARN] Desktop app not found.")
    
    print("=== Done! ===")
    print("Screenshots:", SCREENSHOT_DIR)

if __name__ == "__main__":
    main()
