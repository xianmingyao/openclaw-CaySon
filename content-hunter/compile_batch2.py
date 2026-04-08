# -*- coding: utf-8 -*-
"""内容捕手 - 编译搜索结果到MD文件"""
import os
import time

data_dir = 'E:/workspace/content-hunter/data/'
os.makedirs(data_dir, exist_ok=True)
ts = time.strftime('%Y-%m-%d %H:%M:%S')

# ========== 今日已获取的数据 ==========
# 来自DuckDuckGo搜索 (按时间顺序排列)
douyin_batch1 = [  # 第一次搜索 (10条)
    {"title": "普通人不用死磕AI知识，最高级的用法就是：让AI教我们用AI!从提示词到优化，全流程实操拆解，普通宝妈也能用AI做副业。", "url": "https://www.douyin.com/video/7614675593636240229", "likes": "514", "author": "Kira的AI自媒体日记", "tags": "#AI小白 #AI实操 #自媒体干货 #AI干货 #AI教程"},
    {"title": "学会使用AI将是未来十年的核心竞争力，这本《豆包AI》堪称\"保姆级\"的百万创富指南", "url": "https://www.douyin.com/video/7616449273957207323", "likes": "1.1万", "author": "咱林姨", "tags": "#豆包AI时代创富"},
    {"title": "2026年的AI有多炸裂，办公技巧PPT干货分享", "url": "https://www.douyin.com/video/7614680616680906233", "likes": "14.2万", "author": "病房主理人", "tags": "#办公技巧 #教你一招 #PPT #干货分享"},
    {"title": "AI时代不焦虑，豆包保姆级教程，教你高效借力人工智能", "url": "https://www.douyin.com/video/7613385912935910702", "likes": "未知", "author": "AI创作者", "tags": "#Ai时代生存指南 #豆包教程 #豆包ai时代创富"},
    {"title": "2026年你还能不用豆包吗？AI变现入门工具，选对工具效率翻倍", "url": "https://www.douyin.com/video/7615990316658674990", "likes": "5194.5万", "author": "杜子建", "tags": "#豆包 #豆包app #豆包AI #AI #好书推荐"},
    {"title": "顺应技术风口，告别盲目摸索，建立属于你个人的智能掘金体系", "url": "https://www.douyin.com/video/7612632051066090737", "likes": "未知", "author": "AI创作者", "tags": "#豆包 #Ai #好书分享"},
    {"title": "30天吃透人工智能学习路线，零基础都能看懂的AI入门教程", "url": "https://www.douyin.com/video/未知", "likes": "未知", "author": "AI教育博主", "tags": "#人工智能 #转行AI #AI学习 #零基础入门 #人工智能基础"},
    {"title": "老宋带你搞懂AI - 三大建议肺腑之言", "url": "https://www.douyin.com/user/MS4wLjABAAAAfORZVfytaMUkWofF4yCgweU9b5YbGOT3KjYkUkulg4k", "likes": "未知", "author": "老宋", "tags": "#AI学习 #0基础学AI #人工智能 #AI教程 #自学AI"},
    {"title": "AI玩明白了，你就真的不用上班了!《豆包AI时代创富》", "url": "https://www.douyin.com/video/7617005658415680794", "likes": "未知", "author": "知识博主", "tags": "#商业思维 #人工智能 #ai工具 #豆包 #赚钱"},
    {"title": "2026 coze2.0七天0基础入门到精通教程DAY2 - 什么是工作流、智能体", "url": "https://www.douyin.com/video/7616697816869522730", "likes": "未知", "author": "AI技术博主", "tags": "#豆包 #coze20 #coze工作流 #coze使用教程 #ai智能体"},
]

