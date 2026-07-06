from pywinauto import Desktop
import time

desktop = Desktop(backend='uia')
jingmai = None
for w in desktop.windows():
    try:
        title = w.window_text()
        if title and 'jd_' in title.lower():
            jingmai = w
            break
    except Exception:
        pass

if jingmai:
    print(f'找到窗口: {jingmai.window_text()}')
    
    # 只打印直接子元素
    for elem in jingmai.children():
        try:
            text = elem.window_text()
            ctype = elem.control_type()
            rect = elem.rectangle()
            if text and len(text) > 1:
                print(f'{ctype}: "{text}" @ ({rect.left},{rect.top},{rect.right},{rect.bottom})')
        except Exception as e:
            print(f'Error: {e}')
else:
    print('未找到京麦窗口')
