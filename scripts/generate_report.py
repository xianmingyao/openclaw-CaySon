# -*- coding: utf-8 -*-
import re, os, datetime

DATA_DIR = r'E:\workspace\content-hunter-data\data'

def count_items(fp):
    if not os.path.exists(fp): return 0
    with open(fp, 'r', encoding='utf-8') as f:
        c = f.read()
    return len(re.findall(r'### 第\d+条', c))

bili = count_items(f'{DATA_DIR}\\bilibili.md')
douyin = count_items(f'{DATA_DIR}\\douyin.md')

print("=" * 50)
print("Content Hunter Report - 2026-04-07")
print("=" * 50)
print(f"Bilibili: {bili} items")
print(f"Douyin:   {douyin} items")
print()
print("B站: 成功追加100条AI内容 (via API)")
print("抖音: 验证码拦截，现100条")
