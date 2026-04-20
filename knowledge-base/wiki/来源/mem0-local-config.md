# Mem0 本地配置指南（Ollama + ChromaDB）

## 方案概述
使用本地Ollama运行模型，不需要OpenAI API Key，完全隐私。

## 环境要求

### 1. Ollama 安装
```bash
# 下载安装
https://ollama.com/download

# 验证安装
ollama --version
# 输出: ollama version 0.18.3
```

### 2. 安装模型
```bash
# 安装Embedding模型（必需）
ollama pull nomic-embed-text

# 安装LLM模型（用于记忆提取）
ollama pull llama3.2

# 查看已安装模型
ollama list
```

### 3. 安装依赖
```bash
pip install mem0ai chromadb
```

## Python 配置

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from mem0 import Memory

os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"

config = {
    "vector_store": {
        "provider": "chroma",
        "config": {
            "collection_name": "clawdbot_memories",
            "path": os.path.expanduser("~/.mem0/chroma")
        }
    },
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "llama3.2",
            "temperature": 0.0,
        }
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "nomic-embed-text"
        }
    }
}

memory = Memory.from_config(config)
```

## 常用操作

### 添加记忆
```python
result = memory.add(
    "用户宁采臣是CTO，24年技术老兵",
    user_id="ningcaison"
)
```

### 搜索记忆
```python
results = memory.search(
    "用户背景是什么？",
    user_id="ningcaison"
)
```

### 获取所有记忆
```python
all_memories = memory.get_all(user_id="ningcaison")
```

### 删除记忆
```python
memory.delete(memory_id="xxx", user_id="ningcaison")
```

## 脚本文件

| 脚本 | 功能 |
|------|------|
| `scripts/mem0_local_test.py` | 本地配置测试 |
| `skills/mem0/scripts/mem0-local-*.js` | Node.js本地脚本（待完善） |

## 测试结果

2026-03-28 测试成功：
- Mem0初始化成功
- 添加记忆成功
- 搜索成功
- LLM自动将记忆拆分为细粒度条目

记忆示例：
- "User is Ning Cai Chen"
- "Is a CTO"
- "Has 24 years of technical experience"
- "Specializes in AI Agent"
- "Specializes in RAG"
- "Specializes in Windows automation"
- "Specializes in cross-border e-commerce development"

## 注意事项

1. **Ollama必须运行**：每次使用前确保 `ollama serve` 在运行
2. **模型必须安装**：`nomic-embed-text` 用于向量嵌入，`llama3.2` 用于记忆提取
3. **存储位置**：ChromaDB默认存储在 `~/.mem0/chroma`

## 故障排除

### Ollama连接失败
```bash
# 确保Ollama正在运行
ollama serve

# 测试连接
curl http://localhost:11434/api/tags
```

### 模型拉取失败
```bash
# 检查网络
# 重试拉取
ollama pull nomic-embed-text
```

### ChromaDB错误
```bash
# 删除旧数据库重新初始化
rm -rf ~/.mem0/chroma
```
