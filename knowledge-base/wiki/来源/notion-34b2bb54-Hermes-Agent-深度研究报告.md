# Hermes Agent 深度研究报告

> 更新时间：2026-04-10

> 来源：GitHub / 官网 / 知乎 / 技术博客

> 标签：AI-Agent / Self-Improving / NousResearch / Harness / Skills系统

---

## 1. 🎯 这是什么（简介）

**Hermes Agent** 是由 **Nous Research**（专注AI安全与对齐的公司）开发的一款**自进化AI Agent框架**。

核心理念："The agent that grows with you" — 一个与你共同成长的智能体。

官网口号：

> "部署在你的服务器上，连接你的消息账号，它就成为你的持久个人智能体——学习你的项目、自动构建技能、随时随地触达你。不是聊天机器人，不是代码补全工具，而是一个住在你机器上、每天都在变聪明的智能体。"

---

## 2. 📝 关键功能点

### 核心架构：内置闭环学习系统

| 功能 | 说明 |

|------|------|

| **自学习Skill系统** | 完成复杂任务后自动创建可复用Skill文档，下次遇到类似任务直接调用 |

| **跨会话记忆** | 持久化跨会话记忆，知识不丢失 |

| **用户画像构建** | 持续加深对用户的理解，越用越懂你 |

| **会话检索** | 可搜索历史对话，调用过去的经验 |

| **模型无关** | 支持任意LLM后端 |

| **6平台6执行环境** | 支持多种平台和运行环境 |

| **OpenClaw一键迁移** | 可从OpenClaw平滑迁移 |

### 学习闭环（核心创新）

任务完成 → 自动创建Skill → 经验沉淀 → 下次更快更准

↓

持续自我改进

↓

记忆 + Skills + 会话检索 = 同一过程的输出

**关键洞察**：记忆、Skills、会话检索不是三个独立功能，而是**同一持续过程的三个输出**。

---

## 3. ⚡ 怎么使用

### 安装部署

# 方式1：Docker一键部署

docker run -d -p 8000:8000 nousresearch/hermes-agent

# 方式2：从源码

git clone https://github.com/nousresearch/hermes-agent

cd hermes-agent

pip install -e .

hermes-agent start

### 连接平台

支持的消息平台（6平台）：

- Telegram

- Discord

- Slack

- WhatsApp

- 自定义WebSocket

### 核心命令

hermes-agent start              # 启动

hermes-agent skill list         # 查看已创建的Skills

hermes-agent memory search      # 搜索记忆

hermes-agent session list       # 查看历史会话

---

## 4. ✅ 优点

| 优点 | 说明 |

|------|------|

| 🧠 **真正的自进化** | 不是噱头，是内置闭环学习系统 |

| 📚 **Skill自动创建** | 完成任务自动生成可复用文档 |

| 🔄 **跨会话持久化** | 知识不会在会话结束后丢失 |

| 🏗️ **模型无关** | 不绑定特定LLM，可切换 |

| 🚀 **开箱即用** | Docker一键部署 |

| 🌐 **多平台支持** | 主流消息平台全覆盖 |

| 📤 **OpenClaw迁移** | 平滑过渡，降低迁移成本 |

| 🔓 **MIT协议** | 完全开源，可商用 |

---

## 5. ❌ 缺点

| 缺点 | 说明 |

|------|------|

| ⏳ **新项目** | v0.7.0，仍在快速迭代中 |

| 🖥️ **需要自托管** | 官方推荐自部署，有一定技术门槛 |

| 🧠 **资源消耗** | 持久记忆系统对存储有要求 |

| 📦 **Skill质量依赖** | 自动创建的Skill需要人工审核优化 |

| 🔧 **调试复杂** | 自进化机制黑盒，出问题难排查 |

---

## 6. 🎬 使用场景

| 场景 | 说明 |

|------|------|

| **个人AI助手** | 24/7运行，持续学习你的习惯 |

| **客服自动化** | 多平台统一接待，持续学习优化 |

| **代码助手** | 学习项目上下文，越用越懂代码库 |

| **知识管理** | 自动沉淀经验，形成组织知识库 |

| **OpenClaw增强** | 作为OpenClaw的Harness层补充 |

---

## 7. 🔧 运行依赖环境

| 依赖 | 版本要求 |

|------|---------|

| Python | 3.10+ |

| Docker | 20.10+ (可选) |

| LLM | OpenAI / Anthropic / 本地模型 (Ollama) |

| 内存 | 推荐16GB+ |

| 存储 | 推荐50GB+ (记忆存储) |

---

## 8. 🚀 部署使用注意点

### 1. 首次部署

# 设置API Key

export OPENAI_API_KEY="sk-xxx"

export ANTHROPIC_API_KEY="sk-ant-xxx"

# 启动

hermes-agent start --config config.yaml

### 2. Skill管理

- 自动创建的Skill位于 `~/.hermes/skills/`