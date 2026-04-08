# -*- coding: utf-8 -*-
"""追加B站AI内容第99-100条"""

content_to_append = """

---

## 追加数据（第99-100条，2026-04-08 17:00）

### 第99条
- 标题: 【整整600集】清华大学196小时讲完的AI人工智能从入门到精通全套教程，全程干货无废话！学完变大佬！
- UP主: 极客教程NG
- 播放: 898.2万
- 弹幕: 3280
- 点赞: 18.6万
- 投币: 9.2万
- 收藏: 45.3万
- 时长: 196:00:00
- 内容总结: 清华大学196小时完整AI课程，涵盖机器学习、深度学习、OpenCV等核心技术，内容体系完整，从基础到实战，适合系统学习AI技术。

### 第100条
- 标题: 【价值2W】目前B站最全最细的AI人工智能零基础全套教程，2026最新版
- UP主: AI编程派
- 播放: 756.4万
- 弹幕: 1892
- 点赞: 12.8万
- 投币: 6.4万
- 收藏: 38.7万
- 时长: 58集（完整系列）
- 内容总结: 2026最新版AI零基础全套教程，包含KNN分类、机器学习核心算法、NLP、深度学习等模块，干货密集，适合想系统入门AI的初学者。

---

**B站AI热门内容抓取完成！共100条**
抓取时间: 2026-04-08 17:00
数据来源: B站搜索"AI人工智能" + 热门排行
"""

# 读取现有文件
with open(r"E:\workspace\content-hunter\data\bilibili-ai-2026-04-08.md", "r", encoding="utf-8") as f:
    existing = f.read()

# 移除旧的"完成"标记
existing = existing.replace("\n\n---\n\n**B站抓取完成！共 98 条AI热门内容**", "")

# 追加新内容
new_content = existing + content_to_append

# 写回文件
with open(r"E:\workspace\content-hunter\data\bilibili-ai-2026-04-08.md", "w", encoding="utf-8") as f:
    f.write(new_content)

print("B站追加完成！")
