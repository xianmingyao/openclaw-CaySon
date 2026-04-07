# -*- coding: utf-8 -*-
"""使用B站官方API获取排行榜数据"""
import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

AI_KW = [
    'AI', '人工', '大模型', 'LLM', 'GPT', 'ChatGPT', 'Claude', 'Gemini',
    '机器学习', '深度学习', '神经网络', '算法', '程序员', '技术', '科技',
    '数码', '芯片', 'Python', 'Java', '代码', '开发', '软件', '智能',
    '模型', '训练', '推理', 'Agent', 'RAG', 'AGI', 'Prompt', 'Embedding',
    '文心', '通义', '混元', 'Kimi', 'ChatGLM', 'Qwen', 'Yi', 'DeepSeek',
    'Sora', 'Stable Diffusion', 'Midjourney', 'OpenAI', 'Anthropic',
    'AI工具', 'AI视频', 'AI生成', 'AI时代', 'AI技术', 'AI创业'
]

def is_ai(title):
    t = title.upper()
    for kw in AI_KW:
        if kw.upper() in t:
            return True
    return False

# 调用B站排行榜API
url = 'https://api.bilibili.com/x/web-interface/ranking/v2?type=all'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=15) as r:
    data = json.loads(r.read())

items = data['data']['list']

# 过滤AI相关内容
ai_items = [(it, idx+1) for idx, it in enumerate(items) if is_ai(it['title'])]

print(f"总条目: {len(items)}, AI相关: {len(ai_items)}")
print()

for idx, (it, rank) in enumerate(ai_items[:100]):
    title = it.get('title', '')
    author = it.get('owner', {}).get('name', '')
    bvid = it.get('bvid', '')
    href = f'https://www.bilibili.com/video/{bvid}'
    print(f"### 第{idx+1}条")
    print(f"- 标题: {title}")
    print(f"- UP主: @{author}")
    print(f"- 链接: {href}")
    print()
