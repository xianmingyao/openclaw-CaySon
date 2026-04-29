import win32gui
import win32ui
import win32con
from PIL import Image
import os

hwnd = 789994

# 获取窗口DC
hwndDC = win32gui.GetWindowDC(hwnd)
mfcDC = win32ui.CreateDCFromHandle(hwndDC)
saveDC = mfcDC.CreateCompatibleDC()

# 截取窗口
saveBitMap = win32ui.CreateBitmap()
saveBitMap.CreateCompatibleBitmap(mfcDC, 2560, 1400)
saveDC.SelectObject(saveBitMap)
saveDC.BitBlt((0, 0), (2560, 1400), mfcDC, (0, 0), win32con.SRCCOPY)

# 保存
bmpinfo = saveBitMap.GetInfo()
bmpstr = saveBitMap.GetBitmapBits(True)
im = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
im.save("E:\\workspace\\scripts\\screenshots\\jingmai_window.png")

# 清理
win32gui.DeleteObject(saveBitMap.GetHandle())
saveDC.DeleteDC()
mfcDC.DeleteDC()
win32gui.ReleaseDC(hwnd, hwndDC)

print("截图已保存: E:\\workspace\\scripts\\screenshots\\jingmai_window.png")
