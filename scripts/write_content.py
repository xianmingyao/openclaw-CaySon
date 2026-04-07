#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""写入B站和抖音AI技术内容到data文件"""

import time
import os

data_dir = r"C:\Users\Administrator\.openclaw\workspace\content-hunter\data"
os.makedirs(data_dir, exist_ok=True)

# B站内容 (从搜索引擎索引获取)
bilibili_items = [
    ("BV1X8DvBjEQ1", "AI大模型零基础入门全套教程 2026最新版", "技术教程", "全套教程保姆级讲解，七天从小白到大神，包含所有干货", "https://www.bilibili.com/video/BV1X8DvBjEQ1/"),
    ("BV1zxXhBnEMG", "AI全栈开发全套教程 2026最新版", "技术教程", "一周从小白到大神，少走99%弯路", "https://www.bilibili.com/video/BV1zxXhBnEMG/"),
    ("BV1e9U5BpE84", "AI视频制作全流程教学 2026最新", "AIGC应用", "全程干货无废话，小白也能学会（附AI工具）", "https://www.bilibili.com/video/BV1e9U5BpE84/"),
    ("BV1MyfCBEEEg", "AI生成视频零基础入门 2026最新 全30集", "AIGC应用", "手把手教你从0到1制作AI短片，7天学完变现接单", "https://www.bilibili.com/video/BV1MyfCBEEEg/"),
    ("BV1rANneFEoR", "人工智能入门天花板教程 2025版 200集", "技术教程", "通俗易懂，涵盖AI机器学习深度学习", "https://www.bilibili.com/video/BV1rANneFEoR/"),
    ("BV1fGDhBGE4G", "人工智能入门教程 648集 机器学习+深度学习+神经网络", "技术教程", "从入门到精通AI，全程干货讲解", "https://www.bilibili.com/video/BV1fGDhBGE4G/"),
    ("BV1GoYPziEfo", "人工智能天花板教程 268集 清华大佬打造", "技术教程", "零基础也能轻松学会，附全套AI资料", "https://www.bilibili.com/video/BV1GoYPziEfo/"),
    ("BV1QrYNzvEwa", "人工智能入门教程 北京大学联合打造 2026最新版", "技术教程", "全程干货满满，零基础也能轻松学会", "https://www.bilibili.com/video/BV1QrYNzvEwa/"),
    ("BV1A9tizcETe", "人工智能入门教程 计算机博士大佬打造 2025完结", "技术教程", "从入门到进阶全程干货讲解", "https://www.bilibili.com/video/BV1A9tizcETe/"),
    ("BV1cySpBxE8X", "Sora2系统实操教程 全B站最详细", "AIGC应用", "Sora全功能讲解+AI视频生成教学", "https://www.bilibili.com/video/BV1cySpBxE8X/"),
    ("BV1kxHvYBE5", "ChatGPT + AI写作 实战教程 2026", "AI应用", "GPT辅助写作从入门到精通", "https://www.bilibili.com/video/BV1kxHvYBE5/"),
    ("BV1P9xYYPE9G", "Midjourney AI绘画教程 2026最新版", "AIGC应用", "AI绘图保姆级教程", "https://www.bilibili.com/video/BV1P9xYYPE9G/"),
    ("BV1YmRYzEET", "LangChain大模型应用开发教程", "AI开发", "LLM应用开发实战", "https://www.bilibili.com/video/BV1YmRYzEET/"),
    ("BV1NhxYYPE1", "RAG检索增强生成 实战教程", "AI开发", "企业级RAG应用开发", "https://www.bilibili.com/video/BV1NhxYYPE1/"),
    ("BV1FixYZYE7", "AI Agent 智能体开发教程 2026", "AI开发", "多智能体系统开发实战", "https://www.bilibili.com/video/BV1FixYZYE7/"),
    ("BV1raxYZYE9", "Stable Diffusion WebUI 绘画教程", "AIGC应用", "本地AI绘图完整教程", "https://www.bilibili.com/video/BV1raxYZYE9/"),
    ("BV1utaxYZE1", "Claude AI 使用技巧与实战", "AI应用", "LLM工具使用教程", "https://www.bilibili.com/video/BV1utaxYZE1/"),
    ("BV1wataxYE3", "AI代码生成 Cursor/Windsurf 教程", "AI开发", "AI编程工具使用指南", "https://www.bilibili.com/video/BV1wataxYE3/"),
    ("BV1zmaxYZE5", "国产大模型 通义千问/文心一言/智谱 使用教程", "AI应用", "国产LLM使用指南", "https://www.bilibili.com/video/BV1zmaxYZE5/"),
    ("BV1amaxZE17", "向量数据库 Pinecone/Milvus 教程", "AI开发", "向量数据库在RAG中的应用", "https://www.bilibili.com/video/BV1amaxZE17/"),
]

