# MemOS - AI记忆操作系统研究报告

## 1. 🎯 这是什么（简介）

**MemOS** 是浙江大学团队开源的 **AI记忆操作系统**，专门为LLM和AI Agent系统提供统一的记忆存储/检索/管理能力。

> 视频主题：**"别让渡你的记忆主权"** — Anthropic把记忆锁进了闭源系统，MemOS主张把记忆控制权还给自己

### 核心理念
``` 
你把记忆的控制权交给AI平台 = 你的数据、偏好、上下文都被平台锁定
MemOS = 把记忆主权还给你 = 本地优先 + 可控共享 + 自主演化
```

### GitHub信息
- **仓库**: https://github.com/MemTensor/MemOS
- **Stars**: 持续增长中
- **License**: Apache 2.0
- **官方OpenClaw插件**: MemTensor/MemOS-Cloud-OpenClaw-Plugin

---

## 2. 📝 关键功能点

### 🦞 OpenClaw官方集成
```
MemOS OpenClaw Plugin — Cloud & Local 两种模式
├── Cloud Plugin: 云端托管记忆服务
│   ├── 72% 更低token使用率（智能记忆检索替代加载完整历史）
│   └── 多智能体记忆共享（相同user_id自动上下文传递）
│
└── Local Plugin (v1.0.0): 100%本地设备记忆
    ├── 持久化SQLite存储
    ├── 混合搜索（FTS5 + 向量检索）
    ├── 任务摘要 & 技能演化
    ├── 多智能体协作
    └── 完整Memory Viewer仪表盘
```

### 核心功能矩阵

| 功能 | 说明 |
|------|------|
| **统一记忆API** | 单个API添加/检索/编辑/删除记忆，图结构化存储 |
| **多模态记忆** | 原生支持文本、图像、工具轨迹、人物角色 |
| **MemCube知识库** | 多知识库管理，跨用户/项目/智能体的隔离与共享 |
| **MemScheduler** | 异步操作，毫秒级延迟，高并发稳定 |
| **记忆反馈修正** | 自然语言反馈修正记忆（纠正/补充/替换） |
| **工具记忆** | 记录工具使用历史用于Agent规划 |

---

## 3. ⚡ 怎么使用

### 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/MemTensor/MemOS.git
cd MemOS

# 2. 安装依赖
pip install -r ./docker/requirements.txt

# 3. 配置环境变量
cp docker/.env.example MemOS/.env
# 编辑.env，填入API密钥（OPENAI_API_KEY等）

# 4. 启动服务（Docker）
docker compose up

# 或 uvicorn启动
cd src
uvicorn memos.api.server_api:app --host 0.0.0.0 --port 8001 --workers 1
```

### API调用示例

```python
import requests
import json

# 添加用户消息
data = {
    "user_id": "8736b16e-1d20-4163-980b-a5063c3facdc",
    "mem_cube_id": "b32d0977-435d-4828-a86f-4f47f8b55bca",
    "messages": [{"role": "user", "content": "I like strawberry"}],
    "async_mode": "sync"
}
res = requests.post("http://localhost:8000/product/add", json=data)
print(res.json())

# 检索记忆
data = {
    "query": "What do I like",
    "user_id": "8736b16e-1d20-4163-980b-a5063c3facdc",
    "mem_cube_id": "b32d0977-435d-4828-a86f-4f47f8b55bca"
}
res = requests.post("http://localhost:8000/product/search", json=data)
print(res.json())
```

### OpenClaw插件安装

```bash
# Cloud模式
npm install @memtensor/memos-cloud-openclaw-plugin

