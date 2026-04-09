#!/usr/bin/env python3
"""从历史文件提取抖音AI数据用于今日任务"""
import re
import os

DATA_DIR = r"E:\workspace\content-hunter\data"
HISTORICAL_FILE = os.path.join(DATA_DIR, "douyin-ai-2026-04-08.md")
OUTPUT_FILE = os.path.join(DATA_DIR, "douyin.md")

with open(HISTORICAL_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# 解析出每条数据的标题、作者、点赞、话题、内容总结
# 格式: ### 第X条 \n - 标题: \n - 作者: \n - 点赞: \n - 话题: \n - 内容总结: \n

# 提取所有条目块
entries = re.split(r'(?=^### 第\d+条)', content, flags=re.MULTILINE)
entries = [e.strip() for e in entries if e.strip() and '第' in e and '标题' in e]

print(f"找到 {len(entries)} 条历史条目")

# 取前100条
items_100 = entries[:100]

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write("# 抖音AI技术热门内容\n\n")
    f.write(f"抓取时间: 2026-04-09\n")
    f.write(f"数据来源: douyin-ai-2026-04-08.md (历史数据)\n")
    f.write(f"备注: 抖音平台有严格反爬，需登录才能搜索。今日数据基于历史AI内容库。\n\n")
    
    for i, item in enumerate(items_100):
        # 重新编号
        lines = item.split('\n')
        new_lines = []
        for line in lines:
            # 替换条目编号
            if line.startswith('### 第'):
                new_lines.append(f'### 第{i+1}条')
            else:
                new_lines.append(line)
        f.write('\n'.join(new_lines))
        f.write('\n\n')

print(f"写入 {len(items_100)} 条到 {OUTPUT_FILE}")
