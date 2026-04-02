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
> 技术总结必须包含10个必含章节！

### 技术文档标准格式（铁律）：

```
1. 🎯 这是什么（简介）
2. 📝 关键功能点
3. ⚡ 怎么使用
4. ✅ 优点
5. ❌ 缺点
6. 🎬 使用场景
7. 🔧 运行依赖环境
8. 🚀 部署使用注意点
9. 🕳️ 避坑指南
10. 📊 总结
```

### 核心格式要素：
- ✅/🔴 Emoji图标区分正负面
- 加粗标题 + 扁平化模块设计
- **代码块必须带语言标签**（bash/yaml/python）
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

🕳️ 避坑指南

🔴 坑1：问题描述
问题：xxx
解决：xxx

📊 总结
学习价值：⭐⭐⭐⭐⭐（5星）
推荐指数：⭐⭐⭐⭐（4星）
```

**铁律：格式不对必须修改！技术总结缺少章节必须补全！**

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

## 🔒 SkillHub 技能商店规范（宁兄指令 - 铁律）

### SkillHub CLI 用法

```bash
# 搜索技能
python ~/.skillhub/skills_store_cli.py search <关键词>

# 安装技能
python ~/.skillhub/skills_store_cli.py install <技能名>

# 更新技能
python ~/.skillhub/skills_store_cli.py update <技能名>
```

### 技能安装安全流程（铁律）

**每次安装技能前必须执行：**

1. **安全扫描（必须）**
   ```bash
   # 使用 edgeone-clawscan 扫描技能安全风险
   openclaw skills scan <技能名>
   # 或使用 edgeone-clawscan 技能进行安全体检
   ```

2. **风险评估**
   - 🔴 HIGH/EXTREME 风险 → 拒绝安装，告知用户
   - 🟡 MEDIUM 风险 → 告知用户，确认后安装
   - 🟢 LOW 风险 → 可以安装

3. **安装后验证**
   ```bash
   openclaw skills list | grep <技能名>
   ```

### 每日安全扫描（Cron）

**⏰ 每天凌晨 12:30 自动执行**

使用 `edgeone-clawscan` 对所有已安装技能进行安全体检：
- 扫描技能目录：`E:\workspace\skills\`
- 扫描范围：所有已安装技能
- 异常处理：发现问题立即通知宁兄

**Cron Job ID：** 待设置（需创建）

### 技能版本监控与自动升级

**升级触发条件：**
- 每日凌晨安全扫描后检查版本更新
- 手动触发：`python ~/.skillhub/skills_store_cli.py update <技能名>`

**升级后必须：**
1. 记录升级内容（技能名、旧版本→新版本）
2. 主动告知宁兄升级详情
3. 如有重大变更，更新相关文档

**通知模板：**
```
🔔 技能升级通知
技能：<名称>
旧版本：<v1.0.0>
新版本：<v1.0.1>
变更：<简短描述>
时间：<YYYY-MM-DD HH:mm>
```

### 已安装的 SkillHub 技能

| 技能 | 版本 | 安装日期 | 用途 |
|------|------|---------|------|
| summarize | 1.0.0 | 2026-04-02 | 网页/PDF/YouTube总结 |
| nano-banana-pro | 1.0.1 | 2026-04-02 | AI图片生成（Gemini 3 Pro）|

---

Add whatever helps you do your job. This is your cheat sheet.
