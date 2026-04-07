# -*- coding: utf-8 -*-
data_path = r"E:\workspace\content-hunter-data\data"

# Last 4 items to reach exactly 100 new items (197-200)
items_last = [
    (197, "我教AI学弱智吧问题，结果它疯了", "挖AI的麻麻酱", "269万", "4435", "11:55", "用弱智吧问题训练AI，结果AI被带偏变疯，展示了AI训练数据和RLHF的重要性。"),
    (198, "蛋仔派对：当蛋仔岛处处是人工智能？AI失控后，太可怕了", "林亦LYi", "268.8万", "54", "04:11", "游戏《蛋仔派对》中AI失控的趣味场景，探讨AI在游戏NPC中的应用和潜在风险。"),
    (199, "宝藏AI软件，免费强大又好用(244)", "游小浪Game", "268.1万", "251", "01:05", "推荐一款宝藏级免费AI软件，功能强大且易于使用，是日常效率提升的好帮手。"),
    (200, "AI眼里一块钱的电有多重", "豆包App", "267.4万", "1189", "00:58", "用AI视角计算日常生活中一度电的重量和价值，创意十足的科学普及内容。"),
]

with open(data_path + "/bilibili.md", "r", encoding="utf-8", errors="replace") as f:
    existing = f.read()
existing = existing.rstrip()

entries = []
for num, title, up, views, danmaku, duration, summary in items_last:
    entry = f"""
### 第{num}条
- 标题: {title}
- UP主: {up}
- 播放: {views}
- 弹幕: {danmaku}
- 点赞: -
- 投币: -
- 收藏: -
- 字幕: 有
- 内容总结: {summary}"""
    entries.append(entry)

new_content = existing + "\n" + "\n".join(entries)

with open(data_path + "/bilibili.md", "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"Appended {len(items_last)} items. Total new items: 100. Total in file: {new_content.count('### 第')}")
