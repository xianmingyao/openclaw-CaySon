import win32gui

result = []
def enum_handler(hwnd, result):
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd)
        if title and ('jingmai' in title.lower() or 'jd_' in title.lower() or 'ware' in title.lower()):
            result.append((hwnd, title))

win32gui.EnumWindows(lambda h, r=result: enum_handler(h, r) or True, result)

if result:
    for hwnd, title in result:
        rect = win32gui.GetWindowRect(hwnd)
        print(f'HWND={hwnd}: "{title}" at {rect}')
else:
    print('No Jingmai windows found')
