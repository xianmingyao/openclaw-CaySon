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

```bash
# 一键安装
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# 重载shell
source ~/.bashrc   # 或 source ~/.zshrc

# 启动CLI
hermes
```

**支持平台**：Linux、macOS、WSL2、Android Termux

---

### 方案B：Docker 部署（适合服务器）

```bash
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
```

**注意**：Docker镜像已修复为非root用户运行 + virtualenv隔离

---

### 方案C：源码安装（开发者）

```bash
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
```

---

## 3. 🔧 部署后配置

### 3.1 首次配置向导

```bash
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
```

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
```bash
hermes model                    # 交互式选择
hermes config set model.provider openai
hermes config set model.name gpt-4o
```

### 3.3 支持的消息平台（Gateway）

```
Telegram / Discord / Slack / WhatsApp / Signal / Email
```

配置消息网关：
```bash
# 启动网关
hermes gateway setup   # 交互式配置各平台
hermes gateway start   # 启动网关进程
```

---

## 4. 🔄 结合OpenClaw（核心！）

### 4.1 一键迁移OpenClaw（官方支持！）

**安装Hermes后，直接运行迁移命令**：

```bash
hermes claw migrate              # 交互式迁移（完整预设）
hermes claw migrate --dry-run    # 预览迁移内容（不执行）
hermes claw migrate --preset user-data   # 仅迁移用户数据（不含密钥）
hermes claw migrate --overwrite  # 覆盖已有冲突
```

**迁移内容（完整导入）**：

| 项目 | 说明 |
|------|------|
| `SOUL.md` | 角色定义文件 |
| `MEMORY.md` / `USER.md` | 记忆文件 |
| Skills | 用户创建的Skills → `~/.hermes/skills/openclaw-imports/` |
| Command allowlist | 命令审批模式 |
| Messaging settings | 平台配置、工作目录 |
| API Keys | Telegram/OpenRouter/OpenAI/Anthropic/ElevenLabs |
| TTS assets | 工作区音频文件 |
| `AGENTS.md` | 工作区指令 |

---

### 4.2 组合方案（推荐架构）

```
┌─────────────────────────────────────────────┐
│              用户（微信/Telegram/Discord）     │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│           OpenClaw（多渠道入口）               │
│    微信 / Telegram / Discord / 飞书 等       │
│    Skills生态 / HEARTBEAT / Cron定时任务     │
└─────────────────────────────────────────────┘
                    ↓ 交给Hermes处理
┌─────────────────────────────────────────────┐
│         Hermes Agent（自进化引擎）            │
│    三层记忆 / GEPA进化 / 用户建模 / Skills    │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│         共享记忆层（Milvus + ChromaDB）       │
│         持久化记忆 / 向量检索                 │
└─────────────────────────────────────────────┘
```

**操作步骤**：

```bash
# 1. OpenClaw保持现有配置（宁兄的微信/Telegram等渠道）
# 2. 安装Hermes
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# 3. 一键迁移OpenClaw配置
hermes claw migrate

# 4. 在OpenClaw中配置Hermes为辅助Agent
# 在OpenClaw的agents配置中添加hermes：
openclaw agents add hermes --type hermes --model anthropic/claude-3-5-sonnet

# 5. 测试协同
# OpenClaw主会话 → 调用Hermes处理需要自进化的任务
```

### 4.3 OpenClaw + Hermes 协同场景

| 场景 | OpenClaw负责 | Hermes负责 |
|------|-------------|-----------|
| 日常对话 | 接收消息、路由分发 | - |
| 复杂任务 | 任务分解 | 执行+自进化 |
| 记忆查询 | 记忆检索 | 记忆沉淀+进化 |
| 新技能学习 | 触发学习 | 消化+固化为Skill |
| 定期复盘 | 触发复盘 | 复盘+优化Skills |

---

## 5. 🧪 测试方案（完整验证流程）

### 5.1 安装后验证（hermes doctor）

```bash
# 诊断检查
hermes doctor

# 预期输出：所有检查项PASS
```