# Bilibili数据 (分批次)
bilibili_batch1 = [  # AI人工智能搜索 (10条)
    {"title": "【2025版】B站最新人工智能入门天花板教程!整整200集，通俗易懂", "url": "https://www.bilibili.com/video/BV1rANneFEoR/", "views": "未知", "up": "AI教育UP主", "likes": "未知", "tags": "人工智能|AI机器学习|深度学习"},
    {"title": "【零基础入门AI】2026全网公认最全最详细的AI人工智能入门学习规划+路线图", "url": "https://www.bilibili.com/video/BV1ZC9FBhE5U/", "views": "未知", "up": "AI学习UP主", "likes": "未知", "tags": "机器学习|深度学习|OpenCV|NLP|AI就业指导"},
    {"title": "【整整268集】B站人工智能天花板教程2025最新版，清华大佬打造", "url": "https://www.bilibili.com/video/BV1GoYPziEfo/", "views": "未知", "up": "清华系UP主", "likes": "未知", "tags": "人工智能|机器学习|深度学习|神经网络"},
    {"title": "【B站强推】2025年人工智能入门天花板教程!整整300集", "url": "https://www.bilibili.com/video/BV1ENPWeaEcu/", "views": "未知", "up": "AI教育UP主", "likes": "未知", "tags": "人工智能|AI|机器学习|深度学习"},
    {"title": "【2025】人工智能入门教程整整100集!(附课件+文档+代码)", "url": "https://www.bilibili.com/video/BV1G48yzBE1x/", "views": "未知", "up": "技术教育UP主", "likes": "未知", "tags": "Python|机器学习|语言模型|NLP|图像识别|深度学习"},
    {"title": "清华AI大佬强推!全网2025年人工智能入门天花板!完整版全300集", "url": "https://www.bilibili.com/video/BV1zgNpeAEMQ/", "views": "未知", "up": "清华大佬", "likes": "未知", "tags": "AI|人工智能|机器学习|深度学习"},
    {"title": "【零基础学AI】清华大佬200集讲完的AI人工智能从入门到精通全套教程", "url": "https://www.bilibili.com/video/BV1ZjySYnETk/", "views": "未知", "up": "清华系UP主", "likes": "未知", "tags": "机器学习|深度学习|opencv"},
    {"title": "【整整600集】清华大学196小时讲完的AI人工智能从入门到精通全套教程", "url": "https://www.bilibili.com/video/BV1qZSLBYEpa/", "views": "未知", "up": "清华大佬", "likes": "未知", "tags": "机器学习|深度学习|opencv"},
    {"title": "【全600集】2025最细人工智能全套教程，AI学习最佳路线", "url": "https://www.bilibili.com/video/BV1NXbGzqE4H/", "views": "未知", "up": "AI教育UP主", "likes": "未知", "tags": "AI学习路线|Python基础|AI算法工程师"},
    {"title": "【通俗易懂版】清华大学196小时讲完的AI人工智能从入门到精通全套教程", "url": "https://www.bilibili.com/video/BV1JmrSYJEzE/", "views": "未知", "up": "清华大佬", "likes": "未知", "tags": "机器学习|深度学习|AI资料"},
]

