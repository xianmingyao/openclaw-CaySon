#!/usr/bin/env python3
"""QQ音乐搜索 - 使用pywinauto v2"""
import pywinauto
from pywinauto.findwindows import find_windows
import time
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 查找QQ音乐窗口
print('Finding QQMusic window...')
windows = find_windows(title_re='.*')
print(f'Found {len(windows)} windows')

# 找QQMusic
qqmusic_windows = find_windows(process='42772')
print(f'QQMusic windows: {len(qqmusic_windows)}')

if not qqmusic_windows:
    print('[FAIL] QQMusic window not found')
    exit()

hwnd = qqmusic_windows[0]
print(f'Window handle: {hwnd}')

# 连接应用
app = pywinauto.Application(backend='win32')
app.connect(handle=hwnd)
print('[OK] Connected')

# 获取窗口
dlg = app.window(handle=hwnd)
print(f'Window: {dlg.window_text()}')

# 激活
print('\n[Step 1] Activating window...')
dlg.set_focus()
time.sleep(0.5)

# 尝试找到搜索框
print('\n[Step 2] Finding search box...')
try:
    # 列出所有子窗口
    children = dlg.children()
    print(f'Found {len(children)} children')
    for i, child in enumerate(children[:10]):
        try:
            print(f'  {i}: {child.window_text()[:30]} | class={child.class_name()}')
        except:
            print(f'  {i}: <error getting info>')
except Exception as e:
    print(f'Error: {e}')

# 尝试使用键盘
print('\n[Step 3] Sending search...')
dlg.type_keys('^f')  # Ctrl+F
time.sleep(0.5)
dlg.type_keys('发如雪')
time.sleep(0.3)
dlg.type_keys('{ENTER}')
time.sleep(2)

print('\n[OK] Done')
