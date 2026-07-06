# OpenClaw + Hermes Agent 集成方案

> 更新时间：2026-04-10
> 状态：规划中
> 标签：OpenClaw / Hermes-Agent / 集成 / Skill系统

---

## 1. 🎯 目标

将 **Hermes Agent** 的自进化Skill系统与 **OpenClaw** 集成，让OpenClaw用户也能拥有"越用越聪明"的能力。

---

## 2. 📊 现状分析

### Hermes Agent 核心能力

| 能力 | 说明 |
|------|------|
| **自进化Skill** | 完成任务自动生成SKILL.md，下次调用 |
| **跨会话记忆** | SQLite + FTS5，持久化存储 |
| **用户画像** | 持续学习用户习惯 |
| **按需加载** | Skill不一次性加载，按需加载节省tokens |

### OpenClaw 现有能力

| 能力 | 说明 |
|------|------|
| **多渠道集成** | 微信/Telegram/Discord等 |
| **Skills生态** | 29+ Skills，ClawHub市场 |
| **记忆系统** | Milvus + ChromaDB 双写 |
| **Context层** | Skills热更新能力 |

### 差距

| 维度 | Hermes | OpenClaw |
|------|--------|----------|
| **Skill来源** | 任务中自动生成 | 人工编写/安装 |
| **进化能力** | ✅ 内置闭环学习 | ❌ 无 |
| **记忆检索** | SQLite+FTS5本地 | Milvus云端+本地 |
| **用户理解** | 持续加深 | 依赖外部系统 |

---

## 3. 🔧 集成方案

### 方案A：Hermes作为OpenClaw的Skill生成器（推荐）

**架构**：
```
OpenClaw（主控）
    ├── Hermes（Skill生成引擎）
    │   ├── 自动从对话中提取Skill
    │   └── 输出SKILL.md格式
    └── OpenClaw Skills（已有生态）
```

**实施步骤**：

```bash
# Step 1: 安装Hermes Agent
git clone https://github.com/nousresearch/hermes-agent
cd hermes-agent
pip install -e .

# Step 2: 配置OpenClaw通道
# 让Hermes连接到OpenClaw的渠道（WeChat/Telegram等）

# Step 3: 启用OpenClaw迁移
hermes claw migrate --from openclaw ./openclaw-export/

# Step 4: 双向同步
hermes claw sync --skills --to openclaw
```

### 方案B：OpenClaw Skills导入Hermes

**架构**：
```
OpenClaw Skills（已有Skill库）
    ↓ 导出
Hermes Agent（进化引擎）
    ↓ 进化后Skill
增强的Skill库
```

**Skill格式对照**：

| OpenClaw | Hermes |
|----------|--------|
| Skills/*.md | SKILL.md (YAML frontmatter) |
| SKILL.md | agentskills.io标准格式 |
| 手动创建 | **可自动生成** 🆕 |

**导出脚本**：
```python
# openclaw_to_hermes.py
import os
import shutil
from pathlib import Path

OPENCLAW_SKILLS = Path("~/.openclaw/skills").expanduser()
HERMES_SKILLS = Path("~/.hermes/skills").expanduser()

def convert_skill(src_path, dst_path):
    """OpenClaw Skill → Hermes SKILL.md格式"""
    with open(src_path) as f:
        content = f.read()
    
    # 添加YAML frontmatter
    yaml_frontmatter = f"""---
name: {src_path.stem}
description: Converted from OpenClaw
source: openclaw
---

"""
    with open(dst_path, 'w') as f:
        f.write(yaml_frontmatter + content)

# 遍历转换
for skill_file in OPENCLAW_SKILLS.rglob("*.md"):
    dst = HERMES_SKILLS / skill_file.name
    convert_skill(skill_file, dst)
```

### 方案C：混合架构（长期目标）

```
┌─────────────────────────────────────────┐
│         OpenClaw（主控层）              │
│  ┌─────────────────────────────────┐   │
│  │  多渠道集成（WeChat/Telegram等） │   │
│  └─────────────────────────────────┘   │
│              ↕                           │
│  ┌─────────────────────────────────┐   │
│  │  Context层（Skills + Memory）   │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
              ↕
┌─────────────────────────────────────────┐
│      Hermes Agent（进化引擎）            │
│  ┌─────────────────────────────────┐   │
│  │  闭环学习系统（自进化Skills）    │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │  跨会话记忆（SQLite + FTS5）    │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │  用户画像（使用习惯建模）        │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

---

## 4. 📝 实施路线图

### Phase 1: 调研与测试（1周）
- [ ] 部署Hermes Agent测试环境
- [ ] 测试`hermes claw migrate`从OpenClaw导入
- [ ] 验证Skill格式兼容性
- [ ] 评估Token消耗

### Phase 2: 集成开发（2周）
- [ ] 开发OpenClaw → Hermes Skill导出脚本
- [ ] 开发Hermes → OpenClaw Skill回传机制
- [ ] 集成测试：OpenClaw对话 → Hermes生成Skill → OpenClaw使用
- [ ] 记忆系统对接（Milvus ↔ SQLite）

### Phase 3: 自动化（1周）
- [ ] 自动化Skill进化流程
- [ ] 自动化质量审核（防止Skill泛滥）
- [ ] 监控和告警

---

## 5. 🔑 关键技术点

### Skill格式（agentskills.io标准）

Hermes使用标准化的SKILL.md格式：

```markdown
---
name: code-review
description: Professional code review skill
triggers:
  - "review code"
  - "check this PR"
  - "代码审查"
version: 1.0.0
author: hermes-auto
---

# Code Review Skill

## When to Use
- User asks to review code
- Pull request needs analysis

## Steps
1. Understand the codebase structure
2. Identify potential issues
3. Provide actionable feedback

## Examples
...
```

### OpenClaw Skill格式

```markdown
# Code Review Skill

## 触发词
- review code
- 代码审查

## 操作步骤
...
```

### 关键差异

| 方面 | OpenClaw | Hermes |
|------|----------|--------|
| **元数据** | 无 | YAML frontmatter |
| **触发条件** | 手动指定 | 自动识别 |
| **版本管理** | 无 | 内置版本 |
| **自进化** | ❌ | ✅ |

---

## 6. ✅ 立即可行动项

### 今天可以做的（不依赖Hermes部署）：

1. **整理OpenClaw现有Skills**
   ```bash
   ls ~/.openclaw/skills/
   ```

2. **研究agentskills.io格式**
   - 参考：https://agentsskills.io

3. **准备迁移文档**
   - 导出OpenClaw的SOUL.md、IDENTITY.md等

### 本周可以做的：

1. **Docker部署Hermes测试**
   ```bash
   docker run -d -p 8000:8000 nousresearch/hermes-agent
   ```

2. **测试迁移命令**
   ```bash
   hermes claw migrate --from openclaw ./export/
   ```

---

## 7. 📚 参考资料

- [Hermes官方迁移文档](https://hermes-agent.nousresearch.com/docs/guides/migrate-from-openclaw/)
- [Hermes Skills系统](https://hermes-agent.nousresearch.com/docs/guides/work-with-skills/)
- [agentskills.io标准](https://agentskills.io)
- [DeepWiki - Hermes Skills](https://deepwiki.com/NousResearch/hermes-agent/8-skills-system)

---

## 8. 🔄 更新日志

| 日期 | 更新内容 |
|------|---------|
| 2026-04-10 | 初稿完成 |

