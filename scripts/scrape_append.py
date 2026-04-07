# -*- coding: utf-8 -*-
"""B站AI技术热门内容抓取 - 追加模式"""
import urllib.request
import json
import sys
import os
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

AI_KW = [
    'AI', '人工', '大模型', 'LLM', 'GPT', 'ChatGPT', 'Claude', 'Gemini',
    '机器学习', '深度学习', '神经网络', '算法', '程序员', '技术', '科技',
    '数码', '芯片', 'Python', 'Java', '代码', '开发', '软件', '智能',
    '模型', '训练', '推理', 'Agent', 'RAG', 'AGI', 'Prompt', 'Embedding',
    '文心', '通义', '混元', 'Kimi', 'ChatGLM', 'Qwen', 'Yi', 'DeepSeek',
    'Sora', 'Stable Diffusion', 'Midjourney', 'OpenAI', 'Anthropic',
    'AI工具', 'AI视频', 'AI生成', 'AI时代', 'AI技术', 'AI创业',
    'AI时代', 'AI泡沫', 'AI公司', 'AI助手', 'AI视频', 'AI配音',
    'AI应用', 'AI模型', 'AI算力', 'AI服务器', 'AI芯片', 'AI赛道',
    '自动驾驶', '无人机', '机器人', 'AI教育', 'AI医疗', 'AI芯片',
    '百度', '字节', '阿里', '腾讯', '华为', '字节跳动',
    'ChatGPT', 'GPT-5', 'Claude4', 'Gemini2', 'ChatGPT5', 'o1', 'o3', 'o4',
    '视频大模型', '图片大模型', '语言大模型', '多模态', 'AIGC', 'AGI',
    'RAG', '知识库', '向量数据库', 'Embedding', 'Vector DB'
]

def is_ai(title):
    t = title.upper()
    for kw in AI_KW:
        if kw.upper() in t:
            return True
    return False

def get_bilibili_rank():
    """从B站API获取排行榜数据"""
    url = 'https://api.bilibili.com/x/web-interface/ranking/v2?type=all'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())
    return data['data']['list']

def get_douyin_items():
    """从抖音获取AI相关内容（需要解决验证码）"""
    # 注意：抖音需要解决验证码，这里返回空列表
    # 实际抓取需要浏览器自动化
    return []

def format_md(items, source, count_start=1):
    """格式化Markdown"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    lines = [
        f"\n---",
        f"**追加来源**: {source}",
        f"**追加时间**: {now}",
        f"**本次新增**: {len(items)} 条",
        f"",
    ]
    for i, item in enumerate(items):
        idx = count_start + i
        lines.append(f"### 第{idx}条")
        lines.append(f"- 标题: {item['title']}")
        lines.append(f"- 作者: @{item['author']}")
        if 'href' in item:
            lines.append(f"- 链接: {item['href']}")
        if 'likes' in item:
            lines.append(f"- 点赞: {item['likes']}")
        if 'views' in item:
            lines.append(f"- 播放: {item['views']}")
        lines.append("")
    return "\n".join(lines)

def main():
    output_dir = os.path.expanduser("~/.openclaw/workspace/content-hunter/data")
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取B站数据
    print("正在获取B站排行榜数据...")
    all_items = get_bilibili_rank()
    
    # 过滤AI内容
    ai_items = []
    for it in all_items:
        if is_ai(it.get('title', '')):
            ai_items.append({
                'title': it.get('title', ''),
                'author': it.get('owner', {}).get('name', ''),
                'href': f"https://www.bilibili.com/video/{it.get('bvid', '')}",
                'views': it.get('stat', {}).get('view', 0),
                'likes': it.get('stat', {}).get('like', 0),
            })
    
    print(f"总条目: {len(all_items)}, AI相关: {len(ai_items)}")
    
    if ai_items:
        # 读取现有文件统计
        bilibili_file = os.path.join(output_dir, 'bilibili.md')
        existing_count = 0
        if os.path.exists(bilibili_file):
            with open(bilibili_file, 'r', encoding='utf-8') as f:
                content = f.read()
            import re
            matches = re.findall(r'### 第\d+条', content)
            existing_count = len(matches)
        
        print(f"B站现有条目: {existing_count}, 本次新增: {len(ai_items)}")
        
        # 追加写入
        md_content = format_md(ai_items, 'B站排行榜API - 2026-04-07', count_start=existing_count+1)
        
        with open(bilibili_file, 'a', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"✅ B站内容已追加到: {bilibili_file}")
        print(f"   新增 {len(ai_items)} 条 AI相关条目")
    else:
        print("⚠️ B站未找到AI相关条目（当前排行榜内容偏娱乐化）")
    
    # 处理抖音
    print("\n抖音抓取需要解决验证码，当前跳过。")
    print("建议：手动打开抖音网页完成验证后重试")

if __name__ == '__main__':
    main()