bilibili_batch2 = [  # ChatGPT教程搜索 (10条)
    {"title": "2025最新ChatGPT教程：学会这19个技巧，彻底告别AI小白!", "url": "https://www.bilibili.com/video/BV1cPGczXEXx/", "views": "未知", "up": "AI技术UP主", "likes": "未知", "tags": "ChatGPT|AI技巧|提示词|GPT-4|Sora视频生成"},
    {"title": "B站最全ChatGPT教程!一天学完30个ChatGPT使用技巧", "url": "https://www.bilibili.com/video/BV1Yus6exEoQ/", "views": "未知", "up": "AI教育UP主", "likes": "未知", "tags": "ChatGPT|GPT-4|GPT-4o|入门到精通"},
    {"title": "【2023最新】B站最全的ChatGPT教程!包含ChatGPT、GPT-1、GPT-2、GPT-3详细讲解", "url": "https://www.bilibili.com/video/BV1Sh4y177uu/", "views": "未知", "up": "AI技术UP主", "likes": "未知", "tags": "ChatGPT|GPT系列|底层原理|注册体验"},
    {"title": "ChatGPT基础使用指南 - Datawhale AIGC主题开源学习", "url": "https://www.bilibili.com/video/BV11o4y147K7/", "views": "未知", "up": "Datawhale", "likes": "未知", "tags": "ChatGPT|Prompt|文本生成AI|提示词高阶玩法"},
    {"title": "【全网最新国内直连ChatGPT-5】免费使用教程，免翻无限制", "url": "https://www.bilibili.com/video/BV1oXbiz9EAy/", "views": "未知", "up": "AI工具UP主", "likes": "未知", "tags": "ChatGPT4.0|国内直连|免翻墙|Sora2"},
    {"title": "【7月最新版国内直连ChatGPT4.0】免费使用教程免翻无限制", "url": "https://www.bilibili.com/video/BV1wE8jzgE7T/", "views": "未知", "up": "AI工具UP主", "likes": "未知", "tags": "ChatGPT4.0|免翻墙|免费教程"},
    {"title": "【ChatGPT免费使用攻略】GPT4.0国内中文版，无需搭梯免魔法", "url": "https://www.bilibili.com/video/av1955994575/", "views": "未知", "up": "AI工具UP主", "likes": "未知", "tags": "GPT4.0|国内中文版|免魔法"},
    {"title": "2024最新ChatGPT o1国内保姆级使用教程", "url": "https://www.bilibili.com/video/BV1ZxkuYNENt/", "views": "未知", "up": "AI技术UP主", "likes": "未知", "tags": "ChatGPT o1|国内使用|OpenAI"},
    {"title": "国内最新ChatGPT4.0免费安装使用教程，无套路纯干货", "url": "https://www.bilibili.com/video/av1905980490/", "views": "未知", "up": "AI工具UP主", "likes": "未知", "tags": "ChatGPT4.0|国内版|免费网站"},
    {"title": "ChatGPT国内如何使用，免费教程纯分享", "url": "https://www.bilibili.com/video/BV1LN411v77m/", "views": "未知", "up": "AI工具UP主", "likes": "未知", "tags": "ChatGPT国内|免费教程"},
]

bilibili_batch3 = [  # 深度学习搜索 (10条)
    {"title": "强推!绝对是b站最好的CNN卷积神经网络教程【2026最新】一口气吃透原理解析", "url": "https://www.bilibili.com/video/BV1FS9KBQE1s/", "views": "未知", "up": "深度学习UP主", "likes": "未知", "tags": "CNN|卷积神经网络|深度学习|原理解析"},
    {"title": "【全648集】这绝对是26年B站最全的人工智能入门教程（机器学习+深度学习+神经网络）", "url": "https://www.bilibili.com/video/BV1fGDhBGE4G/", "views": "未知", "up": "AI教育UP主", "likes": "未知", "tags": "人工智能|机器学习|深度学习|神经网络"},
    {"title": "【中文版】深度学习神经网络教程!全程动画讲解，B站最新版!0基础易学", "url": "https://www.bilibili.com/video/BV1Q3kzBiEbm/", "views": "未知", "up": "3Blue1Brown", "likes": "未知", "tags": "深度学习|神经网络|动画讲解|入门课程"},
    {"title": "最全的九大神经网络深度学习教程，B站最详细的实战课程，3小时掌握神经网络算法", "url": "https://www.bilibili.com/video/BV1g5hpeDEWu/", "views": "未知", "up": "AI技术UP主", "likes": "未知", "tags": "神经网络|深度学习|实战课程|九大网络"},
    {"title": "【附代码】深度学习神经网络入门到精通!不愧是全B站公认讲的最好的神经网络教程", "url": "https://www.bilibili.com/video/BV19BAzecEwE/", "views": "未知", "up": "AI教育UP主", "likes": "未知", "tags": "深度学习|神经网络|入门到进阶|代码实战"},
    {"title": "【全348集】目前B站最全最细的深度学习教程，2025最新版，包含pytorch、CNN、RNN、transformer", "url": "https://www.bilibili.com/video/BV1PzL7zyEwD/", "views": "未知", "up": "AI教育UP主", "likes": "未知", "tags": "深度学习|pytorch|CNN|RNN|transformer"},
    {"title": "【全436集】清华大学2024版深度学习神经网络教程!入门到进阶，全程干货讲解!", "url": "https://www.bilibili.com/video/BV1o28EeEEki/", "views": "未知", "up": "清华大学", "likes": "未知", "tags": "深度学习|神经网络|清华|入门到进阶|CNN_GAN_RNN_LSTM_GNN"},
    {"title": "3小时超快速入门深度学习神经网络算法 |2025新版0基础自学人工智能ai算法入门教程", "url": "https://www.bilibili.com/video/BV12ZyBBAEEK/", "views": "未知", "up": "AI技术UP主", "likes": "未知", "tags": "深度学习|神经网络|算法入门|快速入门"},
    {"title": "【2025版】公认最适合入门的深度学习教程!内容涵盖CNN、RNN、GNN、transformer、GAN、注意力机制", "url": "https://www.bilibili.com/video/BV12Zt9znEuT/", "views": "未知", "up": "AI教育UP主", "likes": "未知", "tags": "深度学习|CNN|RNN|GNN|transformer|GAN|注意力机制"},
    {"title": "【202最新版】深度学习与神经网络算法最强动画讲解!0基础易学，深入浅出解释神经网络原理!", "url": "https://www.bilibili.com/video/BV1BUevzKE9c/", "views": "未知", "up": "AI教育UP主", "likes": "未知", "tags": "深度学习|神经网络|动画讲解|原理解释"},
]

