# Karpathy 风格知识库 - 指令文件 (CLOD.md)

## 目录结构

```
knowledge-base/
├── raw/                    # 原始资料（不修改）
│   ├── papers/            # 论文
│   ├── articles/          # 文章
│   ├── github/            # GitHub 代码
│   ├── datasets/          # 数据集
│   └── screenshots/       # 截图
├── wiki/                  # 编译后的知识库（可查看/查询）
│   ├── concepts/          # 概念文章
│   ├── topics/            # 主题分类
│   └── index.md           # 索引
├── altpus/                # AI 答案报告
│   └── reports/           # 查询报告
└── CLOD.md               # 本文件（指令）
```

## 工作流三步曲

### STEP 01: 收集 (Collect)
- 使用 Obsidian Web Clipper 将网页保存为 .md
- 保存到 `raw/` 对应目录
- 不修改原始内容

### STEP 02: 编译 (Compile)
运行编译脚本：
```bash
python compile.py
```
- LLM 读取 `raw/` 所有文件
- 提取核心概念
- 生成结构化 wiki 文章
- 建立双向链接
- 输出到 `wiki/` 目录

### STEP 03: 查询 (Query)
- 直接向 LLM 提问
- LLM 在 wiki/ 中查找答案
- 好答案归档回 wiki

## 编译规则

1. **概念提取**: 从每个 raw 文件中提取 3-5 个核心概念
2. **文章生成**: 每个概念生成一篇简短 wiki 文章
3. **双向链接**: 相关概念之间添加 `[[链接]]`
4. **分类整理**: 按主题归类到 topics/ 目录
5. **质量优先**: 宁可少而精，不要多而杂

## 同步规则

- **飞书**: 每周同步 wiki 到飞书云文档
- **Notion**: 每周同步 wiki 到 Notion
- **记忆**: 每日将新概念上传到云端 Milvus

## 命令

```bash
# 编译 raw → wiki
python compile.py

# 同步到飞书
python sync_feishu.py

# 同步到 Notion
python sync_notion.py

# 上传到云端记忆
python upload_mem0.py

# 全量同步（编译+飞书+Notion+记忆）
python sync_all.py
```
