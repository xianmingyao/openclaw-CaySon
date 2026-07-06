# -*- coding: utf-8 -*-
"""测试_is_jingmai_window函数"""
import sys
sys.path.insert(0, r'E:\workspace\skills\jingmai-putaway\jingmai-cli\resources\jingmai_product_publish\scripts')

# 重新加载模块以确保使用最新代码
import importlib
if 'jingmai_processor' in sys.modules:
    del sys.modules['jingmai_processor']

from jingmai_processor import _is_jingmai_window

# 测试各种窗口标题
test_titles = [
    'jd_465d1abd3ee76',
    'muying/Internal-Platform-Frontend-V2 - Google Chrome',
    'jingmai-putaway - GSD 技术 - brainstormi',
    '京麦商品发布',
]

print("=== _is_jingmai_window 测试 ===")
for title in test_titles:
    result = _is_jingmai_window(title)
    print(f"'{title}' -> {result}")
