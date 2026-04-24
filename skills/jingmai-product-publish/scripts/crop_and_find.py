# -*- coding: utf-8 -*-
"""
裁剪并分析弹窗X按钮
"""
from PIL import Image

img_path = r'E:\workspace\skills\jingmai-product-publish\logs\jingmai_now.png'

# 打开原图
img = Image.open(img_path)
width, height = img.size
print(f"Original: {width}x{height}")

# 手机预览弹窗在屏幕中央位置
# 基于之前的分析，弹窗中心大约在 (1280, 700)
# 弹窗大小大约是 400x700
# X按钮应该在弹窗右上角

# 裁剪弹窗区域 (左边, 上边, 右边, 下边)
popup_left = 900
popup_top = 400
popup_right = 1700
popup_bottom = 1100

crop = img.crop((popup_left, popup_top, popup_right, popup_bottom))
crop_path = r'E:\workspace\skills\jingmai-product-publish\logs\popup_crop.png'
crop.save(crop_path)
print(f"Saved crop: {popup_right-popup_left}x{popup_bottom-popup_top} to {crop_path}")

# 分析裁剪区域找X按钮
import numpy as np
crop_array = np.array(crop)

print("\nAnalyzing crop area for X button...")

# X按钮特征：白色像素，右上角
# 从右上角开始扫描
candidates = []
crop_width, crop_height = crop.size

for y in range(crop_height):
    for x in range(crop_width):
        r, g, b = crop_array[y, x, :3]
        # 白色像素
        if int(r) > 200 and int(g) > 200 and int(b) > 200:
            # 检查是否是右上角区域 (右边30%, 上边30%)
            if x > crop_width * 0.7 and y < crop_height * 0.3:
                candidates.append((x, y))

print(f"Found {len(candidates)} white pixels in top-right area")

if candidates:
    xs = [c[0] for c in candidates]
    ys = [c[1] for c in candidates]
    avg_x = sum(xs) // len(xs)
    avg_y = sum(ys) // len(ys)
    
    # 转回原图坐标
    orig_x = avg_x + popup_left
    orig_y = avg_y + popup_top
    
    print(f"\nX button approximate center in crop: ({avg_x}, {avg_y})")
    print(f"X button in original image: ({orig_x}, {orig_y})")
    
    # 保存结果
    with open(r'E:\workspace\skills\jingmai-product-publish\logs\x_in_crop.txt', 'w') as f:
        f.write(f"Crop area: {popup_left},{popup_top} to {popup_right},{popup_bottom}\n")
        f.write(f"Crop size: {crop_width}x{crop_height}\n")
        f.write(f"X button in crop: ({avg_x}, {avg_y})\n")
        f.write(f"X button original: ({orig_x}, {orig_y})\n")
        f.write(f"White pixels found: {len(candidates)}\n")
else:
    print("No white pixels found in top-right of crop")
    # 扩大搜索范围
    print("\nSearching entire crop for white pixels...")
    for y in range(crop_height):
        for x in range(crop_width):
            r, g, b = crop_array[y, x, :3]
            if int(r) > 200 and int(g) > 200 and int(b) > 200:
                candidates.append((x, y))
    
    if candidates:
        # 找最右上角的白色像素
        candidates.sort(key=lambda c: (-c[0], c[1]))  # 按x降序，y升序
        best = candidates[0]
        orig_x = best[0] + popup_left
        orig_y = best[1] + popup_top
        print(f"Most top-right white pixel in crop: {best}")
        print(f"Original coords: ({orig_x}, {orig_y})")
