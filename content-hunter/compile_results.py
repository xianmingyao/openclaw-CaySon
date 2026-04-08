# -*- coding: utf-8 -*-
"""内容捕手结果编译脚本 - 基于DuckDuckGo搜索结果"""
import os
import time

data_dir = 'E:/workspace/content-hunter/data/'
os.makedirs(data_dir, exist_ok=True)

timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

# ========== 抖音数据 (来自DuckDuckGo搜索) ==========
douyin_data = [
    {
        "title": "普通人不用死磕AI知识，最高级的用法就是：让AI教我们用AI!从提示词到优化，全流程实操拆解，普通宝妈也能用AI做副业。",
        "url": "https://www.douyin.com/video/7614675593636240229",
        "likes": "514",
        "author": "Kira的AI自媒体日记",
        "tags": "AI小白 #AI实操 #自媒体干货 #AI干货 #AI教程",
        "summary": "AI实操教程，介绍如何利用AI工具做副业，从提示词到优化的全流程拆解"
    },
    {
        "title": "学会使用AI将是未来十年的核心竞争力，这本《豆包AI》堪称\"保姆级\"的百万创富指南",
        "url": "https://www.douyin.com/video/7616449273957207323",
        "likes": "1.1万",
        "author": "咱林姨",
        "tags": "豆包AI时代创富",
        "summary": "AI时代竞争力分析，豆包AI工具的创富方法论"
    },
    {
        "title": "2026年的AI有多炸裂，办公技巧，教你一招，PPT干货分享",
        "url": "https://www.douyin.com/video/7614680616680906233",
        "likes": "14.2万",
        "author": "病房主理人",
        "tags": "办公技巧 #教你一招 #PPT #干货分享",
        "summary": "2026年AI办公工具最新技巧，PPT制作效率提升方法"
    },
    {
        "title": "AI时代不焦虑，豆包保姆级教程，教你高效借力人工智能",
        "url": "https://www.douyin.com/video/7613385912935910702",
        "likes": "未知",
        "author": "未知",
        "tags": "Ai时代生存指南 #豆包教程 #豆包ai时代创富",
        "summary": "豆包AI工具保姆级教程，AI时代生存指南"
    },
    {
        "title": "2026年你还能不用豆包吗？AI变现入门工具，选对工具效率翻倍",
        "url": "https://www.douyin.com/video/7615990316658674990",
        "likes": "5194.5万",
        "author": "杜子建",
        "tags": "豆包 #豆包app #豆包AI #AI #好书推荐",
        "summary": "豆包AI变现入门指南，AI工具选择与效率提升"
    },
    {
        "title": "顺应技术风口，告别盲目摸索，建立属于你个人的智能掘金体系",
        "url": "https://www.douyin.com/video/7612632051066090737",
        "likes": "未知",
        "author": "未知",
        "tags": "豆包 #Ai #好书分享",
        "summary": "AI时代个人智能掘金体系建立方法论"
    },
    {
        "title": "30天吃透人工智能学习路线，零基础都能看懂的AI入门教程",
        "url": "https://www.douyin.com/video/未知",
        "likes": "未知",
        "author": "未知",
        "tags": "人工智能 #转行AI #AI学习 #零基础入门 #人工智能基础",
        "summary": "30天AI学习路线规划，零基础入门人工智能"
    },
    {
        "title": "老宋带你搞懂AI - 三大建议肺腑之言",
        "url": "https://www.douyin.com/user/MS4wLjABAAAAfORZVfytaMUkWofF4yCgweU9b5YbGOT3KjYkUkulg4k",
        "likes": "未知",
        "author": "老宋",
        "tags": "AI学习 #0基础学AI #人工智能 #AI教程 #自学AI",
        "summary": "AI学习三大建议，0基础学AI的肺腑之言"
    },
    {
        "title": "AI玩明白了，你就真的不用上班了!《豆包AI时代创富》",
        "url": "https://www.douyin.com/video/7617005658415680794",
        "likes": "未知",
        "author": "未知",
        "tags": "商业思维 #人工智能 #ai工具 #豆包 #赚钱",
        "summary": "AI时代创富指南，豆包AI的财富破局路径"
    },
    {
        "title": "2026 coze2.0七天0基础入门到精通教程DAY2 - 什么是工作流、智能体",
        "url": "https://www.douyin.com/video/7616697816869522730",
        "likes": "未知",
        "author": "未知",
        "tags": "豆包 #coze20 #coze工作流 #coze使用教程 #ai智能体",
        "summary": "Coze2.0工作流与智能体入门教程，AI工作流自动化"
    },
]