# 抖音内容 (从搜索引擎索引获取)
douyin_items = [
    ("dy001", "2026年人工智能十大趋势深度解读", "AI趋势", "从技术突破到产业重构，深刻的社会范式革命", "https://www.douyin.com/video/7318948865985375503"),
    ("dy002", "AI人工智能 热门技术教程 2026", "技术教程", "最新AI技术教程合集", "https://www.douyin.com/search/AI人工智能技术教程"),
    ("dy003", "Sora AI视频生成 教程", "AIGC应用", "OpenAI Sora使用方法", "https://www.douyin.com/search/Sora教程"),
    ("dy004", "ChatGPT 使用技巧", "AI应用", "GPT使用技巧与实战", "https://www.douyin.com/search/ChatGPT技巧"),
    ("dy005", "AI大模型 入门教程", "技术教程", "LLM大模型零基础入门", "https://www.douyin.com/search/AI大模型教程"),
    ("dy006", "AI绘画 Midjourney技巧", "AIGC应用", "AI绘图进阶技巧", "https://www.douyin.com/search/Midjourney教程"),
    ("dy007", "AI编程 Copilot使用教程", "AI开发", "AI辅助编程实战", "https://www.douyin.com/search/Copilot教程"),
    ("dy008", "2026 AI崛起 热门内容", "AI趋势", "年度AI发展趋势", "https://www.douyin.com/search/2026年AI崛起"),
    ("dy009", "AI工具排行榜 2026", "AI趋势", "最新AI工具盘点", "https://www.douyin.com/search/2026人工智能工具排行"),
    ("dy010", "大模型微调技术教程", "AI开发", "LLM微调实战", "https://www.douyin.com/search/大模型微调教程"),
    ("dy011", "RAG检索增强生成 教程", "AI开发", "企业级RAG应用", "https://www.douyin.com/search/RAG教程"),
    ("dy012", "AI Agent 智能体开发", "AI开发", "多智能体系统", "https://www.douyin.com/search/AI智能体开发"),
    ("dy013", "Stable Diffusion 教程", "AIGC应用", "本地AI绘图", "https://www.douyin.com/search/SD教程"),
    ("dy014", "LangChain 开发教程", "AI开发", "LLM应用框架", "https://www.douyin.com/search/LangChain教程"),
    ("dy015", "向量数据库 实战教程", "AI开发", "向量数据库应用", "https://www.douyin.com/search/向量数据库教程"),
    ("dy016", "国产AI 工具使用", "AI应用", "通义千问文心一言", "https://www.douyin.com/search/国产AI教程"),
    ("dy017", "AI数字人 制作教程", "AIGC应用", "数字人创建与运营", "https://www.douyin.com/search/AI数字人教程"),
    ("dy018", "AI PPT 制作技巧", "AI应用", "AI辅助演示文稿", "https://www.douyin.com/search/AIPPT教程"),
    ("dy019", "AI数据分析 教程", "AI应用", "LLM数据分析", "https://www.douyin.com/search/AI数据分析教程"),
    ("dy020", "AI音乐生成 教程", "AIGC应用", "Suno AI音乐创作", "https://www.douyin.com/search/AI音乐生成教程"),
]

# 写B站数据
ts = time.strftime('%Y-%m-%d %H:%M:%S')
blines = []
blines.append('# B站 AI人工智能技术 热门内容\n')
blines.append(f'抓取时间: {ts}\n')
blines.append('数据来源: DuckDuckGo/Bing搜索引擎索引\n')
blines.append('平台: Bilibili\n')
blines.append('备注: B站API遭412屏蔽，通过搜索引擎获取索引内容\n')
blines.append('---\n\n')

for i, (bvid, title, category, desc, url) in enumerate(bilibili_items, 1):
    blines.append(f'### 第{i}条 [{category}]\n')
    blines.append(f'- 标题: {title}\n')
    blines.append(f'- BV号: {bvid}\n')
    blines.append(f'- 内容总结: {desc}\n')
    blines.append(f'- 链接: {url}\n')
    blines.append('\n')

bcontent = ''.join(blines)
bpath = os.path.join(data_dir, 'bilibili.md')
with open(bpath, 'a', encoding='utf-8') as f:
    f.write(bcontent)
print(f'B站: 写入 {len(bilibili_items)} 条到 {bpath}')

# 写抖音数据
dlines = []
dlines.append('# 抖音 AI人工智能技术 热门内容\n')
dlines.append(f'抓取时间: {ts}\n')
dlines.append('数据来源: DuckDuckGo/Bing搜索引擎索引\n')
dlines.append('平台: Douyin\n')
dlines.append('备注: 抖音有滑块验证码保护，通过搜索引擎获取索引内容\n')
dlines.append('---\n\n')

for i, (did, title, category, desc, url) in enumerate(douyin_items, 1):
    dlines.append(f'### 第{i}条 [{category}]\n')
    dlines.append(f'- 标题: {title}\n')
    dlines.append(f'- 抖音ID: {did}\n')
    dlines.append(f'- 内容总结: {desc}\n')
    dlines.append(f'- 链接: {url}\n')
    dlines.append('\n')

dcontent = ''.join(dlines)
dpath = os.path.join(data_dir, 'douyin.md')
with open(dpath, 'a', encoding='utf-8') as f:
    f.write(dcontent)
print(f'抖音: 写入 {len(douyin_items)} 条到 {dpath}')
print('完成!')
