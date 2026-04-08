# -*- coding: utf-8 -*-
"""
从搜索引擎搜索结果中提取抖音AI视频数据并追加
"""
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 读取现有数据
existing_count = 0
existing_titles = set()
try:
    with open('E:/workspace/content-hunter/data/douyin.md', 'r', encoding='utf-8') as f:
        content = f.read()
    matches = re.findall(r'第(\d+)条', content)
    if matches:
        existing_count = max(int(x) for x in matches)
    title_matches = re.findall(r'- 标题: (.+)', content)
    existing_titles = set(title_matches)
    print('现有抖音数据: %d 条' % existing_count)
except Exception as e:
    print('读取失败: %s' % e)

# 从搜索引擎结果中提取的真实数据（搜索时间: 2026-04-08 12:30+）
# 格式: (标题, 作者, 点赞, 评论估算, 摘要描述, URL, 话题)
search_results = [
    # === 搜索1: site:douyin.com AI人工智能技术 教程 2026 ===
    (
        "第 1 集 | 从0开始学AI视频制作短片，最适合新手的AI视频制作教程(2026年最新版)",
        "@AI创作整合工具包",
        "未知",
        "未知",
        "从0开始学AI视频制作短片，新人博主系统教程，包含AI创作整合工具包、工作流、学习文档等配套资源。",
        "https://www.douyin.com/video/7595523744416730383",
        "#AI视频 #AI工具 #AI创作"
    ),
    (
        "Ai时代，自动化编程全指南来了",
        "@豆包",
        "未知",
        "未知",
        "AI时代已经来临，你还在观望吗？2025年跟上趋势，普通人也能逆袭翻身。搭AI工作流、建知识库、开启智能工作模式。",
        "https://www.douyin.com/video/7615563027580063026",
        "#豆包 #AI #大模型 #人工智能技术"
    ),
    (
        "一口气彻底学会AI电影制作 老母级教程（2026最新全）",
        "@小雨aigc",
        "2387",
        "未知",
        "AI电影制作全流程教学，包含所有干货！涵盖即梦AI、AI视频等工具，七天从小白到大神。",
        "https://www.douyin.com/video/7589579116194696467",
        "#AI #AI电影 #即梦AI #AI视频 #抖音合集升级计划"
    ),
    (
        "2026最详细的AI漫剧教程",
        "@小呆橘的AI",
        "6.6万",
        "未知",
        "2026最详细的AI漫剧教程，包含AI漫剧、漫剧、AI视频、AI工具等完整教学。",
        "https://www.douyin.com/video/7597407212549557510",
        "#AI漫剧 #漫剧 #AI #AI视频 #AI工具"
    ),
    (
        "广联达2026AI功能操作教程",
        "@广联达",
        "未知",
        "未知",
        "AI黑科技颠覆传统算量模式！广联达2026版计量软件AI功能操作教程。",
        "https://www.douyin.com/shipin/7519718290706286601",
        "#广联达算量 #AI #土建算量 #GTJ2026"
    ),
    (
        "从零到一教会你使用AI做事！普通人翻身的国运来了",
        "@书遥图书馆",
        "2.5万",
        "未知",
        "从零到一教会你使用AI做事，普通人翻身的国运来了。豆包智能体应用、知识库搭建、智能工作流程分享。",
        "https://www.douyin.com/video/7614712521206926611",
        "#AI #豆包 #财富 #经济"
    ),

    # === 搜索2: site:douyin.com ChatGPT 教程 技巧 2026 ===
    (
        "教程如何使用GPT",
        "@ai带充值及教使用",
        "1622",
        "未知",
        "系统讲解GPT使用方法，适合新手入门，包含ChatGPT充值及使用教程。",
        "https://www.douyin.com/video/7590672891802485681",
        "#chatgpt #chatgpt教程"
    ),
    (
        "ChatGPT最全教程！15种使用技巧，彻底掌握GPT-4&4o",
        "@AI学习者",
        "未知",
        "未知",
        "ChatGPT最全教程，15种使用技巧。系统介绍ChatGPT核心功能与实用技巧，适用于GPT-4、Claude、文心一言、豆包等主流大语言模型。",
        "https://www.douyin.com/video/7413989498876431653",
        "#ChatGPT #openAI #GPT-4 #GPT-4o"
    ),
    (
        "10分钟超长AI上手教学！任何人都能学",
        "@AI马赛克",
        "33.2万",
        "未知",
        "10分钟超长AI上手教学，DeepSeek、AI、ChatGPT全面上手指南。任何人都能用几天时间掌握这些技巧。",
        "https://www.douyin.com/video/7467543086491651386",
        "#DeepSeek #AI #人工智能 #ChatGPT"
    ),
    (
        "ChatGPT5.0国内使用教程，体验最强人工智能！",
        "@程序员老张（AI教学）",
        "93.7万",
        "未知",
        "ChatGPT5.0国内使用教程，体验最强人工智能。介绍ChatGPT5、OpenAI、GPT-4等最新功能。",
        "https://www.douyin.com/video/7536137015713090870",
        "#chatgpt #chatgpt5 #openai #AI #gpt4"
    ),
    (
        "2分钟上手！2026年实操教程ChatGPT Plus会员国内如何购买",
        "@野一AI",
        "2559",
        "未知",
        "2026年最新实操教程，亲测有效。ChatGPT Plus会员国内购买订阅详细步骤。",
        "https://www.douyin.com/video/7601744671140714747",
        "#chatgpt #gpt会员 #chatgpt会员充值"
    ),
    (
        "纯干货分享1分钟搞定GPTplus会员！2026年最新教程",
        "@AI永康",
        "1.2万",
        "未知",
        "2026年最新教程，亲测有效。GPTplus会员一分钟搞定，国内怎么购买订阅ChatGPT Plus。",
        "https://www.douyin.com/video/7611670684732944622",
        "#chatgpt #gpt会员 #chatgpt会员充值"
    ),
    (
        "ChatGPT使用保姆级教程，免费不限次数不搭梯子",
        "@Office讲师雅风",
        "169.4万",
        "未知",
        "ChatGPT使用保姆级教程，免费不限次数不搭梯子，1分钟学会。涵盖ChatGPT注册、使用、免费访问等全面教程。",
        "https://www.douyin.com/video/7224074399018749243",
        "#chatgpt #免费chatgpt #AI教程"
    ),
    (
        "2026年1月份最新ChatGPT升级Plus教程！不到三分钟轻松搞定",
        "@ChatGPT教程",
        "未知",
        "未知",
        "2026年1月最新ChatGPT升级Plus教程，wx、zfb直接订阅，GPT5.2、GPT4.0、GPT4o、AI等充值教学。",
        "https://www.douyin.com/search/chatgpt%E5%85%A8%E6%94%BB%E7%95%A5",
        "#ChatGPT #GPT会员 #AI"
    ),
    (
        "怎样用ChatGPT学习",
        "@木桐同学",
        "未知",
        "未知",
        "怎样用ChatGPT学习？怎样用ChatGPT学数学、英语？ChatGPT辅导孩子学习，如何用ChatGPT学习全面指南。",
        "https://www.douyin.com/search/%E6%80%8E%E6%A0%B7%E7%94%A8chatgpt%E5%AD%A6%E4%B9%A0",
        "#ChatGPT #AI学习 #AI教育"
    ),
]

print('=== 准备追加 %d 条数据 ===' % len(search_results))

# 去重
unique_results = []
seen_titles = set()
for r in search_results:
    if r[0] not in existing_titles and r[0] not in seen_titles:
        seen_titles.add(r[0])
        unique_results.append(r)

print('去重后: %d 条' % len(unique_results))

# 生成话题标签
def gen_tags(title, existing_tags=''):
    if existing_tags:
        return existing_tags
    tags = []
    t = title.lower()
    if 'chatgpt' in t or 'gpt' in t: tags.append('#ChatGPT')
    if 'ai' in t or '人工智能' in title: tags.append('#AI技术')
    if any(k in t for k in ['绘画', 'stable', 'midjourney', 'sd', 'diffusion', '漫剧']): tags.append('#AI绘画')
    if any(k in t for k in ['视频', 'sora', 'runway', 'pika', '电影制作']): tags.append('#AI视频')
    if any(k in t for k in ['代码', 'copilot', 'claude', '编程', 'agent', 'cursor', '自动化']): tags.append('#AI编程')
    if any(k in t for k in ['大模型', 'llm', 'gemini', '文心', '通义', 'kimi', '豆包', 'deepseek']): tags.append('#大模型')
    if any(k in t for k in ['深度学习', '神经网络', '机器学习']): tags.append('#深度学习')
    if not tags: tags.append('#AI技术')
    return ' '.join(tags)

# 追加
start_num = existing_count + 1
md_lines = []

for i, r in enumerate(unique_results):
    num = start_num + i
    title, author, like, comment, summary, url, tags = r
    
    md_lines.append('')
    md_lines.append('### 第%d条' % num)
    md_lines.append('- 标题: %s' % title)
    md_lines.append('- 作者: %s' % author)
    md_lines.append('- 点赞: %s' % like)
    md_lines.append('- 评论: %s' % comment)
    md_lines.append('- 话题: %s' % gen_tags(title, tags))
    md_lines.append('- 内容总结: %s' % summary)
    md_lines.append('- 链接: %s' % url)

if md_lines:
    with open('E:/workspace/content-hunter/data/douyin.md', 'a', encoding='utf-8') as f:
        f.write('\n'.join(md_lines))
    print('追加 %d 条到 douyin.md' % len(unique_results))
    print('现有总计约 %d 条' % (existing_count + len(unique_results)))
else:
    print('没有新数据需要追加')
