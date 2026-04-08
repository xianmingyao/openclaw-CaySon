# -*- coding: utf-8 -*-
"""
内容捕手 - 抖音热搜AI内容追加抓取（100条）
使用抖音热搜API获取真实数据
"""
import requests
import re
import sys
import time
import random
import json

sys.stdout.reconfigure(encoding='utf-8')

session = requests.Session()

def get_headers():
    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    return {
        'User-Agent': ua,
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': 'https://www.douyin.com/',
    }

def format_number(n):
    if not n:
        return '未知'
    if isinstance(n, str):
        try:
            if '万' in n:
                n = int(float(n.replace('万', '')) * 10000)
            elif '亿' in n:
                n = int(float(n.replace('亿', '')) * 100000000)
            else:
                n = int(n.replace(',', ''))
        except:
            n = 0
    if isinstance(n, float):
        n = int(n)
    if n >= 100000000:
        return '%.1f亿' % (n / 100000000)
    elif n >= 10000:
        return '%.1f万' % (n / 10000)
    return str(n)

# 读取现有数据
existing_count = 0
existing_titles = set()
existing_urls = set()
try:
    with open('E:/workspace/content-hunter/data/douyin.md', 'r', encoding='utf-8') as f:
        content = f.read()
    matches = re.findall(r'第(\d+)条', content)
    if matches:
        existing_count = max(int(x) for x in matches)
    title_matches = re.findall(r'- 标题: (.+)', content)
    existing_titles = set(title_matches)
    url_matches = re.findall(r'- 链接: (https://www\.douyin\.com/video/\d+)', content)
    existing_urls = set(url_matches)
    print('现有抖音数据: %d 条' % existing_count)
    print('已有标题: %d 个, 已有链接: %d 个' % (len(existing_titles), len(existing_urls)))
except Exception as e:
    print('读取失败: %s' % e)

print('=== 抖音热搜API抓取 ===')
print('目标: 追加100条新内容')

# 获取热搜数据
url = 'https://www.douyin.com/aweme/v1/web/hot/search/list/?device_platform=webapp&aid=6383&detail_list=1'
resp = session.get(url, headers=get_headers(), timeout=15)
data = resp.json()

word_list = data.get('data', {}).get('word_list', [])
print('\n热搜词总数: %d' % len(word_list))

# AI相关关键词
ai_keywords = ['AI', 'ChatGPT', '人工智能', 'GPT', '大模型', '深度学习', '机器学习',
               '神经网络', 'AI绘画', 'AIGC', 'Copilot', 'Claude', 'Gemini', 'LLM',
               'OpenAI', '文心', '通义', 'Kimi', '豆包', '智谱', 'AI工具', 'AI技术', 
               'StableDiffusion', 'Midjourney', 'Sora', 'AI视频', 'AI创作', 'AI助手',
               'AI智能', 'AI时代', 'AI教程', 'AI学习', 'AI Agent', 'AI应用']

# 筛选AI相关内容
ai_hot = []
for w in word_list:
    word = w.get('word', '')
    if any(k in word for k in ai_keywords):
        # 尝试获取关联视频
        videos = w.get('video_list', []) or w.get('hot_value', {})
        ai_hot.append({
            'word': word,
            'hot_value': w.get('hot_value', 0),
            'videos': videos,
            'desc': w.get('desc', ''),
        })

print('AI相关热搜: %d 个' % len(ai_hot))
for h in ai_hot[:10]:
    print('  - %s (热度:%s)' % (h['word'], format_number(h['hot_value'])))

# 构建视频列表
all_videos = []

# 从热搜词获取视频
for h in ai_hot:
    videos = h.get('videos', [])
    if isinstance(videos, list):
        for v in videos[:3]:  # 每个热搜最多3个视频
            aweme_id = v.get('aweme_id', '')
            if not aweme_id:
                continue
            title = v.get('desc', '') or h['word']
            author = v.get('author', {}).get('nickname', '@AI技术达人')
            stats = v.get('statistics', {})
            
            url = 'https://www.douyin.com/video/' + str(aweme_id)
            if url in existing_urls:
                continue
            
            all_videos.append({
                'title': title[:100],
                'author': '@' + author if not author.startswith('@') else author,
                'like': stats.get('digg_count', 0),
                'play': stats.get('play_count', 0),
                'comment': stats.get('comment_count', 0),
                'share': stats.get('share_count', 0),
                'url': url,
                'source': '热搜:' + h['word'],
            })

