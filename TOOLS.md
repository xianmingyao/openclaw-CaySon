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

### 行为准则规范 v2.0

**触发**：处理文件/图片/任务执行/记忆读取/检索时必须遵循

**记忆检索优先级**：
1. 云端 Milvus (`8.137.122.11:19530`) - 首选，30秒超时降级
2. 本地 ChromaDB - 仅 Milvus 故障/超时时降级

**知识验证**：Karpathy知识库(raw/index/概念/来源/CLAUDE.md) + Notion 双向验证

**存储要求**：Karpathy(raw/附件) + Wiki + 飞书 + Notion + 云端Milvus + 本地ChromaDB 全链路同步

**浏览器**：必须 `--headed` 有头模式

**Skill安全**：安装前必须 edgeone-clawscan 检测，安装后24小时必须实际测试

详见：`knowledge/behavior-guidelines.md`

### 记忆写入策略

- 新记忆：**双写**（同时写入Milvus + ChromaDB）
- 同步脚本：`E:\workspace\scripts\sync_memories_to_milvus.py`

### ⚠️ 飞书/Notion 同步 SIGKILL 绕过策略（05-14 铁律）

**问题**：长时间 Python 脚本（>2分钟）必被 SIGKILL

**受影响脚本**：
- `sync_feishu.py` / `sync_pull_feishu.py` → SIGKILL
- `sync_pull_notion.py` → SIGKILL
- `upload_mem0.py` → SIGKILL

**正确策略**：
1. **飞书写文档**：直接调飞书 Open API（参考 `scripts/feishu_write_github_trending.py`）
2. **Wiki 构建**：用 `knowledge-base/compile.py`（无超时问题）
3. **Milvus 同步**：用短命令而非长脚本
4. **Cron 任务**：避免 long-running Python

**技术配置**：飞书凭证在 `C:\Users\Administrator\.openclaw\openclaw.json` → `channels.feishu`

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

## 长时间任务执行准则（铁律 - 2026-06-03）

### 问题背景
OpenClaw exec工具有timeout限制，长时间运行的进程会被系统SIGKILL。
VLM调用(qwen3-vl:8b)每次需要15-25秒，多步操作累积会触发超时。

### 指数退避+后台执行策略

**核心原则**：不要一味中断，使用指数退避和后台执行规避SIGKILL

1. **指数退避重试**
   - 首次执行使用正常timeout
   - 如果超时，下次使用更长的yieldMs（乘以2的指数）
   - 示例：30s → 60s → 120s → 240s

2. **后台执行模式**
   - 对已知长时间任务使用 `background=True`
   - 使用 `process(poll)` 轮询结果
   - 示例：`exec --command --background --yieldMs 10000`

3. **分批处理**
   - 将多步操作拆分为独立的小任务
   - 每批只做1-2个操作，减少单次执行时间
   - 完成一批后，再启动下一批

4. **使用sessions_spawn**
   - 将长时间任务放到子agent执行
   - 父会话等待completion事件
   - 适用于需要多步骤且每步都耗时的场景

5. **exec timeout参数**
   - 对已知长时间任务显式传 `timeout` 参数
   - 例如：`exec --command --timeout 300` 表示5分钟timeout

### 代码示例

```python
# 指数退避示例
def exec_with_backoff(cmd, max_retries=3):
    yieldMs = 30000  # 首次30秒
    for i in range(max_retries):
        result = exec(cmd, yieldMs=yieldMs)
        if result.success:
            return result
        yieldMs *= 2  # 指数退避
    return result

# 后台执行示例
task = exec("--long-running-command--", background=True)
while not task.done:
    process(poll, sessionId=task.id, timeout=30000)
result = process(log, sessionId=task.id)
```

### 京麦自动化特定策略

**问题**：jingmai-desktop-agent每步需要2次VLM调用(act+verify)，每步约30-50秒

**解决策略**：
1. 使用 `sessions_spawn` 在子会话中执行完整流程
2. 或者每次只执行1步，用多次独立调用完成
3. 避免一次性执行3步以上的操作

---

Add whatever helps you do your job. This is your cheat sheet.
