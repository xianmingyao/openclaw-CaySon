#!/usr/bin/env python3
import re
from datetime import datetime

DATA = r"E:\workspace\content-hunter-data\data"

# B站统计
with open(f"{DATA}\\bilibili.md", encoding='utf-8') as f:
    bc = f.read()
b_old = re.findall(r'^### 第(\d+)条', bc, re.MULTILINE)
b_new = re.findall(r'^## 第(\d+)条', bc, re.MULTILINE)
b_bv = re.findall(r'(BV\w{10})', bc)
print(f"B站总览:")
print(f"  旧格式(###)条目: {len(b_old)} (最大编号{b_old and max(map(int,b_old))})")
print(f"  新格式(##)条目: {len(b_new)} (最大编号{b_new and max(map(int,b_new))})")
print(f"  唯一BV号: {len(set(b_bv))}")

# 抖音统计
with open(f"{DATA}\\douyin.md", encoding='utf-8') as f:
    dc = f.read()
d_old = re.findall(r'^### 第(\d+)条', dc, re.MULTILINE)
d_new = re.findall(r'^## 第(\d+)条', dc, re.MULTILINE)
d_urls = re.findall(r'https://www\.douyin\.com/video/(\d+)', dc)
print(f"\n抖音总览:")
print(f"  旧格式(###)条目: {len(d_old)} (最大编号{d_old and max(map(int,d_old))})")
print(f"  新格式(##)条目: {len(d_new)} (最大编号{d_new and max(map(int,d_new))})")
print(f"  唯一视频URL: {len(set(d_urls))}")

print(f"\n统计时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
