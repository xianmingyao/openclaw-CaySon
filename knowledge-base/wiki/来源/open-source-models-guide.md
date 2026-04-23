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

```bash
# 方式1: pip 安装
pip install voxtral

# 方式2: Hugging Face
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained("mistralai/voxtral-4b")

# 方式3: Ollama (最简单)
ollama pull voxtral
ollama run voxtral
```

### 云端部署

```bash
# Replicate
pip install replicate
replicate run mistral/voxtral --format tts

# Modal
modal run mistral/voxtral
```

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

```bash
# 方式1: pip
pip install uni-1

# 方式2: Hugging Face
from diffusers import StableDiffusionPipeline
pipe = StableDiffusionPipeline.from_pretrained("lumaai/uni-1")

# 方式3: ComfyUI (推荐)
# 下载 ComfyUI
# 安装 Uni-1 节点
```

### 云端部署

```bash
# Replicate
replicate run lumaai/uni-1

# 官网 API
curl -X POST https://api.lumalabs.ai/uni-1/generate
```

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

```bash
# Clone 仓库
git clone https://github.com/GAIR-NLP/daVinci-MagiHuman.git
cd daVinci-MagiHuman

# 安装依赖
pip install -r requirements.txt

# 下载预训练权重
# (查看 README 获取下载链接)

# 运行
python inference.py --prompt "你的提示词"
```

### 云端部署

```bash
# Modal (推荐)
modal run daVinci-MagiHuman/inference.py

# RunPod
# 搜索 DaVinci-MagiHuman 镜像
```

---

## 🗜️ TurboQuant (Google)

### 官方信息
- **GitHub**: `tonbistudio/turboquant-pytorch` (PyTorch 实现)
- **原始论文**: ICLR 2026
- **类型**: LLM KV Cache 压缩算法
- **Stars**: 572

### 显卡配置要求

TurboQuant 是一个压缩算法，不是独立模型：
- **对任何 LLM 都有用**
- 压缩后显存需求 **减少 50-80%**

### 本地部署

```bash
# PyTorch 实现 (tonbistudio)
git clone https://github.com/tonbistudio/turboquant-pytorch.git
cd turboquant-pytorch
pip install -e .

# 使用
from turboquant import compress_kv_cache
compressed = compress_kv_cache(model, ratio=0.5)
```

### 云端部署

```bash
# Google Cloud (TPU 推荐)
# 使用 Google Colab (T4 免费)

# Hugging Face 集成
pip install turboquant-hf
# 自动应用于所有 Hugging Face 模型
```

---

## 🎤 Cohere Transcribe (Cohere)

### 官方信息
- **官网**: https://cohere.com/
- **GitHub**: `cohere-ai/cohere-toolkit`
- **类型**: 开源语音识别 (ASR)
- **特点**: 最强开源语音识别

### 显卡配置要求

| 部署方式 | 需求 |
|---------|------|
| **云端 API** | 无需本地 GPU |
| **本地部署** | RTX 3060 (12GB) |

### 本地部署

```bash
# 方式1: pip
pip install cohere

# 方式2: Docker (完整部署)
git clone https://github.com/cohere-ai/cohere-toolkit.git
cd cohere-toolkit
docker-compose up

# 方式3: Ollama
ollama pull cohere
```

### 云端部署

```bash
# Cohere API (免费额度)
export COHERE_API_KEY="your-key"
curl -X POST "https://api.cohere.ai/v1/transcribe" \
  -H "Authorization: Bearer $COHERE_API_KEY" \
  -F "audio=@audio.mp3"
```

---

## ☁️ 云部署平台推荐

| 平台 | 特点 | 适合场景 |
|------|------|---------|
| **Replicate** | 按秒计费，一键部署 | 快速验证 |
| **Modal** | 弹性计算，冷启动快 | 生产环境 |
| **RunPod** | GPU 云，便宜 | 大模型推理 |
| **Vast.ai** | 竞价实例，最便宜 | 实验研究 |
| **Google Colab** | 免费 T4 | 小模型 |
| **Kaggle** | 免费 P100 | 小模型 |
| **AWS Sagemaker** | 企业级 | 生产部署 |
| **Modal** | 弹性计算 | 任何模型 |

### 价格对比 (RTX 4090)

| 平台 | 价格/小时 |
|------|---------|
| Vast.ai | $0.2-0.3 |
| RunPod | $0.3-0.4 |
| Modal | 按实际使用 |
| Replicate | 按秒计费 |

---

## 🖥️ 显卡选择指南

### 按预算选择

| 预算 | 推荐显卡 | 适合模型 |
|------|---------|---------|
| < $500 | RTX 3060 12GB | Voxtral 4B, Cohere |
| $500-1000 | RTX 4070 Ti 16GB | Voxtral 8B, Uni-1 |
| $1000-2000 | RTX 4090 24GB | Voxtral 24B, Uni-1, DaVinci |
| > $3000 | A100 40GB | 任何模型 |
| > $6000 | A100 80GB | 最佳体验 |

### 按用途选择

| 用途 | 推荐 | 理由 |
|------|------|------|
| 日常开发 | RTX 4070 Ti | 性价比最高 |
| 生产推理 | RTX 4090 | 大显存，稳定 |
| 研究实验 | A100 40GB | 弹性扩展 |
| 企业部署 | A100 80GB | 最高性能 |

---

## 📊 总结

| 模型 | 难度 | 成本 | 推荐程度 |
|------|------|------|---------|
| Voxtral | ⭐ | $0.3/h | ⭐⭐⭐⭐⭐ |
| Uni-1 | ⭐⭐ | $0.4/h | ⭐⭐⭐⭐ |
| DaVinci | ⭐⭐⭐ | $1.5/h | ⭐⭐⭐ |
| TurboQuant | ⭐⭐ | 免费 | ⭐⭐⭐⭐⭐ |
| Cohere | ⭐ | 免费API | ⭐⭐⭐⭐⭐ |

**推荐入门顺序:**
1. **Cohere Transcribe** - 免费 API，无需 GPU
2. **Voxtral** - 简单部署，4B 模型足够
3. **TurboQuant** - 压缩任何模型
4. **Uni-1** - 图像生成
5. **DaVinci** - 视频生成（最贵）

---

## 🔗 快速链接

- Voxtral: https://github.com/mistralai/voxtral
- Uni-1: https://lumalabs.ai/luma-typography
- DaVinci-MagiHuman: https://github.com/GAIR-NLP/daVinci-MagiHuman
- TurboQuant: https://github.com/tonbistudio/turboquant-pytorch
- Cohere: https://cohere.com/

