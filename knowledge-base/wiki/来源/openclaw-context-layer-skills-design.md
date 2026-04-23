# OpenClaw Context 层 Skills 设计：基于 LangChain 三层学习框架

> 研究日期：2026-04-08
> 理论支撑：LangChain 三层学习框架（Model / Harness / Context）

---

## 1. 🎯 核心理念

### 为什么 Context 层最重要？

| 层级 | 成本 | 速度 | 效果 | OpenClaw 对应 |
|------|------|------|------|--------------|
| Model | 🔴 高 | 🐢 慢 | 上限最高 | 模型选择 |
| Harness | 🟡 中 | 🟡 中 | 中等 | 执行框架 |
| **Context** | 🟢 低 | 🐇 快 | 见效最快 | **Skills + Memory** |

```
Context 层 = Skills + Memory
                ↓
         "热更新"能力
         不改模型、不改代码
         直接加个 Skill 就变强
```

**这就是 OpenClaw Skills 的价值所在！**

---

## 2. 📊 OpenClaw Skills 定位

### OpenClaw Skills 架构

```
┌─────────────────────────────────────────────────────────┐
│                    OpenClaw Agent                         │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Context 层（运行时）                 │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐       │   │
│  │  │ Skills  │  │ Memory  │  │  Tools  │       │   │
│  │  └─────────┘  └─────────┘  └─────────┘       │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Harness 层（执行框架）              │   │
│  │  Prompt / Tool Calling / Workflow / Safety      │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Model 层（模型选择）                 │   │
│  │  MiniMax / Claude / Gemini / GPT                │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 3. 🔧 Skills 设计原则

### 3.1 Skill 的本质

```
Skill = Context 层的一种可复用组件
        ↓
   包含：instructions + tools + memory
```

### 3.2 Skill 结构

```yaml
skill-name:
  name: "技能名称"
  description: "简短描述"
  version: "1.0.0"
  
  # Context 层配置
  instructions:
    - "指令1"
    - "指令2"
  
  # 工具定义
  tools:
    - name: "工具1"
      description: "工具描述"
      command: "执行命令"
  
  # 记忆配置
  memory:
    type: "vector|file|structured"
    path: "路径"
  
  # 触发条件
  triggers:
    - "关键词1"
    - "关键词2"
```

---

## 4. 📝 Skill 设计模板

### 4.1 基础 Skill 模板

```markdown
# Skill 名称

## 描述
简短描述这个 Skill 的功能

## 触发条件
- 关键词1
- 关键词2
- 场景描述

## 指令（Instructions）
你是一个 [角色]。当用户要求 [任务] 时，你应该：

1. [步骤1]
2. [步骤2]
3. [步骤3]

## 工具（Tools）
- tool1: [描述]
- tool2: [描述]

## 输出格式
[期望的输出格式]

## 注意事项
- [注意点1]
- [注意点2]
```

### 4.2 示例：Wiki 编译 Skill

```markdown
# wiki-compiler

## 描述
将 raw/ 目录下的资料编译成 wiki 知识库

## 触发条件
- "编译知识库"
- "整理 wiki"
- "构建知识体系"

## 指令（Instructions）
你是一个知识整理专家。请将 raw/ 目录下的所有资料编译成一个 wiki 知识库。

要求：
1. 读取 raw/ 目录下的所有 .md 文件
2. 提取每个文件的核心概念
3. 为每个概念写一篇简短的解释文章
4. 建立分类目录结构
5. 添加双向链接（bidirectional links）关联相关概念
6. 输出格式：Markdown

## 工具（Tools）
- file-read: 读取 raw/ 目录下的文件
- file-write: 写入 wiki/ 目录
- search: 搜索相关概念

## 输出格式
```markdown
# 知识库

## 分类
- [分类1]
- [分类2]

## 概念
### [概念1]
[解释]

### [概念2]
[解释]

## 反向链接
[链接关系]
```
```

---

## 5. 🎯 核心 Skill 设计

### 5.1 知识收集 Skill

```markdown
# knowledge-collector

## 描述
自动收集和整理知识资料

## 触发条件
- "收集知识"
- "整理资料"
- "保存到知识库"

## 指令（Instructions）
你是一个知识收集专家。请帮助用户收集和整理知识资料。

工作流程：
1. 识别用户提供的知识来源（URL/文件/文本）
2. 使用工具获取内容
3. 转换为 Markdown 格式
4. 保存到 raw/ 目录
5. 记录收集日志

## 工具（Tools）
- web-fetch: 获取网页内容
- file-write: 写入本地文件
- convert: 格式转换
```

---

### 5.2 Wiki 编译 Skill

```markdown
# wiki-compiler

## 描述
将 raw/ 目录编译成 wiki 知识库

## 触发条件
- "编译 wiki"
- "构建知识库"
- "整理知识"

## 指令（Instructions）
你是一个知识整理专家。请将 raw/ 目录编译成 wiki 知识库。

编译流程：
1. 扫描 raw/ 目录所有 .md 文件
2. 提取核心概念和关键信息
3. 建立分类体系
4. 生成双向链接
5. 输出到 wiki/ 目录

