# -*- coding: utf-8 -*-
"""测试京麦窗口匹配"""
import sys
sys.path.insert(0, r'E:\workspace\skills\jingmai-putaway\jingmai-cli\resources\jingmai_product_publish\scripts')

# 强制重新加载
if 'jingmai_processor' in sys.modules:
    del sys.modules['jingmai_processor']

from jingmai_processor import _is_jingmai_window, JINGMAI_WINDOW_KEYWORDS
from pywinauto import Desktop

print("=== 关键词配置 ===")
print(f"JINGMAI_WINDOW_KEYWORDS: {JINGMAI_WINDOW_KEYWORDS}")

print("\n=== 枚举所有窗口 ===")
desktop = Desktop(backend="uia")
matched_windows = []

for w in desktop.windows():
    try:
        title = w.window_text()
        if title:
            rect = w.rectangle()
            width, height = rect.width(), rect.height()
            is_match = _is_jingmai_window(title)
            if is_match or any(kw.lower() in title.lower() for kw in ['muying', 'internal', 'jd_', 'jingmai']):
                matched_windows.append({
                    'title': title,
                    'rect': rect,
                    'width': width,
                    'height': height,
                    'is_match': is_match
                })
                print(f"\n窗口: {title}")
                print(f"  尺寸: {width}x{height}")
                print(f"  匹配: {is_match}")
    except Exception as e:
        pass

print(f"\n=== 匹配结果 ===")
print(f"共找到 {len(matched_windows)} 个相关窗口")
