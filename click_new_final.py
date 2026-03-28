from pywinauto import Application
import time
import pyautogui
import win32gui
import win32con

Hwnd = 5639224

print('Step 1: 激活窗口...')
if win32gui.IsIconic(Hwnd):
    win32gui.ShowWindow(Hwnd, win32con.SW_RESTORE)
time.sleep(0.3)
win32gui.SetForegroundWindow(Hwnd)
time.sleep(0.5)
win32gui.BringWindowToTop(Hwnd)
time.sleep(0.3)
print('  窗口已激活')

print('Step 2: 截图确认...')
screenshot = pyautogui.screenshot()
screenshot.save('E:\\workspace\\final_step1.png')
print('  截图已保存')

print('Step 3: 点击新建笔记按钮...')
# 使用 pywinauto 的 click_input
app = Application(backend='win32')
app.connect(handle=Hwnd)
dlg = app.window(handle=Hwnd)
dlg.set_focus()
time.sleep(0.3)

# 点击页面中间位置 (960, 540)
print('  使用 dlg.click_input(coords=(960, 540))')
dlg.click_input(coords=(960, 540))
time.sleep(2)

screenshot = pyautogui.screenshot()
screenshot.save('E:\\workspace\\final_step2.png')
print('  截图已保存')

print('Step 4: 再次点击...')
dlg.click_input(coords=(960, 540))
time.sleep(2)

screenshot = pyautogui.screenshot()
screenshot.save('E:\\workspace\\final_step3.png')
print('  截图已保存')

print('Done!')