## 工具（Tools）
- file-read: 读取 raw/
- file-write: 写入 wiki/
- search: 建立链接
```

---

### 5.3 知识查询 Skill

```markdown
# knowledge-query

## 描述
在 wiki 知识库中查找答案

## 触发条件
- "查找知识"
- "查询资料"
- "搜索知识库"

## 指令（Instructions）
你是一个知识库助手。请在 wiki/ 目录中查找问题的答案。

查询流程：
1. 理解用户问题
2. 在 wiki/ 中搜索相关内容
3. 综合答案
4. 如果找到好的结果，建议归档

## 工具（Tools）
- search: 搜索 wiki/
- file-read: 读取相关文件
- summarize: 总结答案
```

---

### 5.4 同事 Skill（参考同事.skill）

```markdown
# coworker

## 描述
AI 同事角色扮演，协助完成工作

## 触发条件
- "帮我做"
- "同事协助"
- "分工合作"

## 指令（Instructions）
你是一个勤劳的 AI 同事。当用户要求你协助工作时：

1. 理解任务目标
2. 评估工作量和复杂度
3. 主动承担力所能及的任务
4. 定期汇报进度
5. 主动发现和解决问题

## 同事规范
- 主动积极，不等指令
- 及时汇报，不埋问题
- 分工合作，尊重用户
- 质量优先，效率并重
```

---

## 6. 🔄 Skill 生命周期

```
创建 → 安装 → 触发 → 执行 → 学习 → 优化
  ↓        ↓       ↓       ↓       ↓       ↓
 设计    加载    条件    工具    Trace   迭代
       验证     匹配    调用    记录    改进
```

### 6.1 创建阶段
- 设计 Skill 结构和指令
- 定义触发条件
- 编写工具配置

### 6.2 安装阶段
- 验证 Skill 语法
- 测试功能
- 加载到 OpenClaw

### 6.3 执行阶段
- 触发条件匹配
- 加载上下文
- 执行指令
- 调用工具

### 6.4 学习阶段
- 记录 Trace
- 分析执行效果
- 反馈优化

---

## 7. 📊 Skills 分类

### 7.1 按功能分类

| 类别 | 示例 | 说明 |
|------|------|------|
| **知识管理** | knowledge-collector, wiki-compiler | 知识收集、整理、查询 |
| **工作协助** | coworker, project-manager | 角色扮演、任务协助 |
| **开发工具** | code-review, git-assistant | 代码审查、Git 操作 |
| **内容创作** | article-writer, summarizer | 文章撰写、内容总结 |
| **数据分析** | data-analyst, report-generator | 数据分析、报告生成 |

### 7.2 按复杂度分类

| 级别 | 说明 | 示例 |
|------|------|------|
| L1 | 简单指令 | 翻译、格式转换 |
| L2 | 多步骤任务 | 撰写文章、整理资料 |
| L3 | 复杂协作 | 项目管理、代码开发 |
| L4 | 自主决策 | 战略规划、风险评估 |

---

## 8. 💡 Context 层最佳实践

### 8.1 Skill 设计原则

1. **单一职责** — 每个 Skill 只做一件事
2. **清晰触发** — 明确的触发条件
3. **可组合** — Skill 之间可调用
4. **可观测** — 记录 Trace
5. **可优化** — 基于反馈迭代

### 8.2 Context 层 vs Harness 层

| 维度 | Context 层（Skills） | Harness 层（框架） |
|------|---------------------|-------------------|
| 更新频率 | 高（实时） | 低（版本发布）|
| 改动范围 | 小（单个 Skill）| 大（全局）|
| 风险 | 低 | 高 |
| 见效 | 快 | 慢 |
| 粒度 | 细（任务级）| 粗（系统级）|

---

## 9. 🔧 技术实现

### 9.1 Skill 文件结构

```
skills/
├── skill-name/
│   ├── SKILL.md          # Skill 定义
│   ├── instructions.md   # 指令文档
│   ├── tools.yaml        # 工具配置
│   └── memory/           # 记忆配置
│       └── config.json
```

### 9.2 Skill 注册

```yaml
skills:
  - name: "wiki-compiler"
    path: "./skills/wiki-compiler"
    enabled: true
    triggers:
      - "编译"
      - "知识库"
    version: "1.0.0"
```

---

## 10. 📊 总结

| 维度 | 评分 |
|------|------|
| 实用性 | ⭐⭐⭐⭐⭐ |
| 可扩展性 | ⭐⭐⭐⭐ |
| 学习成本 | ⭐⭐⭐ |
| 维护成本 | ⭐⭐⭐ |

### 一句话总结
> **Context 层 Skills = OpenClaw 的"热更新"能力，不改模型不改代码，直接加 Skill 就变强。**

### 行动清单

- [ ] 设计标准 Skill 模板
- [ ] 开发知识管理系列 Skill
- [ ] 实现 Skill 追踪和反馈机制
- [ ] 建立 Skill 生态（分享/安装）

