import sys
sys.path.insert(0, '.')
from infrastructure.locator import JingmaiLocator

loc = JingmaiLocator()
wi = loc.find_window()
if not wi:
    raise SystemExit("京麦窗口未找到")
print("rect:", loc.window_rect)
print("hwnd:", loc.hwnd)