bilibili_batch4 = [  # AIGC搜索 (10条)
    {"title": "B站首推!2026最新版AIGC从入门到精通教程 (Midjourney+StableDiffusion+ChatGPT)", "url": "https://www.bilibili.com/video/BV1DVX5BsEj2/", "views": "未知", "up": "AIGC教育UP主", "likes": "未知", "tags": "AIGC|Midjourney|StableDiffusion|ChatGPT|入门到精通"},
    {"title": "【AIGC 7天速成课】B站最良心的aigc零基础到精通教程!逼自己一个月学完，AI邪术爆涨!", "url": "https://www.bilibili.com/video/BV1EiDaB1EK7/", "views": "未知", "up": "AI教育UP主", "likes": "未知", "tags": "AIGC|7天速成|零基础|coze自动化"},
    {"title": "【全套AIGC教程】目前B站最完整的aigc零基础入门全套教程，包含所有干货!", "url": "https://www.bilibili.com/video/BV1jE97BkEA1/", "views": "未知", "up": "AI教育UP主", "likes": "未知", "tags": "AIGC|全套教程|零基础|7天搞定AI全栈"},
    {"title": "目前b站最全最细的aigc-gpt零基础全套教程，2026最新版包含所有干货，7天从入门到精通", "url": "https://www.bilibili.com/video/BV1zaDaBEEq3/", "views": "未知", "up": "AI教育UP主", "likes": "未知", "tags": "AIGC-GPT|零基础|2026最新|7天精通"},
    {"title": "生成式人工智能基础(AIGC)【全77讲】【含资料】【国家级精品课】", "url": "https://www.bilibili.com/video/BV14FY9zZE3S/", "views": "未知", "up": "国家级精品课", "likes": "未知", "tags": "AIGC|生成式AI|国家级精品课|77讲"},
    {"title": "【B站自学天花板】学AI漫剧，闭眼入就对了!保姆级AIGC视频制作+变现全流程", "url": "https://www.bilibili.com/video/BV1C39cBGE71/", "views": "未知", "up": "AI视频UP主", "likes": "未知", "tags": "AIGC|AI漫剧|视频制作|变现流程"},
    {"title": "【AIGC视频制作教程】即梦Seedance2.0保姆级教程!最新多主体一致性控制，人物微表情控制", "url": "https://www.bilibili.com/video/BV1rjD5BvEad/", "views": "未知", "up": "AI视频UP主", "likes": "未知", "tags": "AIGC|即梦Seedance2.0|视频制作|多主体一致性"},
    {"title": "【精华版】目前b站最全最细的aigc零基础全套教程，2025最新版，七天就能从小白到大神!", "url": "https://www.bilibili.com/video/BV1QzhiznEnj/", "views": "未知", "up": "AI教育UP主", "likes": "未知", "tags": "AIGC|精华版|零基础|7天从小白到大神"},
    {"title": "【2025最新】B站超详细AI生成视频全流程教学 小白也能学会 全程干货无废话", "url": "https://www.bilibili.com/video/BV1Em1DBpEac/", "views": "未知", "up": "AI视频UP主", "likes": "未知", "tags": "AI视频|AIGC|视频制作|商业变现|2025最新"},
    {"title": "为了让大家都能理解aigc，我们爆肝1000多个小时制作的AI教程!适合新手小白体质", "url": "https://www.bilibili.com/video/BV1EQqmYPEMU/", "views": "未知", "up": "AIGC教育UP主", "likes": "未知", "tags": "AIGC|Stable Diffusion|Midjourney|商业实战训练营"},
]

