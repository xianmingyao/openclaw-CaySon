# -*- coding: utf-8 -*-
"""
智能图像识别 - 查找修改按钮和X关闭按钮
"""
from PIL import Image
import numpy as np

img_path = r'E:\workspace\skills\jingmai-product-publish\logs\jingmai_now.png'
img = Image.open(img_path)
img_array = np.array(img)

width, height = img.size
print(f"Image: {width}x{height}")

# 方法1: 找"修改"文字（蓝色小文字）
# 修改通常是深蓝色文字
print("\n1. Searching for '修改' blue text...")
modify_candidates = []

# 扫描商品类目附近区域 (y: 150-300, x: 500-1100)
for y in range(150, 300):
    for x in range(500, 1100):
        r, g, b = img_array[y, x, :3]
        # 蓝色文字特征: B值高，R和G低
        if int(b) > 150 and int(r) < 100 and int(g) < 150:
            modify_candidates.append((x, y))

if modify_candidates:
    xs = [p[0] for p in modify_candidates]
    ys = [p[1] for p in modify_candidates]
    print(f"   Found {len(modify_candidates)} blue text pixels")
    print(f"   X range: {min(xs)}-{max(xs)}, Y range: {min(ys)}-{max(ys)}")
    modify_center = (sum(xs)//len(xs), sum(ys)//len(ys))
    print(f"   Approximate center: {modify_center}")

# 方法2: 找弹窗的X关闭按钮（白色X在深灰背景上）
print("\n2. Searching for X close button...")
x_candidates = []

# 扫描右上角区域 (y: 50-300, x: 1700-2560)
for y in range(50, 300):
    for x in range(1700, 2560):
        r, g, b = img_array[y, x, :3]
        # 白色X特征: RGB都高，在深色背景上
        if int(r) > 200 and int(g) > 200 and int(b) > 200:
            x_candidates.append((x, y))

if x_candidates:
    xs = [p[0] for p in x_candidates]
    ys = [p[1] for p in x_candidates]
    print(f"   Found {len(x_candidates)} white pixels")
    print(f"   X range: {min(xs)}-{max(xs)}, Y range: {min(ys)}-{max(ys)}")
    x_center = (sum(xs)//len(xs), sum(ys)//len(ys))
    print(f"   Approximate center: {x_center}")

# 方法3: 找所有蓝色按钮
print("\n3. Searching for all blue buttons...")
all_blue = []

for y in range(height):
    for x in range(width):
        r, g, b = img_array[y, x, :3]
        if int(b) > 100 and int(b) > int(r) * 1.5 and int(b) > int(g) * 1.2:
            all_blue.append((x, y))

# 聚类分析
if all_blue:
    # 按Y坐标分组（同一行的按钮）
    from collections import defaultdict
    y_groups = defaultdict(list)
    for x, y in all_blue:
        y_group = (y // 30) * 30
        y_groups[y_group].append(x)
    
    # 找出最密集的行
    dense_rows = sorted(y_groups.items(), key=lambda g: len(g[1]), reverse=True)[:5]
    print("   Top 5 dense rows:")
    for y_base, xs in dense_rows:
        if len(xs) > 50:
            center_y = y_base + 15
            center_x = (min(xs) + max(xs)) // 2
            print(f"   Row y={center_y}, X range: {min(xs)}-{max(xs)}, Count: {len(xs)}")

# 输出建议的点击坐标
print("\n" + "="*50)
print("Recommended click positions:")
print("="*50)

if modify_candidates:
    print(f"'修改' button (approx): {modify_center}")

if x_candidates:
    print(f"X close button (approx): {x_center}")

# 保存分析结果
with open(r'E:\workspace\skills\jingmai-product-publish\logs\button_analysis.txt', 'w') as f:
    f.write(f"Image: {width}x{height}\n")
    if modify_candidates:
        f.write(f"'修改' center: {modify_center}\n")
    if x_candidates:
        f.write(f"X button center: {x_center}\n")
print("\nAnalysis saved to button_analysis.txt")