### 5.2 基础功能测试

```bash
# 1. 启动CLI
hermes

# 2. 测试对话
> 你好，请自我介绍
# 预期：回复包含Hermes Agent信息

# 3. 测试记忆
> 记住我喜欢喝美式咖啡
# 预期：确认记住

# 4. 验证记忆持久化（新会话）
> 我喜欢喝什么？
# 预期：回答美式咖啡

# 5. 测试Skills
> /skills
# 预期：列出已安装的Skills

# 6. 测试工具
> 帮我搜索今天的天气
# 预期：调用工具返回结果

# 7. 测试会话搜索
> 找到之前关于什么的讨论
# 预期：FTS5全文搜索返回历史会话
```

### 5.3 自进化功能测试

```bash
# 1. 执行一个复杂任务（触发Skill创建）
> 帮我写一个Python脚本，实现数据清洗+可视化

# 2. 检查Skill是否自动创建
> /skills
# 预期：新Skill出现在列表中

# 3. 使用新Skill
> /data-clean-viz
# 预期：调用刚创建的Skill

# 4. 测试GEPA进化（如果有self-evolution包）
git clone https://github.com/NousResearch/hermes-agent-self-evolution
cd hermes-agent-self-evolution
pip install -e .

# 对某个Skill进行进化
hermes-agent evolve --skill <skill-name>

# 验证进化效果
# 预期：质量分数提升（官方数据：0.408 → 0.569，+39.5%）
```

### 5.4 消息网关测试

```bash
# 1. 配置Telegram（示例）
hermes gateway setup
# 选择Telegram，输入Bot Token

# 2. 启动网关
hermes gateway start

# 3. Telegram发送消息给Bot
# 预期：收到回复

# 4. 跨平台测试
# Telegram发消息 → Discord也同步收到
```

### 5.5 OpenClaw迁移验证

```bash
# 1. 迁移前备份OpenClaw
cp -r ~/.openclaw ~/.openclaw.backup

# 2. 执行迁移（dry-run预览）
hermes claw migrate --dry-run

# 3. 执行迁移
hermes claw migrate

# 4. 验证每个迁移项
ls ~/.hermes/skills/openclaw-imports/   # Skills导入成功？
cat ~/.hermes/memory/*.md               # 记忆导入成功？
grep -r "SOUL.md" ~/.hermes/            # 角色定义导入成功？

# 5. OpenClaw仍可正常使用
openclaw status
```

### 5.6 性能基准测试

```bash
# 1. 测试$5 VPS运行
# 在1核1G VPS上运行，观察响应时间

# 2. 记忆检索性能
time hermes memory search "测试查询"

# 3. 冷启动时间
time hermes  # 从启动到首次响应

# 4. 并发处理
# 同时发送5条消息，验证并行处理
```

---

## 6. 🔐 安全配置

### 6.1 命令审批

```bash
# 设置命令白名单
hermes config set security.command_allowlist "read,search,execute"

# 启用审批模式
hermes config set security.approval_mode true
```

### 6.2 DM配对

```bash
# 设置允许的DM用户
hermes config set security.allowed_users "user_id_1,user_id_2"

# 启用DM配对
hermes config set security.dm_pairing true
```

### 6.3 容器隔离

```bash
# 使用Docker隔离执行
hermes tools set backend docker

# 配置容器资源限制
hermes config set docker.memory_limit "2g"
hermes config set docker.cpu_limit "1"
```

---

## 7. 🚀 生产环境部署

### 7.1 systemd服务（Linux）

```ini
# /etc/systemd/system/hermes-agent.service
[Unit]
Description=Hermes Agent Service
After=network.target

[Service]
Type=simple
User=hermes
WorkingDirectory=/home/hermes
ExecStart=/usr/local/bin/hermes gateway start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable hermes-agent
sudo systemctl start hermes-agent
sudo systemctl status hermes-agent
```

### 7.2 反向代理（Nginx）

