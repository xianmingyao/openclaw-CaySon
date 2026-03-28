# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## 📝 宁兄笔记格式规范（铁律）

> 必须按照 `knowledge\note-format-rules.md` 的格式书写！

### 核心格式要素：
- ✅/🔴 Emoji图标区分正负面
- 加粗标题 + 扁平化模块设计
- **代码块必须带语言标签**（bash/plaintext/python）
- 代码块用等宽字体 + 浅灰背景
- 数字列表用于步骤，圆点列表用于要点
- 浅灰分割线分隔区块
- 左对齐、留白充足

### 示例格式：
```
✅ 重大好消息
核心已正常运行

🔴 现在的问题
1. xxx组件版本不兼容
2. xxx组件网络超时

┌─ bash ───────────────────────────────┐
│ rd /s /q "C:\Users\...\feishu"     │
└──────────────────────────────────────┘
```

**铁律：格式不对必须修改！**

### 检索优先级

**长期记忆检索顺序：**
1. **首选：云端Milvus向量数据库**
   - 地址：`8.137.122.11:19530`
   - 集合：`CaySon_db`
   - 优势：快速、准确、匹配度高

2. **备选：本地ChromaDB**
   - 路径：`C:\Users\Administrator\.mem0\chroma\`
   - 触发条件：Milvus连接失败时自动降级

### 检索脚本

```bash
# 主检索脚本（优先Milvus）
python E:\workspace\scripts\mem0_dual_write.py search "查询内容"

# 仅本地检索
python E:\workspace\scripts\show_memories.py
```

### 记忆写入策略

- 新记忆：**双写**（同时写入Milvus + ChromaDB）
- 同步脚本：`E:\workspace\scripts\sync_memories_to_milvus.py`

### 技术配置

| 项目 | 配置 |
|------|------|
| Milvus HOST | 8.137.122.11 |
| Milvus PORT | 19530 |
| Collection | CaySon_db |
| Embedding模型 | nomic-embed-text |
| 维度 | 768 |

---

Add whatever helps you do your job. This is your cheat sheet.
