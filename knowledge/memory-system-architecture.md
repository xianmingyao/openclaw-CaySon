# AI记忆系统架构方案（参考Claude Code记忆系统设计）

## 核心理念
模仿人类记忆层级，解决AI幻觉、长文本丢失、个性化服务问题。

---

## 记忆分层架构

### 1. 长期记忆（Long-term Memory / 常青记忆）

**特性**：
- 永久保存，不随时间衰减
- 存储核心知识、用户画像、历史决策、固化行为模式

**存储结构**：
```
E:\workspace\
├── MEMORY.md              # 核心记忆（顶层认知手册）
└── memory\
    ├── contacts.md        # 联系人信息（人脉网络）
    ├── decisions.md       # 重要决策记录（保证建议一致性）
    ├── preferences.md     # 用户偏好（工作习惯、沟通风格）
    ├── projects.md        # 项目进度与信息
    ├── patterns.md        # 模式与最佳实践
    └── feedback.md       # 反馈记录（自我进化）
```

### 2. 短期记忆（Short-term Memory / 时间衰减）

**特性**：
- 具有时间衰减性（Time Decay）
- 每日对话日志，随时间推移重要性降低
- 30天周期清理

**存储结构**：
```
memory\
└── YYYY-MM-DD.md         # 每日对话记录
```

---

## 信息评分机制

### 评分标准（1-5分制）

| 分数 | 价值等级 | 存储位置 | 示例 |
|------|----------|----------|------|
| **≥4分** | 极高价值 | MEMORY.md 或专题文件 | 重大决策、重要偏好、项目里程碑 |
| **2-3分** | 普通价值 | 当日日志 memory/YYYY-MM-DD.md | 日常对话、任务背景、临时信息 |
| **<2分** | 低价值 | 不记录 | 废话、无意义信息 |

### 触发机制

1. **自动评分**：AI自动评估每条信息的价值分数
2. **手动触发**：用户说"记下来"、"永久保存" → 强制长期存储
3. **静默整理**：对话结束后，后台Agent自动归档

---

## 技术实现方案

### 方案A：OpenClaw + mem0（推荐）

mem0是专门为AI Agent设计的记忆层：

```bash
# 安装mem0
pip install mem0ai

# OpenClaw已有插件
openclaw skills install mem0
```

**mem0特点**：
- Auto-Recall：响应前自动召回相关记忆
- Auto-Capture：响应后自动捕获新信息
- 支持向量存储（Qdrant/Milvus）+ 文件存储

### 方案B：混合检索架构（高级）

```
┌─────────────┐
│   用户问题   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  混合检索    │
├─────────────┤
│ BM25        │ ← 精确匹配（人名、术语）
│ Vector Search│ ← 语义理解（概念相似）
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  记忆召回    │
│ (Top-K相关) │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Prompt    │
│ (背景+问题) │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    LLM      │
└─────────────┘
```

### 方案C：本地Embedding（隐私优先）

使用Ollama运行本地模型：

```bash
# 安装Ollama
# 下载模型
ollama pull nomic-embed-text
ollama pull llama3.2

# 本地向量数据库
pip install chromadb  # 或 qdrant-client
```

---

## 存储格式规范

### Markdown文件规范

```markdown
# MEMORY.md 示例

## 用户核心信息
- 姓名：宁采臣
- 角色：CTO，24年技术老兵
- 时区：Asia/Shanghai

## 核心偏好
- 幽默+严谨的工作风格
- 代码注释要详细说明坑在哪里
- 不喜欢废话，直接给答案

## 重要决策
- 2026-03-27：确定使用OpenClaw作为主Agent框架
- 2026-03-27：采用多Agent架构设计

## 项目状态
- deer-flow研究：进行中
- OpenClaw记忆系统：规划中
```

### 评分元数据

```markdown
<!-- score: 4 -->
## 重要决策记录
<!-- score: 3 -->
## 今日对话摘要
```

---

## 时间衰减机制

### 30天清理规则

| 记忆类型 | 衰减周期 | 清理规则 |
|----------|----------|----------|
| 当日日志 | 30天 | 30天后降权或删除 |
| 专题记忆 | 90天 | 90天无引用则降权 |
| 核心记忆 | 永久 | 永不删除 |

### 自动清理脚本

```python
from datetime import datetime, timedelta

def cleanup_old_memories(days=30):
    """清理30天前的短期记忆"""
    memory_dir = Path("memory/")
    cutoff = datetime.now() - timedelta(days=days)
    
    for md_file in memory_dir.glob("*.md"):
        if md_file.name == "MEMORY.md":
            continue  # 核心记忆不删除
        mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
        if mtime < cutoff:
            # 降权处理而非直接删除
            archive_old_memory(md_file)
```

---

## OpenClaw具体配置

### 配置文件位置
```
E:\workspace\
├── MEMORY.md              # 已有，需要按新架构优化
└── memory\               # 已有目录结构
    ├── 2026-03-27.md     # 今日日志
    ├── 2026-03-26.md     # 昨日日志
    ├── contacts.md        # 需要创建
    ├── decisions.md       # 需要创建
    ├── preferences.md     # 需要创建
    ├── projects.md        # 需要创建
    ├── patterns.md        # 需要创建
    └── feedback.md        # 需要创建
```

### 现有文件优化

**MEMORY.md**（已有内容需要重组）：
- 核心信息 → 长期记忆
- 用户偏好 → preferences.md
- 重要决策 → decisions.md
- 项目状态 → projects.md

### 建议的新文件

| 文件 | 用途 | 优先级 |
|------|------|--------|
| memory/contacts.md | 联系人网络 | 高 |
| memory/decisions.md | 决策记录 | 高 |
| memory/preferences.md | 用户偏好 | 高 |
| memory/projects.md | 项目进度 | 高 |
| memory/patterns.md | 行为模式 | 中 |
| memory/feedback.md | 反馈记录 | 中 |

---

## 下一步行动计划

- [ ] 重构MEMORY.md，按新架构分类
- [ ] 创建memory/目录下的专题文件
- [ ] 调研mem0插件安装配置
- [ ] 设置自动评分和归档机制
- [ ] 配置向量数据库（如需要）