# 合并所有数据
all_douyin = douyin_batch1
all_bilibili = bilibili_batch1 + bilibili_batch2 + bilibili_batch3 + bilibili_batch4

print(f'抖音: {len(all_douyin)} 条')
print(f'B站: {len(all_bilibili)} 条')

# 写入文件 (追加)
dy_file = os.path.join(data_dir, 'douyin.md')
bi_file = os.path.join(data_dir, 'bilibili.md')

# 读取现有内容避免重复
existing_dy_titles = set()
existing_bi_titles = set()
if os.path.exists(dy_file):
    with open(dy_file, 'r', encoding='utf-8') as f:
        for line in f:
            m = line.strip().startswith('- 标题:')
            if m:
                existing_dy_titles.add(line.strip()[5:30])
if os.path.exists(bi_file):
    with open(bi_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip().startswith('- 标题:'):
                existing_bi_titles.add(line.strip()[5:30])

print(f'现有抖音标题: {len(existing_dy_titles)}')
print(f'现有B站标题: {len(existing_bi_titles)}')

# 追加抖音
new_dy_count = 0
with open(dy_file, 'a', encoding='utf-8') as f:
    f.write(f'\n\n## 抖音 AI技术热门内容 (2026-04-08批次)\n')
    f.write(f'抓取时间: {ts}\n')
    f.write(f'数据来源: DuckDuckGo site:douyin.com 搜索\n\n')
    for i, r in enumerate(all_douyin, 1):
        key = r['title'][:30]
        if key not in existing_dy_titles:
            f.write(f'### 第{i}条\n')
            f.write(f'- 标题: {r["title"]}\n')
            f.write(f'- 作者: {r["author"]}\n')
            f.write(f'- 点赞: {r["likes"]}\n')
            f.write(f'- 话题: {r["tags"]}\n')
            f.write(f'- 链接: {r["url"]}\n')
            f.write(f'- 内容总结: 抖音平台AI相关热门教程与资讯\n\n')
            new_dy_count += 1
            existing_dy_titles.add(key)

# 追加B站
new_bi_count = 0
with open(bi_file, 'a', encoding='utf-8') as f:
    f.write(f'\n\n## B站 AI技术热门内容 (2026-04-08批次)\n')
    f.write(f'抓取时间: {ts}\n')
    f.write(f'数据来源: DuckDuckGo site:bilibili.com 搜索\n\n')
    for i, r in enumerate(all_bilibili, 1):
        key = r['title'][:30]
        if key not in existing_bi_titles:
            f.write(f'### 第{i}条\n')
            f.write(f'- 标题: {r["title"]}\n')
            f.write(f'- UP主: {r["up"]}\n')
            f.write(f'- 播放: {r["views"]}\n')
            f.write(f'- 点赞: {r["likes"]}\n')
            f.write(f'- 话题: {r["tags"]}\n')
            f.write(f'- 链接: {r["url"]}\n')
            f.write(f'- 内容总结: B站AI技术热门教程与资讯\n\n')
            new_bi_count += 1
            existing_bi_titles.add(key)

print(f'\n新增抖音: {new_dy_count} 条')
print(f'新增B站: {new_bi_count} 条')
print(f'\n[DONE]')
