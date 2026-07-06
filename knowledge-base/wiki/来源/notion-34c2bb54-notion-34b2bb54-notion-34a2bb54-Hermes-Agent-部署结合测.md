# Hermes Agent 部署 + 结合OpenClaw + 测试实战手册

> 更新时间：2026-04-13（基于GitHub v0.8.0）

> 来源：nousresearch/hermes-agent GitHub README + 技术文档

> 标签：部署 / 迁移 / 测试 / Hermes / OpenClaw

---

## 1. 🎯 这是什么

**Hermes Agent** 是 Nous Research 的自进化AI Agent（66.2K Stars，v0.8.0，400贡献者），与 OpenClaw 的关系：

> **"不是竞争，是组合题"** — Gggda

- **OpenClaw** = 多渠道AI助手（微信/Telegram/Discord/等）

- **Hermes Agent** = 自进化引擎 + 记忆系统 + Skills自动进化

- **组合方案**：OpenClaw做主入口，Hermes做后台自进化辅助Agent

---

## 2. ⚡ 部署方案（三选一）

### 方案A：Linux/macOS/WSL2 一键安装（推荐）

# 一键安装

curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# 重载shell

source ~/.bashrc   # 或 source ~/.zshrc

# 启动CLI

hermes

**支持平台**：Linux、macOS、WSL2、Android Termux

---

### 方案B：Docker 部署（适合服务器）

# 克隆仓库

git clone https://github.com/NousResearch/hermes-agent.git

cd hermes-agent

# Docker构建（已修复非root用户）

docker build -t hermes-agent:latest .

# 运行

docker run -d -p 8000:8000 \

-v ~/.hermes:/root/.hermes \

-e OPENAI_API_KEY=$OPENAI_API_KEY \

hermes-agent:latest

# 或者使用Docker Compose

docker-compose up -d

**注意**：Docker镜像已修复为非root用户运行 + virtualenv隔离

---

### 方案C：源码安装（开发者）

# 克隆

git clone https://github.com/NousResearch/hermes-agent.git

cd hermes-agent

# 安装 uv（Rust包管理器）

curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境（Python 3.11+）

uv venv venv --python 3.11

source venv/bin/activate

# 安装依赖

uv pip install -e ".[all,dev]"

# 运行测试

python -m pytest tests/ -q

# 启动CLI

python cli.py

---

## 3. 🔧 部署后配置

### 3.1 首次配置向导

# 交互式配置（推荐首次）

hermes setup

# 配置模型

hermes model        # 选择LLM provider和model

# 配置工具

hermes tools        # 启用哪些工具

# 配置消息平台

hermes gateway      # 启动消息网关

# 诊断检查

hermes doctor       # 诊断问题

### 3.2 支持的模型Provider

| Provider | 说明 |

|----------|------|

| `nous` | Nous Portal（自家） |

| `openrouter` | 200+模型 |

| `openai` | GPT系列 |

| `anthropic` | Claude系列 |

| `z.ai/GLM` | 智谱 |

| `kimi` | 月之暗面Moonshot |

| `minimax` | 海螺/ MiniMax |

| `ollama` | 本地模型 |

**切换模型（无需改代码）**：

hermes model                    # 交互式选择

hermes config set model.provider openai

hermes config set model.name gpt-4o

### 3.3 支持的消息平台（Gateway）

Telegram / Discord / Slack / WhatsApp / Signal / Email

配置消息网关：

# 启动网关

hermes gateway setup   # 交互式配置各平台

hermes gateway start   # 启动网关进程

---

## 4. 🔄 结合OpenClaw（核心！）

### 4.1 一键迁移OpenClaw（官方支持！）

**安装Hermes后，直接运行迁移命令**：

hermes claw migrate              # 交互式迁移（完整预设）

hermes claw migrate --dry-run    # 预览迁移内容（不执行）

hermes claw migrate --preset user-data   # 仅迁移用户数据（不含密钥）

hermes claw migrate --overwrite  # 覆盖已有冲突

**迁移内容（完整导入）**：

| 项目 | 说明 |

|------|------|

| `SOUL.md` | 角色定义文件 |

| `MEMORY.md` / `USER.md` | 记忆文件 |

| Skills | 用户创建的Skills → `~/.hermes/skills/openclaw-imports/` |