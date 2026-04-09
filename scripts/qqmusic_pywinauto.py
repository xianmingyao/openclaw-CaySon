#!/usr/bin/env python3
"""QQ音乐搜索 - 使用pywinauto"""
import pywinauto
import time
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 连接QQ音乐
print('Connecting to QQMusic...')
app = pywinauto.Application(backend='win32')

try:
    # 连接到已运行的QQ音乐
    app.connect(process_id=42772, timeout=10)
    print('[OK] Connected to QQMusic')
except Exception as e:
    print(f'[FAIL] Cannot connect: {e}')
    exit()

# 获取主窗口
try:
    dlg = app.window(title_re='.*50 Feet.*')
    print(f'Found window: {dlg.window_text()}')
except Exception as e:
    print(f'[FAIL] Cannot find window: {e}')
    exit()

# 激活窗口
print('\n[Step 1] activating window...')
dlg.set_focus()
dlg.maximize()
time.sleep(0.5)
dlg.minimize()
time.sleep(0.3)
dlg.restore()
time.sleep(0.5)

# 点击搜索框
print('\n[Step 2] Clicking search box...')
# 搜索框大约在窗口左上角
search_box = dlg.child_window(title="搜索音乐", class_name="Edit")
try:
    search_box.set_focus()
    print('[OK] Search box focused')
except Exception as e:
    print(f'[WARN] Cannot focus search box: {e}')
    # 尝试点击坐标
    try:
        # 在窗口范围内点击搜索框位置
        dlg.click(coords=(150, 120))
        print('[OK] Clicked at (150, 120)')
    except Exception as e2:
        print(f'[WARN] Click failed: {e2}')

time.sleep(0.5)

# 输入搜索词
print('\n[Step 3] Typing search...')
search_box.type_keys('发如雪')
time.sleep(0.3)

print('\n[Step 4] Pressing Enter...')
search_box.type_keys('{ENTER}')
time.sleep(2)

print('\n[Step 5] Clicking first result...')
try:
    # 点击搜索结果中的第一首歌
    dlg.click(coords=(180, 280))
    print('[OK] Clicked first result')
except Exception as e:
    print(f'[WARN] Click failed: {e}')

time.sleep(1)
print('\n[OK] Done!')
