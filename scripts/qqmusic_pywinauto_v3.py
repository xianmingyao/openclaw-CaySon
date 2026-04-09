#!/usr/bin/env python3
"""QQ音乐搜索 - pywinauto v3"""
import pywinauto
from pywinauto.findwindows import find_windows
import time
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 尝试用窗口标题查找
print('Finding by title...')
windows = find_windows(title_re='.*50 Feet.*')
print(f'Found windows with 50 Feet: {len(windows)}')

if windows:
    hwnd = windows[0]
else:
    # 尝试用QQMusic标题
    windows = find_windows(title_re='.*QQMusic.*')
    print(f'Found QQMusic windows: {len(windows)}')
    if windows:
        hwnd = windows[0]
    else:
        # 尝试所有可见窗口
        all_windows = find_windows(visible_only=True)
        print(f'Visible windows: {len(all_windows)}')
        for w in all_windows[:20]:
            try:
                from pywinauto.controls.hwndwrapper import HwndWrapper
                app_temp = pywinauto.Application(backend='win32')
                app_temp.connect(handle=w)
                dlg_temp = app_temp.window(handle=w)
                title = dlg_temp.window_text()
                if title and ('QQ' in title or 'Music' in title or 'music' in title.lower()):
                    print(f'Found relevant: {title}')
                    hwnd = w
                    break
            except:
                pass
        else:
            print('[FAIL] Cannot find QQMusic')
            exit()

print(f'Using window handle: {hwnd}')

# 连接
app = pywinauto.Application(backend='win32')
app.connect(handle=hwnd)
dlg = app.window(handle=hwnd)
print(f'Window: {dlg.window_text()}')

# 激活
print('\n[Step 1] Activating...')
dlg.set_focus()
time.sleep(0.5)

# 发送 Ctrl+F
print('\n[Step 2] Sending Ctrl+F...')
dlg.type_keys('^f')
time.sleep(0.5)

# 输入搜索
print('\n[Step 3] Typing search...')
dlg.type_keys('发如雪')
time.sleep(0.3)

print('\n[Step 4] Pressing Enter...')
dlg.type_keys('{ENTER}')
time.sleep(2)

print('\n[OK] Done')
