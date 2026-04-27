# AgentSkills 技术规范

> 类型：概念/方法论

> 更新时间：2026-04-10

## 简介

AgentSkills的SKILL.md技术规范，用于构建AI Agent的"能力包"。

## 核心概念

### Skills的本质

> Skill是把人类的经验写成一份说明书，然后交给大模型严格执行

## 四大章节

| 章节 | 内容 |

|------|------|

| 01 | Skills机制介绍 - YAML头部编写技巧 |

| 02 | Skills流程编写规范 - 思维链(CoT)应用 |

| 03 | 快速生成Skills |

| 04 | 自动化工具测试与验证 |

## YAML头部要点

- **Name**：必须全小写，与文件夹名称1:1对齐

- **Description**：动作(What) + 触发时机(When)，命中率从45%提升到92%

## CoT思维链三要素

1. 判定条件 - 二次强化场景

2. 分步指南 - 原子化操作

3. 异常分支 - 容错路径

## 相关标签

#AgentSkills #SKILL规范 #AI-Agent #YAML #CoT #思维链