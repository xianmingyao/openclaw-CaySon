# -*- coding: utf-8 -*-
"""检查JINGMAI_WINDOW_KEYWORDS的值"""
import sys
sys.path.insert(0, r'E:\workspace\skills\jingmai-putaway\jingmai-cli\resources\jingmai_product_publish\scripts')

# 强制重新加载
if 'jingmai_processor' in sys.modules:
    del sys.modules['jingmai_processor']

import jingmai_processor
print("=== JINGMAI_WINDOW_KEYWORDS ===")
print(f"Type: {type(jingmai_processor.JINGMAI_WINDOW_KEYWORDS)}")
print(f"Value: {jingmai_processor.JINGMAI_WINDOW_KEYWORDS}")
print()

# 测试匹配
title = 'muying/Internal-Platform-Frontend-V2 - Google Chrome'
title_lower = title.lower()
print(f"title: {title}")
print(f"title_lower: {title_lower}")
print()

for kw in jingmai_processor.JINGMAI_WINDOW_KEYWORDS:
    result = kw.lower() in title_lower
    print(f"'{kw.lower()}' in title_lower = {result}")
