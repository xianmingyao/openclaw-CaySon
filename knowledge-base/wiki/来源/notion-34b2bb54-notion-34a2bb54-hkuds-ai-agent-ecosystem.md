# HKUDS 港大人工智能实验室 AI Agent生态研究报告

## 1. 🎯 这是什么

HKUDS（香港大学数据科学实验室，Hong Kong University Data Science Lab）是由黄超（Chao Huang）助理教授领导的研究团队，专注于大语言模型、AI Agent和图机器学习研究，Google Scholar引用超过14,000次。

**2026年4月连发三个开源项目，形成完整的AI Agent生态体系。**

## 2. 📝 实验室概览

### 领导者背景

- **黄超（Chao Huang）**：HKUDS助理教授

- **研究方向**：大语言模型、AI Agent、图机器学习

- **学术影响力**：Google Scholar 14,000+ 引用

### 核心项目矩阵

| 项目 | 定位 | Stars | 核心价值 |

|------|------|-------|---------|

| **OpenSpace** | 自进化引擎 | - | 技能进化、经验沉淀 |

| **OpenHarness** | 基础设施框架 | 4000+ | hands/eyes/memory/safety |

| **CLI-Anything** | CLI生成工具 | 1400+ | 任意软件→CLI |

## 3. 📊 三项目对比分析

### 技术定位对比

| 维度 | OpenSpace | OpenHarness | CLI-Anything |

|------|-----------|-------------|--------------|

| **定位** | 进化层 | 基础设施层 | 接口转换层 |

| **解决的问题** | Agent不学习 | Agent缺手脚 | 软件缺CLI |

| **代码量** | - | 1万行 | - |

| **自动化** | 技能自动进化 | 工具调用 | CLI自动生成 |

| **适用场景** | 长期任务 | 快速开发 | 软件集成 |

### 三层架构

┌─────────────────────────────────────────┐

│           OpenSpace（进化层）            │

│   技能进化 · 经验沉淀 · 工作流捕获       │

├─────────────────────────────────────────┤

│          OpenHarness（基础层）           │

│   hands · eyes · memory · safety        │

├─────────────────────────────────────────┤

│         CLI-Anything（接口层）           │

│      任意软件 → 标准CLI接口             │

└─────────────────────────────────────────┘

## 4. ⚡ 核心项目详解

### OpenSpace - 自进化引擎

**口号**："One Command to Evolve All Your Agents"

**三大能力**：

1. 🔧 **自动修复**：技能失效自动修复重试

2. 📚 **经验沉淀**：成功经验固化为可复用Skill

3. ⚡ **工作流捕获**：复杂任务简化为一条命令

**实测数据**：

- Token消耗 **减少46%**

- 收入提升 **4.2倍**

- 6小时赚取 **$11K**

**支持框架**：OpenClaw、Claude Code、Cursor、Codex、nanobot

### OpenHarness - 轻量级基础设施

**口号**："The model is the agent. The code is the harness."

**四大组件**：

| 组件 | 功能 |

|------|------|

| 🖐️ hands | 工具调用 |

| 👀 eyes | 环境感知 |

| 💾 memory | 记忆管理 |

| 🛡️ safety | 安全边界 |

**核心数据**：

- 代码量：**1万行**（Claude Code的3%）

- 工具覆盖：**98%**

- 模型支持：**任意LLM**

### CLI-Anything - CLI生成工具

**定位**：自动为任意软件生成CLI接口

**核心价值**：

- 绕过官方API限制

- 标准化AI Agent交互接口

- 支持GIMP、Blender等复杂软件

## 5. ✅ HKUDS生态优势

1. **完整性**：从基础设施→工具调用→技能进化，覆盖完整链路

2. **轻量化**：用最少代码实现最强功能

3. **开放性**：兼容现有生态（Claude Code skills、plugins）

4. **研究驱动**：学术背景支撑，技术深度有保障

5. **实战验证**：GDPVal基准测试验证，真实任务有效

## 6. ❌ 潜在风险

1. **项目新**：v0.1.0为主，稳定性待验证

2. **资源有限**：学术团队，维护能力有限

3. **文档不足**：部分项目文档较少

4. **企业功能**：缺少企业级特性（权限、审计等）

## 7. 🎯 应用场景

| 场景 | 推荐组合 | 效果 |

|------|---------|------|

| 学习Agent原理 | OpenHarness | 1万行代码，深入理解 |

| 长期任务Agent | OpenHarness + OpenSpace | 边用边进化 |

| 软件CLI集成 | CLI-Anything | 快速生成接口 |

| 生产级Agent | OpenClaw + OpenSpace | 完整生态 |

## 8. 🔧 快速上手

### OpenSpace（自进化引擎）

pip install openspace

openspace init --agent openclaw

openspace engine start

### OpenHarness（基础设施）

pip install open-harness

oh init my-agent

oh run --task "完成任务"

### CLI-Anything（CLI生成）

# 分析软件并生成CLI

cli-anything analyze <software>

## 9. 💡 与OpenClaw的协同

OpenClaw（主Agent）

│

├── OpenHarness（提供基础设施：工具调用+记忆+安全）