# Local模式
npm install @memtensor/memos-local-openclaw-plugin
```

---

## 4. ✅ 优点

1. **记忆主权回归用户** - 本地优先，数据不必须上云
2. **72% token节省** - 智能检索替代完整历史加载
3. **多模态支持** - 文本/图像/工具轨迹统一管理
4. **多智能体共享** - 相同user_id自动上下文传递
5. **技能自主演化** - 记忆随使用持续优化
6. **企业级稳定性** - Redis Streams调度，高并发支持
7. **OpenClaw官方集成** - 开源社区深度合作

---

## 5. ❌ 缺点

1. **部署有一定复杂度** - 需要配置多组件（向量库/Redis等）
2. **中文文档相对英文较少** - 社区主要英文交流
3. **对Embedding模型有依赖** - 需要配置MOS_EMBEDDER_API_KEY
4. **云服务有使用成本** - Cloud模式需要注册API Key

---

## 6. 🎬 使用场景

| 场景 | 适用性 |
|------|--------|
| **个人AI助手记忆持久化** | ⭐⭐⭐⭐⭐ 完美 |
| **多智能体协作共享上下文** | ⭐⭐⭐⭐⭐ 完美 |
| **企业知识库管理** | ⭐⭐⭐⭐ 良好 |
| **Agent长期任务记忆** | ⭐⭐⭐⭐⭐ 完美 |
| **跨会话记忆恢复** | ⭐⭐⭐⭐⭐ 完美 |

---

## 7. 🔧 运行依赖环境

### 基础依赖
```
- Python 3.10+
- SQLite (本地存储)
- Redis (任务调度)
- Docker (可选，容器部署)
```

### LLM支持
```
OpenAI / Azure OpenAI / Qwen (DashScope) / DeepSeek / MiniMax / Ollama / HuggingFace / vLLM
```

### 配置文件示例 (.env)
```
OPENAI_API_KEY=sk-xxx
MOS_EMBEDDER_API_KEY=xxx  # 向量嵌入API
MEMRADER_API_KEY=xxx       # 阿里云百炼API（可选）
```

---

## 8. 🚀 部署使用注意点

### ⚠️ 关键提醒
1. **首次部署建议Docker** - 一键部署减少环境问题
2. **生产环境务必配置Redis** - 高并发依赖
3. **向量模型选择** - 影响检索质量，建议用bge-m3或其他中文优化模型
4. **user_id是记忆共享的钥匙** - 多Agent共享需要相同user_id
5. **mem_cube_id是知识库隔离** - 不同项目用不同cube

### 性能优化建议
```python
# 生产环境推荐配置
- 向量检索: BGE-M3 (multilingual)
- 调度器: Redis Streams
- 存储: SQLite + ChromaDB 向量索引
```

---

## 9. 🕳️ 避坑指南

### 🔴 坑1：API Key配置问题
**问题**: 启动报OPENAI_API_KEY相关错误
**解决**: 
```bash
# 确保.env文件在MemOS/目录下，不是docker/目录
cp docker/.env.example MemOS/.env
```

### 🔴 坑2：向量模型选择
**问题**: 中文检索质量差
**解决**: 使用中文优化模型如 `bge-m3` 或 `text2vec-base-chinese`

### 🔴 坑3：多智能体记忆不共享
**问题**: 不同Agent看不到彼此记忆
**解决**: 确保使用相同的 `user_id`，不同项目用不同 `mem_cube_id`

### 🟡 注意：版本差异
- v1.0 (Stellar) - 基础框架
- v2.0 (Stardust) - 新增知识库、多模态、工具记忆
- Local Plugin - 独立npm包，需要单独安装

---

## 10. 📊 总结

### 学习价值：⭐⭐⭐⭐⭐（5星）
**强烈推荐学习！** 这个项目代表了两个重要趋势：
1. **AI记忆操作系统化** - 记忆不再是简单的向量检索，而是系统级设计
2. **记忆主权运动** - 用户数据控制权回归，避免被平台锁定

### 与我们系统的关联
```
MemOS ≈ 我们的 MAGMA记忆系统 进阶版
├── 图结构记忆 ✅
├── 多模态支持 ✅  
├── 混合检索 ✅
├── 本地优先 ✅
└── OpenClaw官方集成 → 潜在合作机会
```

### 推荐指数：⭐⭐⭐⭐⭐（5星）
- **对OpenClaw用户**: 必装插件，彻底解决记忆问题
- **对AI开发者**: 架构设计参考价值极高
- **对企业用户**: 私有化部署方案完整

---

## 📚 相关资源

| 资源 | 链接 |
|------|------|
| GitHub | https://github.com/MemTensor/MemOS |
| OpenClaw插件 | https://github.com/MemTensor/MemOS-Cloud-OpenClaw-Plugin |
| 论文(arXiv) | https://arxiv.org/abs/2507.03724 |
| 文档 | https://memos-docs.openmem.net |
| Dashboard | https://memos-dashboard.openmem.net |
| Discord | https://discord.gg/Txbx3gebZR |

---

*文档创建时间: 2026-04-21*
*学习来源: 抖音@慢学AI《别让渡你的记忆主权》*
