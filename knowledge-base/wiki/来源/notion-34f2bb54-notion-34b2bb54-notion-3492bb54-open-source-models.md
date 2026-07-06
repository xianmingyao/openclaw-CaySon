# 开源模型下载与部署指南

> 整理时间：2026-03-30

> 来源：GitHub 搜索 + 官方文档

---

## 🎯 模型总览

| 模型 | 公司 | 类型 | 链接 | 显卡要求 |

|------|------|------|------|---------|

| **Voxtral TTS** | Mistral | 语音合成 | [GitHub](https://github.com/mistralai/voxtral) | 4GB+ VRAM |

| **Voxtral ASR** | Mistral | 语音识别 | [GitHub](https://github.com/mistralai/voxtral) | 4GB+ VRAM |

| **Uni-1** | Luma AI | 图像生成 | [官网](https://lumalabs.ai/luma-typography) | 8GB+ VRAM |

| **DaVinci-MagiHuman** | GAIR-NLP | 视频生成 | [GitHub](https://github.com/GAIR-NLP/daVinci-MagiHuman) | 24GB+ VRAM |

| **TurboQuant** | Google | LLM压缩 | [GitHub](https://github.com/tonbistudio/turboquant-pytorch) | 取决于模型 |

| **Cohere Transcribe** | Cohere | 语音识别 | [官网](https://cohere.com/) | 云端 |

---

## 🔥 Voxtral TTS / ASR (Mistral)

### 官方信息

- **GitHub**: `mistralai/voxtral`

- **官网**: https://mistral.ai/news/voxtral/

- **类型**: 开源语音合成(TTS) + 语音识别(ASR)

- **模型大小**: Voxtral 4B / 8B / 24B

### 显卡配置要求

| 模型 | 参数量 | 最低显存 | 推荐显存 |

|------|--------|---------|---------|

| Voxtral-4B | 4B | RTX 3060 (12GB) | RTX 4080 (16GB) |

| Voxtral-8B | 8B | RTX 4090 (24GB) | A100 (40GB) |

| Voxtral-24B | 24B | A100 (40GB) | A100 80GB |

### 本地部署

# 方式1: pip 安装

pip install voxtral

# 方式2: Hugging Face

from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("mistralai/voxtral-4b")

# 方式3: Ollama (最简单)

ollama pull voxtral

ollama run voxtral

### 云端部署

# Replicate

pip install replicate

replicate run mistral/voxtral --format tts

# Modal

modal run mistral/voxtral

---

## 🖼️ Uni-1 (Luma AI)

### 官方信息

- **官网**: https://lumalabs.ai/luma-typography

- **GitHub**: `lumalabsai/uni-1`

- **类型**: 开源图像生成模型

- **特点**: 最强开源图像模型

### 显卡配置要求

| 模型 | 最低显存 | 推荐显存 |

|------|---------|---------|

| Uni-1 | RTX 3080 (10GB) | RTX 4090 (24GB) |

### 本地部署

# 方式1: pip

pip install uni-1

# 方式2: Hugging Face

from diffusers import StableDiffusionPipeline

pipe = StableDiffusionPipeline.from_pretrained("lumaai/uni-1")

# 方式3: ComfyUI (推荐)

# 下载 ComfyUI

# 安装 Uni-1 节点

### 云端部署

# Replicate

replicate run lumaai/uni-1

# 官网 API

curl -X POST https://api.lumalabs.ai/uni-1/generate

---

## 🎬 DaVinci-MagiHuman (GAIR-NLP)

### 官方信息

- **GitHub**: `GAIR-NLP/daVinci-MagiHuman`

- **Stars**: 1,210

- **类型**: 视频生成模型

### 显卡配置要求

| 配置 | 显存要求 | 说明 |

|------|---------|------|

| 最低 | RTX 4090 (24GB) | 勉强运行 |

| 推荐 | A100 40GB | 流畅运行 |

| 最佳 | A100 80GB x2 | 并行加速 |

### 本地部署

# Clone 仓库

git clone https://github.com/GAIR-NLP/daVinci-MagiHuman.git

cd daVinci-MagiHuman

# 安装依赖

pip install -r requirements.txt

# 下载预训练权重

# (查看 README 获取下载链接)

# 运行

python inference.py --prompt "你的提示词"

### 云端部署

# Modal (推荐)

modal run daVinci-MagiHuman/inference.py

# RunPod

# 搜索 DaVinci-MagiHuman 镜像

---

## 🗜️ TurboQuant (Google)

### 官方信息

- **GitHub**: `tonbistudio/turboquant-pytorch` (PyTorch 实现)

- **原始论文**: ICLR 2026

- **类型**: LLM KV Cache 压缩算法

- **Stars**: 572