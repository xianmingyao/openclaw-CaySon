# -*- coding: utf-8 -*-
"""
图像识别 - 查找蓝色按钮位置
"""
from PIL import Image
import numpy as np

img_path = r'E:\workspace\skills\jingmai-product-publish\logs\jingmai_now.png'

# 加载图片
img = Image.open(img_path)
img_array = np.array(img)

print(f"Image size: {img.size}")

# 蓝色按钮的HSV范围 (京麦蓝色按钮)
# 蓝色在HSV中: H=120, 但京麦按钮通常是深蓝色 H≈240
# 让我搜索深蓝色区域

# 转换为HSV更容易检测蓝色
from PIL import Image
import colorsys

width, height = img.size
print(f"Scanning {width}x{height} pixels for blue buttons...")

blue_pixels = []

# 遍历图片寻找蓝色像素 (京麦蓝色按钮通常是 RGB(0, 102, 204) 或类似)
for y in range(height):
    for x in range(width):
        r, g, b = img_array[y, x, :3]
        # 检测蓝色: B > R 且 B > G
        if int(b) > 100 and int(b) > int(r) * 1.2 and int(b) > int(g) * 1.2:
            blue_pixels.append((x, y))

print(f"Found {len(blue_pixels)} blue-ish pixels")

# 按x坐标分组（水平排列的按钮）
if blue_pixels:
    # 找到最密集的蓝色区域
    from collections import defaultdict
    
    x_groups = defaultdict(list)
    for x, y in blue_pixels:
        # 按80像素分组
        x_group = (x // 80) * 80
        x_groups[x_group].append((x, y))
    
    # 找出最大的蓝色区域
    max_group = max(x_groups.items(), key=lambda g: len(g[1]))
    group_x = max_group[0]
    pixels = max_group[1]
    
    if pixels:
        ys = [p[1] for p in pixels]
        min_y = min(ys)
        max_y = max(ys)
        center_x = group_x + 40
        center_y = (min_y + max_y) // 2
        
        print(f"\nLargest blue region:")
        print(f"  Center: ({center_x}, {center_y})")
        print(f"  Size: {len(pixels)} pixels")
        print(f"  Y range: {min_y} to {max_y}")

# 同时检查是否有"修改"文字附近的可疑区域
# "修改"通常是蓝色文字
print("\nSearching for '修改' button area...")

# 扫描左侧区域(商品类目附近)
category_area = img_array[150:300, 300:800]
print(f"Category area (y:150-300, x:300-800) scanned")

# 找出所有可能的按钮候选位置
candidates = []

# 方法1: 找蓝色按钮
for y in range(150, 350):
    for x in range(300, 1000):
        r, g, b = img_array[y, x, :3]
        if int(b) > 80 and int(b) > int(r) * 1.5:
            candidates.append((x, y, 'blue'))

# 方法2: 找白色/浅色X按钮
for y in range(50, 300):
    for x in range(1700, 2560):
        r, g, b = img_array[y, x, :3]
        if int(r) > 200 and int(g) > 200 and int(b) > 200:
            candidates.append((x, y, 'white_x'))

print(f"\nTotal candidates: {len(candidates)}")

# 按区域分组显示
if candidates:
    print("\nTop 5 clickable areas:")
    areas = {}
    for x, y, t in candidates[:1000]:
        key = (x // 50, y // 50, t)
        areas[key] = areas.get(key, 0) + 1
    
    sorted_areas = sorted(areas.items(), key=lambda a: -a[1])[:5]
    for (gx, gy, t), count in sorted_areas:
        center_x = gx * 50 + 25
        center_y = gy * 50 + 25
        print(f"  Type: {t}, Center: ({center_x}, {center_y}), Pixels: {count}")
