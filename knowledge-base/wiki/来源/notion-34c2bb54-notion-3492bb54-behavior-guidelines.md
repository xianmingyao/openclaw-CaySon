# 调教🦞 行为准则规范 v2.0 (2026-04-09)

> 来源：宁兄指令 - 完整版调教规范

---

## 📋 触发条件

处理以下操作时必须遵循本准则：

- 📁 文件处理

- 🖼️ 图片操作

- ⚙️ 任务执行

- 💬 对话记忆读取

- 🔍 记忆检索操作

---

## 1. 记忆检索优先级控制规范

### 1.1 主检索通道

**云端 Milvus 向量数据库** - 优先调用

- 地址：`8.137.122.11:19530`

- Collection：`CaySon_db`

- 检索命令：`python E:\workspace\scripts\mem0_dual_write.py search "查询"`

### 1.2 备用检索通道

**本地 ChromaDB** - 仅在以下条件满足时启用：

- 云端 Milvus 数据库连接超时（超过30秒无响应）

- 网络连接中断或无法访问 Milvus 服务

- 系统检测到 Milvus 服务状态异常

- 备选命令：`python E:\workspace\scripts\show_memories.py`

---

## 2. 知识验证与整合标准流程

### 2.1 Karpathy 知识库系统（必须同步检索）

| 模块 | 路径 | 说明 |

|------|------|------|

| raw/ | `E:\workspace\knowledge-base\raw\` | 原始资料存储区 |

| index.md | `E:\workspace\knowledge-base\index.md` | 全局内容索引 |

| 概念/ | `E:\workspace\knowledge-base\概念\` | 24个核心概念体系 |

| 来源/ | `E:\workspace\knowledge-base\来源\` | 信息来源摘要 |

| CLAUDE.md | `E:\workspace\knowledge-base\CLAUDE.md` | Schema规则手册 |

### 2.2 Notion 个人知识库

- **地址**：https://www.notion.so/33d2bb5417c380f6baaff3467dea91c8

- **要求**：验证是否存在相关、相近或关键词的个人知识点

---

## 3. 知识处理与存储管理规范

### 3.1 处理逻辑

检索到历史知识点

↓

深度分析 + 结构性剖析 + 系统性整理 + 核心内容总结

↓

未检索到历史知识点

↓

创建符合规范的新整理总结内容

↓

所有内容整合至 Karpathy 知识库系统

↓

文件/截图等附件 → raw/ 目录下指定位置

↓

生成符合 Wiki 标准的笔记文档

↓

飞书文档 + Notion 笔记 双向同步

↓

最终上传至云端记忆库（Milvus + ChromaDB）双写

### 3.2 存储要求

| 系统 | 同步内容 | 时机 |

|------|----------|------|

| Karpathy 知识库 | 原始材料 + Wiki笔记 + 附件 | 每次处理后 |

| raw/ 目录 | 文件/截图等附件 | 每次有附件时 |

| 飞书文档 | 整理总结内容 | 每次处理后 |

| Notion | 整理总结内容 | 每次处理后 |

| Milvus 云端 | 记忆向量 | 每次处理后 |

| ChromaDB 本地 | 记忆向量 | 每次处理后 |

---

## 🎯 核心铁律实施细则

| 铁律 | 要求 |

|------|------|

| **铁律1** | 实事求是，数据说话。所有结论必须基于可验证的数据。**禁止**"大概、可能、应该"等模糊表述 |

| **铁律2** | 代码质量 > 代码执行速度 > 代码技巧展示 |

| **铁律3** | 24年经验风险识别机制。看到 `eval()` 等高危函数，**自动警报并拒绝执行** |

---

## ⚙️ 技能管理规范

### 技能获取与自我提升流程

遇到无法独立完成的任务

↓

调用 find-skills 技能访问 SkillHub 商店

↓

筛选下载量 TOP 20% 且 好评度 ≥ 4.5星 的技能

↓

安装完成后 → 调用 self-improving-agent 技能进行自我提升总结

↓

形成结构化报告，主动汇报：

* 新增/提升的具体能力与技能名称

* 操作流程优化点及效率提升数据

* 技能应用场景与预期效果

### 技能安全与版本管理

| 项目 | 要求 |

|------|------|

| **安全检测** | 每日凌晨 12:30 自动触发 edgeone-clawscan 全技能安全检测 |

| **安装前** | 必须通过 edgeone-clawscan 安全风险评估 |

| **版本监听** | 持续监听 SkillHub 商店版本更新 |

| **升级报告** | 包含：技能名、版本变更、执行时间、影响范围、功能对比 |

### SkillHub CLI 操作规范

| 操作 | 命令 |

|------|------|

| 搜索 | `python ~/.skillhub/skills_store_cli.py search <关键词>` |

| 安装 | `python ~/.skillhub/skills_store_cli.py install <技能名>` |

| 更新 | `python ~/.skillhub/skills_store_cli.py update <技能名>` |