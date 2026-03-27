from pywinauto import Application, Desktop
import time
import pyautogui

# 连接到有道云笔记窗口
print('Connecting to Youdao Note window...')
app = Application(backend='win32')
app.connect(handle=5639224)
dlg = app.window(handle=5639224)
dlg.set_focus()
time.sleep(0.3)

print('Window focused')

# 尝试各种键盘快捷键
shortcuts = [
    ('ctrl+n', 'Ctrl+N'),
    ('ctrl+shift+n', 'Ctrl+Shift+N'),
    ('alt+n', 'Alt+N'),
    ('f4', 'F4'),
]

for keys, name in shortcuts:
    print(f'Trying {name}...')
    keys_list = keys.split('+')
    pyautogui.hotkey(*keys_list)
    time.sleep(1)
    
    # 截图
    screenshot = pyautogui.screenshot()
    screenshot.save(f'E:\\workspace\\key_{name.replace("+", "_").replace(" ", "_")}.png')

# 最终截图
screenshot = pyautogui.screenshot()
screenshot.save('E:\\workspace\\final_keyboard.png')
print('Done')
