# -*- coding: utf-8 -*-
import win32gui
import win32con
import win32ui
from PIL import Image
import sys

# Find Jingmai window
hwnd = win32gui.FindWindow(None, 'jd_465d1abd3ee76')
if not hwnd:
    print("Window not found!")
    sys.exit(1)

# Get window rect
rect = win32gui.GetWindowRect(hwnd)
print(f"Window rect: {rect}")

# Get client rect (what the webpage sees)
client_rect = win32gui.GetClientRect(hwnd)
print(f"Client rect: {client_rect}")

# Get window style
style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
print(f"Style: {style}")
print(f"ExStyle: {ex_style}")

# Check if maximized
if style & win32con.WS_MAXIMIZE:
    print("Window is MAXIMIZED")
if style & win32con.WS_MINIMIZE:
    print("Window is MINIMIZED")

# Get visible rect (accounting for borders)
left, top, right, bottom = rect
width = right - left
height = bottom - top
print(f"Window size: {width}x{height}")

# Get screen size
import win32api
screen_w = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
screen_h = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
print(f"Screen size: {screen_w}x{screen_h}")
