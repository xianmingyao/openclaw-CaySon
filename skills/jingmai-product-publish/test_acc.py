from pywinauto import Application
from pywinauto.mouse import click
import time

print('Testing title field click using different methods...')

# Method 1: Use pywinauto's built-in click on coords
app = Application(backend='win32').connect(title='jd_465d1abd3ee76')
dlg = app.window(title='jd_465d1abd3ee76')

# Get the WebView window
webview = dlg.child_window(class_name='Chrome_RenderWidgetHostHWND')
print(f'WebView handle: {webview.handle}')

# Try clicking at various positions within the WebView
# These are relative to the WebView window
test_positions = [
    (900, 350, 'title field estimate 1'),
    (1000, 350, 'title field estimate 2'),
    (1100, 350, 'title field estimate 3'),
    (1200, 350, 'title field estimate 4'),
]

for x, y, desc in test_positions:
    print(f'Testing: {desc} at ({x}, {y})')
    try:
        # Click using pywinauto's click method on the dialog
        click(coords=(x, y))
        time.sleep(0.5)
        print(f'  Clicked at ({x}, {y})')
    except Exception as e:
        print(f'  Error: {e}')

print()
print('Now let us try typing to see if any field received focus...')
