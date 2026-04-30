# -*- coding: utf-8 -*-
"""测试窗口枚举"""
import win32gui
import win32con

def enum_handler(hwnd, results):
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd)
        if title:
            print(f'  Found: "{title}" (hwnd={hwnd})')
            exclude_list = ['Claude', 'claude', 'codex', 'Codex', 'session', 'openclaw']
            for ex in exclude_list:
                if ex.lower() in title.lower():
                    print(f'    -> EXCLUDED (matched "{ex}")')
                    return
            include_list = ['muying', 'Internal-Platform-Frontend', '京麦', '京东商家', 
                          'wares-jdm', 'wares.jd', 'JMWorkStation', 'jd_465d1abd3ee76', 'jingmai']
            for kw in include_list:
                if kw.lower() in title.lower():
                    print(f'    -> INCLUDED (matched "{kw}")')
                    results.append((hwnd, title))
                    return
            print(f'    -> no match')

results = []
win32gui.EnumWindows(enum_handler, results)
print()
print('Matched windows:')
for hwnd, title in results:
    print(f'  {title} (hwnd={hwnd})')
