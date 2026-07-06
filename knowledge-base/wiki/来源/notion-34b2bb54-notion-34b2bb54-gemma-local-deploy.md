# Gemma 4 本地部署完全指南

> 2026-04-03 | 来源：抖音@阿博粒 + 官方文档

---

## 一句话

**Gemma 4 = 谷歌开源的小规模大模型，本地部署后实现手机Agent、离线编码、跨设备流式推理**

---

## 项目信息

| 项目 | 信息 |

|------|------|

| **开发** | Google DeepMind |

| **开源** | 是（Open Weights） |

| **官网** | ai.google.dev/gemma |

| **GitHub** | github.com/google-deepmind/gemma |

| **最新版本** | Gemma 4 |

---

## 模型规格

| 模型 | 参数量 | 显存要求 | 特点 |

|------|--------|---------|------|

| **Gemma 4** | 最新版本 | 待确认 | 支持多模态（图像+文本） |

| **Gemma 3** | 4B/7B/12B | 8GB+ / 24GB+ | 多模态支持 |

| **Gemma 2** | 2B/7B/9B/27B | 8GB+ / 24GB+ | - |

| **Gemma 1** | 2B/7B | 8GB+ / 24GB+ | 基础版本 |

**官方推荐：**

- 2B checkpoint：8GB+ GPU RAM

- 7B checkpoint：24GB+ GPU RAM

---

## 本地部署方式

### 1. Ollama（最简单）

# 安装Ollama

# macOS/Linux: brew install ollama

# Windows: 下载安装包

# 下载Gemma模型

ollama pull gemma:4b

ollama pull gemma:7b

# 运行

ollama run gemma:7b

# API调用

curl http://localhost:11434/api/generate -d '{

"model": "gemma:7b",

"prompt": "你好，请介绍一下自己"

}'

### 2. LM Studio（GUI界面）

# 下载地址：https://lmstudio.ai/

# 在GUI中搜索 "gemma"

# 下载对应版本（4B/7B）

# 本地运行，支持聊天界面

### 3. Ollama + OpenWebUI（Web界面）

# 安装Ollama

# 安装OpenWebUI

docker run -d -p 3000:8080 \

-e OLLAMA_BASE_URL=http://localhost:11434 \

openwebui/open-webui:latest

# 访问 http://localhost:3000

### 4. Jan（离线ChatGPT替代）

# 下载：https://jan.ai/

# 支持 Gemma 全系列

# 完全离线，隐私友好

### 5. LocalAI（API服务）

# Docker部署

docker run -p 8080:8080 \

quay.io/localai/localai:latest \

--models-path /models

# API调用

curl http://localhost:8080/v1/completions \

-H "Content-Type: application/json" \

-d '{"model": "gemma-7b", "prompt": "你好"}'

---

## 硬件要求

| 配置 | 最低 | 推荐 |

|------|------|------|

| **GPU** | 8GB VRAM | 24GB VRAM |

| **内存** | 16GB | 32GB+ |

| **存储** | 10GB | 20GB+ |

| **CPU** | 多核 | 多核 |

### 手机/ARM设备

- **iPhone 15 Pro** (A17 Pro) - 可运行4B模型

- **Mac M1/M2/M3** - 原生支持，效率高

- **Android** - 需要Termux + 交叉编译

---

## Gemma 4 新特性（预测）

基于Gemma 3的特性推断：

| 特性 | 说明 |

|------|------|

| **多模态** | 支持图像+文本理解 |

| **长上下文** | 支持更长的上下文窗口 |

| **手机Agent** | 本地运行AI助手 |

| **离线编码** | 不依赖云端编写代码 |

| **流式推理** | 跨设备流式传输 |

---

## 本地部署 vs 云端对比

| 维度 | 本地部署 | 云端API |

|------|---------|---------|

| **成本** | 一次性硬件成本 | 按量付费 |

| **隐私** | 完全私有 | 数据上传 |

| **速度** | 取决于硬件 | 取决于网络 |

| **离线** | ✅ 支持 | ❌ 不支持 |

| **速度** | 依赖GPU | 可能有延迟 |

---

## 常见问题

### Q: 需要多少显存？