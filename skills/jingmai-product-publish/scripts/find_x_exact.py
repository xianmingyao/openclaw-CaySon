# -*- coding: utf-8 -*-
"""
精确查找弹窗X按钮 - 扫描整个屏幕
"""
from PIL import Image
import numpy as np

img_path = r'E:\workspace\skills\jingmai-product-publish\logs\jingmai_now.png'
img = Image.open(img_path)
img_array = np.array(img)

width, height = img.size
print(f"Image: {width}x{height}")

# 扫描整个屏幕找X按钮
# X按钮特征：白色像素，在深色背景上
print("\nScanning entire screen for X button...")

candidates = []

for y in range(height):
    for x in range(width):
        r, g, b = img_array[y, x, :3]
        # 白色像素
        if int(r) > 200 and int(g) > 200 and int(b) > 200:
            # 检查周围是否有深色背景
            dark_count = 0
            for dy in [-3, -2, -1, 1, 2, 3]:
                for dx in [-3, -2, -1, 1, 2, 3]:
                    if 0 <= y+dy < height and 0 <= x+dx < width:
                        nr, ng, nb = img_array[y+dy, x+dx, :3]
                        if int(nr) < 80 and int(ng) < 80 and int(nb) < 80:
                            dark_count += 1
            
            if dark_count >= 10:
                candidates.append((x, y, dark_count))

print(f"Found {len(candidates)} white-on-dark pixels")

# 按周围深色像素数量排序
candidates.sort(key=lambda c: -c[2])

# 输出top 20
print("\nTop 20 X button candidates:")
for i, (x, y, score) in enumerate(candidates[:20]):
    print(f"  #{i+1}: ({x}, {y}), dark: {score}")

# 聚类 - 按50像素网格
from collections import defaultdict
grid = defaultdict(list)
for x, y, score in candidates[:2000]:
    gx = (x // 50) * 50
    gy = (y // 50) * 50
    grid[(gx, gy)].append(score)

# 找最密集的区域
dense = sorted(grid.items(), key=lambda g: sum(g[1]), reverse=True)[:10]
print("\nTop 10 dense areas (50x50 grid):")
for (gx, gy), scores in dense:
    cx = gx + 25
    cy = gy + 25
    print(f"  ({cx}, {cy}): total_score={sum(scores)}, count={len(scores)}")

# 保存结果
with open(r'E:\workspace\skills\jingmai-product-publish\logs\x_candidates.txt', 'w') as f:
    f.write(f"Total candidates: {len(candidates)}\n\n")
    f.write("Top 20:\n")
    for i, (x, y, score) in enumerate(candidates[:20]):
        f.write(f"  #{i+1}: ({x}, {y}), dark: {score}\n")
    f.write("\nTop 10 dense areas:\n")
    for (gx, gy), scores in dense:
        cx = gx + 25
        cy = gy + 25
        f.write(f"  ({cx}, {cy}): total_score={sum(scores)}, count={len(scores)}\n")

print("\nResults saved to x_candidates.txt")
