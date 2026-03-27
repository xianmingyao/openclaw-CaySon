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

# 尝试多次点击在不同位置
positions = [
    (960, 600),  # 中间偏下
    (960, 550),  # 中间
    (960, 650),  # 更下面
    (1000, 600), # 偏右
    (920, 600),  # 偏左
]

for i, (x, y) in enumerate(positions):
    print(f'Attempt {i+1}: Clicking at ({x}, {y})...')
    dlg.click_input(coords=(x, y))
    time.sleep(0.5)
    
    # 截图
    screenshot = pyautogui.screenshot()
    screenshot.save(f'E:\\workspace\\click_attempt_{i+1}.png')
    
    # 检查是否创建了笔记（通过检查是否出现了编辑器）
    # 如果不是空文件夹状态，说明成功了

# 最终截图
screenshot = pyautogui.screenshot()
screenshot.save('E:\\workspace\\final_attempt.png')
print('Final screenshot saved')