# ========== B站数据 ==========
bilibili_data = [
    # AI人工智能搜索结果
    {
        "title": "【2025版】B站最新人工智能入门天花板教程!整整200集，通俗易懂",
        "url": "https://www.bilibili.com/video/BV1rANneFEoR/",
        "views": "未知",
        "up": "未知",
        "likes": "未知",
        "tags": "人工智能|AI机器学习|深度学习",
        "summary": "B站最全面的人工智能入门教程，200集系统性讲解AI/机器学习/深度学习"
    },
    {
        "title": "【零基础入门AI】2026全网公认最全最详细的AI人工智能入门学习规划+路线图",
        "url": "https://www.bilibili.com/video/BV1ZC9FBhE5U/",
        "views": "未知",
        "up": "未知",
        "likes": "未知",
        "tags": "机器学习|深度学习|OpenCV|NLP|AI就业指导",
        "summary": "2026年AI入门学习路线图规划，零基础到就业的完整路径"
    },
    {
        "title": "【整整268集】B站人工智能天花板教程2025最新版，清华大佬打造",
        "url": "https://www.bilibili.com/video/BV1GoYPziEfo/",
        "views": "未知",
        "up": "未知",
        "likes": "未知",
        "tags": "人工智能|机器学习|深度学习|神经网络",
        "summary": "清华大佬出品的268集AI教程，从入门到进阶的保姆级内容"
    },
    {
        "title": "【B站强推】2025年人工智能入门天花板教程!整整300集",
        "url": "https://www.bilibili.com/video/BV1ENPWeaEcu/",
        "views": "未知",
        "up": "未知",
        "likes": "未知",
        "tags": "人工智能|AI|机器学习|深度学习",
        "summary": "B站强推的300集AI入门教程，通俗易懂全程干货"
    },
    {
        "title": "【2025】人工智能入门教程整整100集!(附课件+文档+代码)",
        "url": "https://www.bilibili.com/video/BV1G48yzBE1x/",
        "views": "未知",
        "up": "未知",
        "likes": "未知",
        "tags": "Python|机器学习|语言模型|NLP|图像识别|深度学习",
        "summary": "100集AI入门教程，附全套课件文档代码，自学AI必备"
    },
    {
        "title": "清华AI大佬强推!全网2025年人工智能入门天花板!完整版全300集",
        "url": "https://www.bilibili.com/video/BV1zgNpeAEMQ/",
        "views": "未知",
        "up": "未知",
        "likes": "未知",
        "tags": "AI|人工智能|机器学习|深度学习",
        "summary": "清华大学AI大佬出品的300集AI入门教程，草履虫都能学会"
    },
    {
        "title": "【零基础学AI】清华大佬200集讲完的AI人工智能从入门到精通全套教程",
        "url": "https://www.bilibili.com/video/BV1ZjySYnETk/",
        "views": "未知",
        "up": "未知",
        "likes": "未知",
        "tags": "机器学习|深度学习|opencv",
        "summary": "清华大佬200集讲完的AI全套教程，零基础到精通"
    },
    {
        "title": "【整整600集】清华大学196小时讲完的AI人工智能从入门到精通全套教程",
        "url": "https://www.bilibili.com/video/BV1qZSLBYEpa/",
        "views": "未知",
        "up": "未知",
        "likes": "未知",
        "tags": "机器学习|深度学习|opencv",
        "summary": "清华大学196小时AI全套教程，600集超完整内容"
    },
    {
        "title": "【全600集】2025最细人工智能全套教程，AI学习最佳路线",
        "url": "https://www.bilibili.com/video/BV1NXbGzqE4H/",
        "views": "未知",
        "up": "未知",
        "likes": "未知",
        "tags": "AI学习路线|Python基础|AI算法工程师",
        "summary": "600集最细AI全套教程，从0基础到AI算法工程师完整路径"
    },
    {
        "title": "【通俗易懂版】清华大学196小时讲完的AI人工智能从入门到精通全套教程",
        "url": "https://www.bilibili.com/video/BV1JmrSYJEzE/",
        "views": "未知",
        "up": "未知",
        "likes": "未知",
        "tags": "机器学习|深度学习|AI资料",
        "summary": "通俗易懂版清华AI教程，含西瓜书、花书等经典AI资料"
    },
    # ChatGPT教程搜索结果
    {
        "title": "2025最新ChatGPT教程：学会这19个技巧，彻底告别AI小白!",
        "url": "https://www.bilibili.com/video/BV1cPGczXEXx/",
        "views": "未知",
        "up": "未知",
        "likes": "未知",
        "tags": "ChatGPT|AI技巧|提示词|GPT-4|Sora视频生成",
        "summary": "19个ChatGPT核心技巧，从匿名聊天到深度研究的全面指南"
    },
    {
        "title": "B站最全ChatGPT教程!一天学完30个ChatGPT使用技巧",
        "url": "https://www.bilibili.com/video/BV1Yus6exEoQ/",
        "views": "未知",
        "up": "未知",
        "likes": "未知",
        "tags": "ChatGPT|GPT-4|GPT-4o|入门到精通",
        "summary": "B站最全ChatGPT教程，30个使用技巧一天学完"
    },
    {
        "title": "【2023最新】B站最全的ChatGPT教程!包含ChatGPT、GPT-1、GPT-2、GPT-3详细讲解",
        "url": "https://www.bilibili.com/video/BV1Sh4y177uu/",
        "views": "未知",
        "up": "未知",
        "likes": "未知",
        "tags": "ChatGPT|GPT系列|底层原理|注册体验",
        "summary": "GPT系列算法与实战教程，从GPT-1到GPT-3的完整讲解"
    },
    {
        "title": "ChatGPT基础使用指南 - Datawhale AIGC主题开源学习",
        "url": "https://www.bilibili.com/video/BV11o4y147K7/",
        "views": "未知",
        "up": "Datawhale",
        "likes": "未知",
        "tags": "ChatGPT|Prompt|文本生成AI|提示词高阶玩法",
        "summary": "Datawhale开源ChatGPT基础使用指南，Prompt高阶玩法"
    },
    {
        "title": "【全网最新国内直连ChatGPT-5】免费使用教程，免翻无限制",
        "url": "https://www.bilibili.com/video/BV1oXbiz9EAy/",
        "views": "未知",
        "up": "未知",
        "likes": "未知",
        "tags": "ChatGPT4.0|国内直连|免翻墙|Sora2",
        "summary": "国内直连ChatGPT-5免费使用教程，无需翻墙无限制使用"
    },
    {
        "title": "【7月最新版国内直连ChatGPT4.0】免费使用教程免翻无限制",
        "url": "https://www.bilibili.com/video/BV1wE8jzgE7T/",
        "views": "未知",
        "up": "未知",
        "likes": "未知",
        "tags": "ChatGPT4.0|免翻墙|免费教程",
        "summary": "最新版国内直连ChatGPT4.0免费教程，免翻墙无限制"
    },
    {
        "title": "【ChatGPT免费使用攻略】GPT4.0国内中文版，无需搭梯免魔法",
        "url": "https://www.bilibili.com/video/av1955994575/",
        "views": "未知",
        "up": "未知",
        "likes": "未知",
        "tags": "GPT4.0|国内中文版|免魔法",
        "summary": "GPT4.0国内中文版免费使用攻略，无需翻墙"
    },
    {
        "title": "2024最新ChatGPT o1国内保姆级使用教程",
        "url": "https://www.bilibili.com/video/BV1ZxkuYNENt/",
        "views": "未知",
        "up": "未知",
        "likes": "未知",
        "tags": "ChatGPT o1|国内使用|OpenAI",
        "summary": "ChatGPT o1国内使用教程，100%能搭建成功"
    },
    {
        "title": "国内最新ChatGPT4.0免费安装使用教程，无套路纯干货",
        "url": "https://www.bilibili.com/video/av1905980490/",
        "views": "未知",
        "up": "未知",
        "likes": "未知",
        "tags": "ChatGPT4.0|国内版|免费网站",
        "summary": "国内版ChatGPT4.0免费安装教程，纯干货分享"
    },
    {
        "title": "ChatGPT国内如何使用，免费教程纯分享",
        "url": "https://www.bilibili.com/video/BV1LN411v77m/",
        "views": "未知",
        "up": "未知",
        "likes": "未知",
        "tags": "ChatGPT国内|免费教程",
        "summary": "ChatGPT国内使用方法，免费教程分享"
    },
]

