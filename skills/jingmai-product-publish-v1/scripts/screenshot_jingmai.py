# -*- coding: utf-8 -*-
"""京麦窗口截图工具"""
import win32gui
import win32ui
import win32con
from PIL import Image
import ctypes

def screenshot_window(hwnd, save_path):
    """截图指定窗口"""
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    w, h = right - left, bottom - top
    
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(mfcDC, w, h)
    saveDC.SelectObject(bmp)
    saveDC.BitBlt((0, 0), (w, h), mfcDC, (0, 0), win32con.SRCCOPY)
    
    # 获取BITMAPINFO
    class BITMAPINFOHEADER(ctypes.Structure):
        _fields_ = [
            ('biSize', ctypes.c_uint32),
            ('biWidth', ctypes.c_int),
            ('biHeight', ctypes.c_int),
            ('biPlanes', ctypes.c_short),
            ('biBitCount', ctypes.c_short),
            ('biCompression', ctypes.c_uint32),
            ('biSizeImage', ctypes.c_uint32),
            ('biXPelsPerMeter', ctypes.c_long),
            ('biYPelsPerMeter', ctypes.c_long),
            ('biClrUsed', ctypes.c_uint32),
            ('biClrImportant', ctypes.c_uint32),
        ]
    
    bmi = BITMAPINFOHEADER()
    bmi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.biWidth = w
    bmi.biHeight = -h  # 负值表示自上而下
    bmi.biPlanes = 1
    bmi.biBitCount = 32
    bmi.biCompression = 0  # BI_RGB
    
    buf_len = w * h * 4
    buf = ctypes.create_string_buffer(buf_len)
    
    # 使用GetDIBits获取位图数据
    GetDIBits = ctypes.windll.gdi32.GetDIBits
    GetDIBits.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint]
    GetDIBits.restype = ctypes.c_int
    
    result = GetDIBits(saveDC.GetHandleOutput(), bmp.GetHandle(), 0, h, buf, ctypes.byref(bmi), 0)
    
    if result:
        img = Image.frombuffer('RGBA', (w, h), buf, 'raw', 'BGRA', 0, 1)
        img = img.convert('RGB')
        img.save(save_path)
    
    win32gui.DeleteObject(bmp.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)
    return w, h

if __name__ == "__main__":
    # 找到京麦窗口
    jingmai_hwnd = None
    def enum_handler(hwnd, ctx):
        global jingmai_hwnd
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title and 'jd_' in title.lower():
                jingmai_hwnd = hwnd
    win32gui.EnumWindows(enum_handler, None)
    
    if jingmai_hwnd:
        print(f"找到京麦窗口: {jingmai_hwnd}")
        w, h = screenshot_window(jingmai_hwnd, r"E:\workspace\skills\jingmai-product-publish\logs\jingmai_current.png")
        print(f"截图保存: {w}x{h}")
    else:
        print("未找到京麦窗口")
