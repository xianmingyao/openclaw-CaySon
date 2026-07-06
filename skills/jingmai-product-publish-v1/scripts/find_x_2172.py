# -*- coding: utf-8 -*-
"""
在指定区域查找X按钮
"""
from PIL import Image
import numpy as np

img_path = r'E:\workspace\skills\jingmai-product-publish\logs\jingmai_now.png'
img = Image.open(img_path)
img_array = np.array(img)

width, height = img.size
print(f"Image: {width}x{height}")

# 宁兄提示X按钮在 2172, 140 左右
# 扫描这个区域附近找白色X图案
target_x, target_y = 2172, 140

# 扫描区域：x: 2100-2300, y: 100-250
print(f"\nScanning area around ({target_x}, {target_y})...")

candidates = []
scan_radius = 100

for y in range(max(0, target_y - scan_radius), min(height, target_y + scan_radius)):
    for x in range(max(0, target_x - scan_radius), min(width, target_x + scan_radius)):
        r, g, b = img_array[y, x, :3]
        # 白色像素
        if int(r) > 200 and int(g) > 200 and int(b) > 200:
            # 检查周围是否有深色背景
            dark_count = 0
            for dy in [-5, -4, -3, -2, -1, 1, 2, 3, 4, 5]:
                for dx in [-5, -4, -3, -2, -1, 1, 2, 3, 4, 5]:
                    if 0 <= y+dy < height and 0 <= x+dx < width:
                        nr, ng, nb = img_array[y+dy, x+dx, :3]
                        if int(nr) < 100 and int(ng) < 100 and int(nb) < 100:
                            dark_count += 1
            if dark_count >= 8:
                candidates.append((x, y, dark_count))

print(f"Found {len(candidates)} white-on-dark pixels")

if candidates:
    # 聚类分析
    from collections import defaultdict
    grid = defaultdict(list)
    for x, y, score in candidates:
        gx = (x // 20) * 20
        gy = (y // 20) * 20
        grid[(gx, gy)].append(score)
    
    dense = sorted(grid.items(), key=lambda g: sum(g[1]), reverse=True)[:10]
    print("\nTop dense areas:")
    for (gx, gy), scores in dense:
        cx = gx + 10
        cy = gy + 10
        print(f"  ({cx}, {cy}): score={sum(scores)}, count={len(scores)}")

# 同时分析整个屏幕找最像X按钮的地方
print("\n\nScanning entire screen for X pattern...")
all_x = []

for y in range(height):
    for x in range(width):
        r, g, b = img_array[y, x, :3]
        # 找白色像素
        if int(r) > 220 and int(g) > 220 and int(b) > 220:
            # 检查是否是X形状（周围有对应的斜向像素）
            all_x.append((x, y))

if all_x:
    xs = [p[0] for p in all_x]
    ys = [p[1] for p in all_x]
    print(f"Total white pixels: {len(all_x)}")
    print(f"X range: {min(xs)}-{max(xs)}")
    print(f"Y range: {min(ys)}-{max(ys)}")