# ========== 写入抖音文件 ==========
douyin_file = os.path.join(data_dir, 'douyin.md')
with open(douyin_file, 'a', encoding='utf-8') as f:
    f.write(f'\n\n## 抖音 AI技术热门内容\n')
    f.write(f'抓取时间: {timestamp}\n')
    f.write(f'数据来源: DuckDuckGo site:douyin.com 搜索\n\n')
    for i, r in enumerate(douyin_data, 1):
        f.write(f'### 第{i}条\n')
        f.write(f'- 标题: {r["title"]}\n')
        f.write(f'- 作者: {r["author"]}\n')
        f.write(f'- 点赞: {r["likes"]}\n')
        f.write(f'- 话题: {r["tags"]}\n')
        f.write(f'- 链接: {r["url"]}\n')
        f.write(f'- 内容总结: {r["summary"]}\n\n')

# ========== 写入B站文件 ==========
bilibili_file = os.path.join(data_dir, 'bilibili.md')
with open(bilibili_file, 'a', encoding='utf-8') as f:
    f.write(f'\n\n## B站 AI技术热门内容\n')
    f.write(f'抓取时间: {timestamp}\n')
    f.write(f'数据来源: DuckDuckGo site:bilibili.com 搜索\n\n')
    for i, r in enumerate(bilibili_data, 1):
        f.write(f'### 第{i}条\n')
        f.write(f'- 标题: {r["title"]}\n')
        f.write(f'- UP主: {r["up"]}\n')
        f.write(f'- 播放: {r["views"]}\n')
        f.write(f'- 点赞: {r["likes"]}\n')
        f.write(f'- 话题: {r["tags"]}\n')
        f.write(f'- 链接: {r["url"]}\n')
        f.write(f'- 内容总结: {r["summary"]}\n\n')

print(f'[DONE] 抖音: {len(douyin_data)} 条 -> {douyin_file}')
print(f'[DONE] B站: {len(bilibili_data)} 条 -> {bilibili_file}')
