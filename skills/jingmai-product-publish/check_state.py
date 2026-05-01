import sys
sys.path.insert(0, '.')
from pathlib import Path
from infrastructure.locator import JingmaiLocator
from PIL import Image

loc = JingmaiLocator()
wi = loc.find_window()
if not wi:
    raise SystemExit("京麦窗口未找到")

root = Path(__file__).resolve().parent
save_path = root / 'jingmai_current.png'
thumb_path = root / 'jingmai_thumb.png'

ss_result = loc.take_screenshot(str(save_path))
print(f"截图: {ss_result}")

img = Image.open(save_path)
w, h = img.size
print(f"截图尺寸: {w}x{h}")
if w > 0 and h > 0:
    new_w = 800
    new_h = int(h * (new_w / w))
    img.thumbnail((new_w, new_h), Image.Resampling.LANCZOS)
    img.save(thumb_path, 'PNG', quality=85)
    print(f"缩略图: {thumb_path} ({new_w}x{new_h})")
