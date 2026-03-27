import win32gui
import win32con
import win32api
import time
import subprocess

# 先用 windows-control 激活 Chrome
print("Activating Chrome with windows-control...")
subprocess.run(['python', 'E:\\workspace\\skills\\windows-control\\windows_control.py', 'open-app', '--app-name', 'chrome'], capture_output=True)
time.sleep(0.5)

# 枚举所有窗口
def find_youdao_windows():
    windows = []
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            classname = win32gui.GetClassName(hwnd)
            if 'note.youdao' in title.lower() or '技术知识库' in title:
                rect = win32gui.GetWindowRect(hwnd)
                windows.append({
                    'hwnd': hwnd,
                    'title': title,
                    'rect': rect,
                    'class': classname
                })
    win32gui.EnumWindows(callback, windows)
    return windows

# 查找窗口
print("\nSearching for Youdao Note windows...")
youdao_wins = find_youdao_windows()
print(f"Found {len(youdao_wins)} windows:")

for w in youdao_wins:
    print(f"  HWND: {w['hwnd']}")
    print(f"  Title: {w['title']}")
    print(f"  Class: {w['class']}")
    print(f"  Rect: {w['rect']}")
    
    # 激活窗口
    try:
        win32gui.ShowWindow(w['hwnd'], win32con.SW_RESTORE)
        time.sleep(0.3)
        win32gui.SetForegroundWindow(w['hwnd'])
        time.sleep(0.5)
        
        # 获取焦点
        rect = w['rect']
        # 点击窗口中间位置
        center_x = (rect[0] + rect[2]) // 2
        center_y = (rect[1] + rect[3]) // 2
        print(f"  Clicking center: {center_x}, {center_y}")
        
        import pyautogui
        pyautogui.click(center_x, center_y)
        time.sleep(1)
        
        print("  -> Done!")
    except Exception as e:
        print(f"  -> Error: {e}")

# 截图确认
import pyautogui
screenshot = pyautogui.screenshot()
screenshot.save('E:\\workspace\\youdao_final.png')
print("\nScreenshot saved to youdao_final.png")
