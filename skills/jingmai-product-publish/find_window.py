import sys
sys.path.insert(0, '.')
from infrastructure.locator import JingmaiLocator

loc = JingmaiLocator()
wi = loc.find_window()
print("找到:", wi)
print("hwnd:", loc.hwnd if hasattr(loc, 'hwnd') else 'N/A')
