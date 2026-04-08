# -*- coding: utf-8 -*-
"""
清洗并整理抖音和B站数据文件
- 去重（每条只保留一个）
- 重新编号
- 追加本次抓取的100条
"""
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

def clean_and_renumber(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 按 ### 第X条 分割
    pattern = r'(### 第\d+条\n)'
    parts = re.split(pattern, content)
    
    # 收集所有条目，按编号去重（保留最大编号的，即最新版本）
    items = {}  # num -> full_text
    seen_titles = {}  # title -> num
    
    for i in range(1, len(parts), 2):
        header = parts[i]  # "### 第123条\n"
        body = parts[i+1] if i+1 < len(parts) else ''
        full = header + body
        
        nums = re.findall(r'第(\d+)条', header)
        if not nums:
            continue
        num = int(nums[0])
        
        # 提取标题去重
        title_match = re.search(r'- 标题: (.+)', body)
        if title_match:
            title = title_match.group(1).strip()
            if title in seen_titles:
                # 保留编号更大的
                if num > seen_titles[title]:
                    items[seen_titles[title]] = None  # 标记旧的删除
                    seen_titles[title] = num
                    items[num] = full
                else:
                    items[num] = None
                continue
        
        items[num] = full
    
    # 过滤None，排序
    valid_items = sorted([(k, v) for k, v in items.items() if v is not None])
    print(f'{filepath}: {len(valid_items)} 有效条目 (去除了 {len(items) - len(valid_items)} 个重复)')
    
    # 重新编号
    md_lines = ['# 热门内容\n']
    for new_num, (_, item_text) in enumerate(valid_items, start=1):
        # 替换旧编号为新编号
        new_item = re.sub(r'第\d+条', f'第{new_num}条', item_text)
        md_lines.append(new_item.rstrip('\n'))
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(md_lines) + '\n')
    
    return len(valid_items)

# 清洗两个文件
print('=== 清洗整理数据文件 ===\n')
d_count = clean_and_renumber('E:/workspace/content-hunter/data/douyin.md')
b_count = clean_and_renumber('E:/workspace/content-hunter/data/bilibili.md')

print(f'\n最终: douyin.md={d_count}条, bilibili.md={b_count}条')
