# -*- coding: utf-8 -*-
"""
精确查找弹窗X按钮
"""
from PIL import Image
import numpy as np

img_path = r'E:\workspace\skills\jingmai-product-publish\logs\jingmai_now.png'
img = Image.open(img_path)
img_array = np.array(img)

width, height = img.size
print(f"Image: {width}x{height}")

# "参数"弹窗应该在屏幕中央区域
# 让我扫描整个屏幕找X按钮

print("\nScanning for white X patterns...")

# 找所有可能是X按钮的白色像素
# X按钮特征：白色，在深色背景上，通常在角落
candidates = []

for y in range(0, height):
    for x in range(0, width):
        r, g, b = img_array[y, x, :3]
        # 白色像素
        if int(r) > 200 and int(g) > 200 and int(b) > 200:
            # 检查周围是否有深色背景（弹窗特征）
            neighbors_dark = 0
            for dy in [-5, -4, -3, -2, -1, 1, 2, 3, 4, 5]:
                for dx in [-5, -4, -3, -2, -1, 1, 2, 3, 4, 5]:
                    if 0 <= y+dy < height and 0 <= x+dx < width:
                        nr, ng, nb = img_array[y+dy, x+dx, :3]
                        if int(nr) < 100 and int(ng) < 100 and int(nb) < 100:
                            neighbors_dark += 1
            
            if neighbors_dark > 15:  # 周围有深色背景
                candidates.append((x, y, neighbors_dark))

print(f"Found {len(candidates)} white-on-dark pixels")

# 按周围深色像素数量排序（越多越可能是X按钮）
candidates.sort(key=lambda c: -c[2])

# 输出top 10
print("\nTop 10 X button candidates:")
for i, (x, y, score) in enumerate(candidates[:10]):
    print(f"  #{i+1}: ({x}, {y}), dark_neighbors: {score}")

# 聚类分析
if candidates:
    from collections import defaultdict
    groups = defaultdict(list)
    for x, y, score in candidates[:1000]:
        # 按50像素分组
        gx = (x // 50) * 50
        gy = (y // 50) * 50
        groups[(gx, gy)].append(score)
    
    # 找出最密集的区域
    dense = sorted(groups.items(), key=lambda g: sum(g[1]), reverse=True)[:5]
    print("\nTop 5 dense areas:")
    for (gx, gy), scores in dense:
        center_x = gx + 25
        center_y = gy + 25
        total_score = sum(scores)
        print(f"  Area ({center_x}, {center_y}): total_score={total_score}")