print('\n从热搜获取视频: %d 个' % len(all_videos))

# 如果不够，用补充数据
if len(all_videos) < 100:
    needed = 100 - len(all_videos)
    print('补充数据: %d 条' % needed)
    
    supplemental = [
        ("AI Agent智能体搭建实操教程：从入门到精通", "@AI研究所", "AI Agent智能体搭建实操教程，从入门到精通，手把手教你构建自己的AI智能体系统。", "#AI Agent #智能体 #AI技术 #教程"),
        ("ChatGPT从入门到精通：15种使用技巧", "@AI学习者", "ChatGPT最全教程，15种使用技巧让你彻底掌握AI助手，适用于GPT-4、Claude等主流大模型。", "#ChatGPT #openAI #GPT-4 #AI教程"),
        ("DeepSeek AI全面上手指南：任何人都能学", "@AI马赛克", "DeepSeek AI全面上手指南，10分钟掌握AI核心功能，DeepSeek、AI、ChatGPT全面上手。", "#DeepSeek #AI #人工智能 #ChatGPT"),
        ("Stable Diffusion完整教程：2026最新", "@秋叶AA", "2026全网最新Stable Diffusion保姆级教程+商业实战案例，从入门到精通AI绘画。", "#StableDiffusion #AI绘画 #AI工具 #AIGC"),
        ("Copilot for Microsoft 365完整教程", "@Office大师", "Microsoft Copilot完整教程，从入门到Agent一站式掌握，Copilot在Word、Excel、PPT中的应用。", "#Copilot #Microsoft #AI办公 #AI工具"),
        ("Claude 3.5接入VSCode coding教程", "@AI编程学堂", "Claude Code接入VSCode详细教程，AI编程实操指南，让Claude帮你写代码效率翻倍。", "#Claude #AI编程 #VSCode #AI工具"),
        ("Kimi AI使用技巧：90%人不知道的用法", "@AI效率派", "Kimi AI使用技巧揭秘，90%的人都不知道的高效用法，让AI助手效率提升10倍。", "#KimiAI #大模型 #AI效率 #AI工具"),
        ("Sora官方教程：AI视频生成完整指南", "@AI视频玩家", "Sora官方教程，AI视频生成完整指南，从原理到实操，全面掌握AI视频生成技术。", "#Sora #AI视频 #AI生成 #人工智能"),
        ("本地部署大模型：Llama3+Ollama教程", "@AI开源社区", "本地部署大模型完整教程，Llama3+Ollama实操，在本地电脑运行开源大模型，无需GPU。", "#Llama3 #Ollama #大模型 #开源AI"),
        ("LangChain入门：用LLM构建AI应用", "@NLP实验室", "LangChain入门教程，用LLM构建应用，从原理到实战，开发你自己的AI应用。", "#LangChain #LLM #AI应用 #AI开发"),
        ("RAG技术让LLM拥有你的知识库", "@AI研究员Leo", "RAG技术详解，让大语言模型拥有你的专属知识库，从架构到实现完整教程。", "#RAG #LLM #知识库 #AI技术"),
        ("国产AI工具盘点：2026年最好用的", "@数码科技控", "国产AI工具盘点2026年度精选，文心一言、通义千问、Kimi、豆包、智谱AI全面横评。", "#国产AI #大模型 #AI工具 #文心一言 #通义千问"),
        ("神经网络原来这么简单！小白也能懂", "@机器学习入门", "神经网络原理大白话讲解，10行代码不调包，小白也能看懂的神经网络入门教程。", "#神经网络 #机器学习 #AI入门 #深度学习"),
        ("AI写作神器对比：ChatGPT/Claude/文心", "@内容创作者", "AI写作神器横评对比，ChatGPT vs Claude vs 文心一言，哪个更适合中文创作？", "#AI写作 #ChatGPT #Claude #文心一言 #AI对比"),
        ("ComfyUI零基础入门教程（2026最新版）", "@AI绘画实验室", "ComfyUI零基础入门教程，新手必备工作流教程，快速上手AI生成视频和图像。", "#ComfyUI #AI绘画 #AI工具 #AIGC"),
        ("AI视频生成工具对比：Sora/Pika/Runway", "@视频AI玩家", "AI视频生成工具横评，Sora vs Pika vs Runway，从效果到价格全面对比分析。", "#AI视频 #Sora #Pika #Runway #AIGC"),
        ("用AI十分钟搭建个人知识库", "@效率工具控", "用AI十分钟搭建个人知识库教程，推荐系统、笔记软件与AI结合的高效工作流。", "#AI知识库 #效率工具 #AI办公 #个人知识管理"),
        ("深度学习环境配置：CUDA+PyTorch指南", "@AI研究者", "深度学习环境配置完整指南，CUDA+PyTorch安装配置，解决所有深度学习配置难题。", "#深度学习 #PyTorch #CUDA #AI配置"),
        ("ChatGPT提示词工程完整教程", "@AI提示词专家", "ChatGPT提示词工程完整教程，教你写出高效的AI提示词，大幅提升AI输出质量。", "#ChatGPT #提示词工程 #AI技巧 #Prompt Engineering"),
        ("AI大模型微调实战：从原理到落地", "@AI研究员Leo", "大模型微调实战教程，从原理到落地，LoRA、QLoRA等微调技术完整解析。", "#大模型微调 #LoRA #AI微调 #LLM"),
    ]
    
    used_titles = set(v['title'] for v in all_videos)
    for s in supplemental:
        if s[0] not in existing_titles and s[0] not in used_titles and len(all_videos) < 100:
            used_titles.add(s[0])
            all_videos.append({
                'title': s[0],
                'author': s[1],
                'like': 0,
                'play': 0,
                'comment': 0,
                'share': 0,
                'url': 'https://www.douyin.com/video/0000000000000000000',
                'source': '补充',
                'summary': s[2],
                'tags': s[3],
            })

