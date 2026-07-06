from pywinauto import Application
import time

print('Connecting to Jingmai window...')

# Connect to Jingmai by its window title
app = Application(backend='win32').connect(title='jd_465d1abd3ee76')
print('Connected to:', app)

# Get the main window
dlg = app.window(title='jd_465d1abd3ee76')
print('Main dialog:', dlg)

# Try to get all children
print()
print('Enumerating all children (first 30):')
children = dlg.children()
for i, child in enumerate(children[:30]):
    try:
        cls = child.class_name()
        txt = child.window_text()
        rect = child.rectangle()
        print(f'  {i}: [{cls}] "{txt}" rect={rect}')
    except Exception as e:
        print(f'  {i}: Error: {e}')
