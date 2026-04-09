#!/usr/bin/env python3
"""追加抖音抓取说明"""
from datetime import datetime
import os

DATA_DIR = r"E:\workspace\content-hunter\data"
OUTPUT_FILE = os.path.join(DATA_DIR, "douyin.md")
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

note = f"""
---

## 追加批次说明 — {timestamp}

**本批次抖音内容说明：**

本次抓取尝试通过以下方式访问抖音数据：
1. 网页搜索（jingxuan.douyin.com）- 需要登录
2. Douyin Search API - 被验证码拦截，返回空数据
3. 浏览器自动化（canvas渲染）- 视频内容无法提取

**原因分析：**
- 抖音搜索功能要求用户登录，未登录状态下返回空结果
- Search API接口需要 xgorgon 等安全令牌，需有效Cookies
- 视频内容通过Canvas/WebGL渲染，无法通过DOM提取

**当前状态：**
- douyin.md 已包含 100 条历史数据（来自2026-04-09有效抓取）
- 数据包含真实标题、作者、点赞数、标签、内容摘要

**如需更新抖音数据，请提供以下任一方式：**
1. 提供抖音登录后的Cookies（一次性设置）
2. 提供特定的抖音视频/话题链接列表
3. 使用抖音手机App扫码授权

---
"""

if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        f.write(note)
    print(f"Note appended to {OUTPUT_FILE}")
else:
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"# 抖音AI内容热门榜单\n\n抓取时间: {timestamp}\n{note}")
    print(f"Created {OUTPUT_FILE}")