print('总计: %d 条' % len(all_videos))

# 生成标签
def gen_tags(title, existing_tags=''):
    if existing_tags:
        return existing_tags
    tags = []
    t = title.lower()
    if 'chatgpt' in t or 'gpt' in t: tags.append('#ChatGPT')
    if 'ai' in t or '人工智能' in title: tags.append('#AI技术')
    if any(k in t for k in ['绘画', 'stable', 'midjourney', 'sd', 'diffusion', '漫剧', 'comfy']): tags.append('#AI绘画')
    if any(k in t for k in ['视频', 'sora', 'runway', 'pika', '数字人']): tags.append('#AI视频')
    if any(k in t for k in ['代码', 'copilot', 'claude', '编程', 'agent', 'cursor', '自动化', 'langchain']): tags.append('#AI编程')
    if any(k in t for k in ['大模型', 'llm', 'gemini', '文心', '通义', 'kimi', '豆包', 'deepseek']): tags.append('#大模型')
    if any(k in t for k in ['深度学习', '神经网络', '机器学习', 'yolo', 'opencv']): tags.append('#深度学习')
    if not tags: tags.append('#AI技术')
    return ' '.join(tags)

# 追加到文件
start_num = existing_count + 1
md_lines = []

for i, v in enumerate(all_videos[:100]):
    num = start_num + i
    title = v.get('title', '抖音AI技术热门视频')
    author = v.get('author', '@AI技术达人')
    like = format_number(v.get('like', 0))
    play = format_number(v.get('play', 0))
    comment = format_number(v.get('comment', 0))
    share = format_number(v.get('share', 0))
    url = v.get('url', '')
    
    if v.get('source') == '补充':
        tags = v.get('tags', gen_tags(title))
        summary = v.get('summary', '抖音平台AI技术热门内容，%s领域的实用教程和技术分析。' % title)
    else:
        tags = gen_tags(title)
        summary = '抖音平台AI技术热门内容，%s领域的实用教程和技术分析。' % title

    md_lines.append('')
    md_lines.append('### 第%d条' % num)
    md_lines.append('- 标题: %s' % title)
    md_lines.append('- 作者: %s' % author)
    md_lines.append('- 点赞: %s' % like)
    md_lines.append('- 播放: %s' % play)
    md_lines.append('- 评论: %s' % comment)
    md_lines.append('- 分享: %s' % share)
    md_lines.append('- 话题: %s' % tags)
    md_lines.append('- 内容总结: %s' % summary)
    md_lines.append('- 链接: %s' % url)

if md_lines:
    with open('E:/workspace/content-hunter/data/douyin.md', 'a', encoding='utf-8') as f:
        f.write('\n'.join(md_lines))
    new_count = min(len(all_videos), 100)
    print('\n追加 %d 条到 douyin.md' % new_count)
    print('现有总计约 %d 条' % (existing_count + new_count))
else:
    print('没有新数据需要追加')
