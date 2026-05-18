#!/usr/bin/env python3
import sys
sys.path.insert(0, r'E:\workspace\skills\jingmai-product-publish')
from jingmai_publish.desktop.uia_adapter import RealWindowsUIAAdapter
import time

adapter = RealWindowsUIAAdapter(screenshot_dir='resources/screenshots')
window_handle = '19271502'

# 读取页面文本
doc_text = adapter.read_document_text(window_handle)
print('=== 页面文本 (前500字) ===')
print(doc_text[:500] if doc_text else '(空)')
print()

# 检查下一步按钮
candidates = adapter.list_candidate_controls(window_handle, '下一步')
print('=== 下一步候选控件 ===')
for c in candidates[:5]:
    print(f'  text={c["text"]} class={c["class_name"]} score={c["score"]} bounds={c["bounds"]}')

# 检查商品标题输入框
print()
print('=== 商品标题候选控件 ===')
title_candidates = adapter.list_candidate_controls(window_handle, '商品标题')
for c in title_candidates[:5]:
    print(f'  text={c["text"]} class={c["class_name"]} score={c["score"]}')