```nginx
# /etc/nginx/sites-available/hermes
server {
    listen 443 ssl;
    server_name hermes.your-domain.com;

    ssl_certificate /etc/letsencrypt/live/hermes.your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/hermes.your-domain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 7.3 备份策略

```bash
# 定时备份记忆和配置
0 2 * * * tar -czf ~/hermes-backup-$(date +\%Y\%m\%d).tar.gz ~/.hermes

# 备份脚本（每周）
#!/bin/bash
DATE=$(date +\%Y\%m\%d)
tar -czf /backup/hermes-config-$DATE.tar.gz \
  ~/.hermes/config.yaml \
  ~/.hermes/skills/ \
  ~/.hermes/memory/
```

---

## 8. 🕳️ 避坑指南

### 🔴 坑1：Windows原生不支持
**问题**：Native Windows直接运行会报错
**解决**：安装WSL2，在WSL2里运行安装命令

### 🔴 坑2：Termux缺少语音依赖
**问题**：Termux安装时full extra有Android不适配的语音依赖
**解决**：使用`.[termux]`extra，不使用`.[all]`

### 🔴 坑3：迁移后Skills路径
**问题**：Skills导入到`openclaw-imports/`子目录，不在根目录
**解决**：
```bash
# 查看导入的Skills
ls ~/.hermes/skills/openclaw-imports/

# 如需移动到主Skills目录
mv ~/.hermes/skills/openclaw-imports/* ~/.hermes/skills/
```

### 🔴 坑4：Docker非root问题
**解决**：新版本已修复（16小时前commit），使用最新镜像

### 🔴 坑5：model name拼写错误
**问题**：配置model时拼写错误导致连接失败
**解决**：
```bash
hermes model  # 使用交互式选择，避免手动拼写
```

---

## 9. 📊 测试清单

| 测试项 | 命令 | 预期结果 |
|--------|------|---------|
| 安装成功 | `hermes --version` | 显示版本号 |
| Doctor检查 | `hermes doctor` | 全部PASS |
| CLI对话 | `hermes` → `你好` | 正常回复 |
| 记忆持久化 | 记住X → 新会话 → 问X | 回答正确 |
| Skills列表 | `/skills` | 显示Skills |
| 消息网关 | Telegram发消息 | 收到回复 |
| OpenClaw迁移 | `hermes claw migrate --dry-run` | 预览成功 |
| 模型切换 | `hermes model` | 切换成功 |
| 工具调用 | 搜索天气 | 返回结果 |
| 会话搜索 | `/search 关键词` | 返回历史会话 |

---

## 10. 📊 总结

| 维度 | 评分 |
|------|------|
| **部署难度** | ⭐⭐（1条命令搞定） |
| **OpenClaw迁移** | ⭐（官方一键迁移） |
| **功能完整度** | ⭐⭐⭐⭐⭐（40+工具/6平台/自进化） |
| **生产可用性** | ⭐⭐⭐⭐（v0.8.0，稳定） |
| **推荐指数** | ⭐⭐⭐⭐⭐（必部署！） |

### 推荐部署顺序

1. ✅ **先备份OpenClaw**：`cp -r ~/.openclaw ~/.openclaw.backup`
2. ✅ **安装Hermes**：`curl -fsSL ... | bash`
3. ✅ **迁移OpenClaw**：`hermes claw migrate`
4. ✅ **验证迁移**：检查SOUL.md/MEMORY.md/Skills
5. ✅ **测试协同**：OpenClaw主会话 + Hermes辅助
6. ✅ **生产部署**：systemd服务 + 反向代理 + 备份

---

## 相关链接

| 资源 | 链接 |
|------|------|
| GitHub | https://github.com/nousresearch/hermes-agent |
| 文档 | https://hermes-agent.nousresearch.com/docs |
| Discord | https://discord.gg/hermes-agent |
| Skills Hub | https://agentskills.io |
| 自进化引擎 | https://github.com/NousResearch/hermes-agent-self-evolution |
| 安装脚本 | https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh |
