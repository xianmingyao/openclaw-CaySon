import json
import os
import re

def clean(text):
    """Remove HTML entities and clean text"""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

# Data from earlier successful DuckDuckGo search
douyin_items = [
    {
        "title": "手把手部署开源版chat-gpt gpt-oss 20b 本地部署教程",
        "author": "卢哥-AI",
        "likes": "6.6万",
        "tags": ["gptoss", "gpt开源"],
        "url": "https://www.douyin.com/video/7535921043328765220",
        "date": "20250808",
        "platform": "抖音",
        "summary": "手把手教你在本地部署开源版GPT-oss 20b模型的详细教程"
    },
    {
        "title": "ChatGPT5.0国内使用教程，体验最强人工智能!",
        "author": "程序员老张（AI教学）",
        "likes": "93.7万",
        "tags": ["chatgpt", "chatgpt5", "openai", "AI", "gpt4"],
        "url": "https://www.douyin.com/video/7536137015713090870",
        "date": "20250808",
        "platform": "抖音",
        "summary": "国内使用ChatGPT5.0的完整教程，体验最强人工智能模型"
    },
    {
        "title": "Chat Gpt保姆级电脑、手机三端使用教程",
        "author": "子戎（可指导安装GPT）",
        "likes": "5.4万",
        "tags": ["人工智能", "ai", "ChatGPT"],
        "url": "https://www.douyin.com/video/7448660314150784314",
        "date": "20241215",
        "platform": "抖音",
        "summary": "ChatGPT在电脑和手机三端使用的保姆级教程"
    },
    {
        "title": "【超级福利】免费使用ChatGPT-4保姆级教程，帮你每月省20美元",
        "author": "大陈聊AI",
        "likes": "21.9万",
        "tags": ["ChatGPT", "ai", "GPT4", "人工智能"],
        "url": "https://www.douyin.com/video/7268557524649971002",
        "date": "20230818",
        "platform": "抖音",
        "summary": "免费使用ChatGPT-4的保姆级教程，帮助用户每月节省20美元订阅费"
    },
    {
        "title": "大师的ai小灶 - AI一键3D化效果碾压99%同事",
        "author": "大师的ai小灶",
        "likes": "未知",
        "tags": ["AI", "PPT", "GPT4o"],
        "url": "https://www.douyin.com/user/MS4wLjABAAAAohe8JB4RvITJitJ69b7cV4NTaYTMYrVI43C-3SUnPPc",
        "date": "未知",
        "platform": "抖音",
        "summary": "AI一键3D化效果教程，让PPT制作效率大幅提升"
    },
    {
        "title": "在国内没有魔法也可以使用Chat GPT教程来了",
        "author": "AI数字星球（超脑）",
        "likes": "3985",
        "tags": ["干货分享", "人工智能", "chatgpt应用领域", "AI"],
        "url": "https://www.douyin.com/video/7278899681168543010",
        "date": "20230915",
        "platform": "抖音",
        "summary": "无需翻墙在国内使用ChatGPT的教程"
    },
    {
        "title": "搭建chat gpt聊天机器人教程",
        "author": "未知",
        "likes": "未知",
        "tags": ["ai聊天程序chatgpt", "openai", "chatgpt"],
        "url": "https://www.douyin.com/shipin/7291165728013551651",
        "date": "未知",
        "platform": "抖音",
        "summary": "手把手教你搭建ChatGPT微信聊天机器人的完整教程"
    },
    {
        "title": "Apple AI + ChatGPT，这才是满血版iPhone",
        "author": "苹果迷",
        "likes": "未知",
        "tags": ["appleai", "chatgpt", "数码科技", "手机技巧"],
        "url": "https://www.douyin.com/search/chatgpt",
        "date": "未知",
        "platform": "抖音",
        "summary": "Apple Intelligence与ChatGPT深度整合，让iPhone获得顶级AI能力"
    },
    {
        "title": "ChatGPT最全安装和使用教程来了",
        "author": "未知",
        "likes": "未知",
        "tags": ["gpt5", "gpt", "chatgpt", "大模型", "openai"],
        "url": "https://www.douyin.com/video/7539489926808423699",
        "date": "未知",
        "platform": "抖音",
        "summary": "ChatGPT最全安装和使用教程，包含多种AI模型的API中转服务介绍"
    },
    {
        "title": "也是用上了gpt5.4",
        "author": "潇潇雨下",
        "likes": "25",
        "tags": ["chatgpt", "ai教程"],
        "url": "https://www.douyin.com/video/7614847098424695985",
        "date": "20260308",
        "platform": "抖音",
        "summary": "分享使用GPT5.4的体验"
    }
]

# Build markdown
lines = []
lines.append("# 抖音 AI技术热门内容")
lines.append("")
lines.append("> 抓取时间：2026-04-07 16:30 | 数据来源：抖音搜索（Google索引） | 关键词：AI人工智能/ChatGPT等 | 数量：10条")
lines.append("> **注意**：抖音有严格反爬机制（CAPTCHA验证码+API认证），直接爬取被拦截，仅获取Google搜索索引收录的公开内容")
lines.append("")
lines.append("---")
lines.append("")

for i, v in enumerate(douyin_items):
    tags_str = " / ".join(v['tags'])
    lines.append(f"### 第{i+1}条 / Item #{i+1}")
    lines.append(f"- 标题 / Title: {v['title']}")
    lines.append(f"- 作者 / Author: @{v['author']}")
    lines.append(f"- 点赞 / Likes: {v['likes']}")
    lines.append(f"- 话题 / Tags: {tags_str}")
    lines.append(f"- 内容总结 / Summary: {v['summary']}")
    lines.append(f"- 链接 / URL: {v['url']}")
    lines.append("")

# APPEND to existing douyin.md
data_dir = r'C:\Users\Administrator\.openclaw\workspace\content-hunter\data'
output_path = os.path.join(data_dir, 'douyin.md')
with open(output_path, 'a', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')

print(f"DOUYIN DATA APPENDED to: {output_path}")
print(f"Total records: {len(douyin_items)}")
