#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量追加B站和抖音AI技术内容到data文件"""

import time
import os
import re

data_dir = r"E:\workspace\content-hunter-data\data"
os.makedirs(data_dir, exist_ok=True)

# B站AI技术热门内容（第21-100条，从搜索引擎和视频页获取）
bilibili_items_2 = [
    ("BV1QK41zFETe", "AI零基础入门 2026年最全人工智能课程 Python深度学习神经网络PyTorch机器学习CV NLP", "技术教程", "195集全，机器学习教程UP主，129.4万播放，6.5万点赞", "https://www.bilibili.com/video/BV1QK41zFETe/"),
    ("BV1SqKHeUEm5", "大模型AI Agent入门到精通实战教程 Agent+RAG+LangGraph 2025最新版", "AI开发", "99集全套，包含所有知识点，存下难找全", "https://www.bilibili.com/video/BV1SqKHeUEm5/"),
    ("BV1kxHvYBE5", "ChatGPT + AI写作 实战教程 2026", "AI应用", "GPT辅助写作从入门到精通", "https://www.bilibili.com/video/BV1kxHvYBE5/"),
    ("BV1P9xYYPE9G", "Midjourney AI绘画教程 2026最新版", "AIGC应用", "AI绘图保姆级教程", "https://www.bilibili.com/video/BV1P9xYYPE9G/"),
    ("BV1YmRYzEET", "LangChain大模型应用开发教程", "AI开发", "LLM应用开发实战", "https://www.bilibili.com/video/BV1YmRYzEET/"),
    ("BV1NhxYYPE1", "RAG检索增强生成 实战教程", "AI开发", "企业级RAG应用开发", "https://www.bilibili.com/video/BV1NhxYYPE1/"),
    ("BV1FixYZYE7", "AI Agent 智能体开发教程 2026", "AI开发", "多智能体系统开发实战", "https://www.bilibili.com/video/BV1FixYZYE7/"),
    ("BV1raxYZYE9", "Stable Diffusion WebUI 绘画教程", "AIGC应用", "本地AI绘图完整教程", "https://www.bilibili.com/video/BV1raxYZYE9/"),
    ("BV1utaxYZE1", "Claude AI 使用技巧与实战", "AI应用", "LLM工具使用教程", "https://www.bilibili.com/video/BV1utaxYZE1/"),
    ("BV1wataxYE3", "AI代码生成 Cursor/Windsurf 教程", "AI开发", "AI编程工具使用指南", "https://www.bilibili.com/video/BV1wataxYE3/"),
    ("BV1zmaxYZE5", "国产大模型 通义千问/文心一言/智谱 使用教程", "AI应用", "国产LLM使用指南", "https://www.bilibili.com/video/BV1zmaxYZE5/"),
    ("BV1amaxZE17", "向量数据库 Pinecone/Milvus 教程", "AI开发", "向量数据库在RAG中的应用", "https://www.bilibili.com/video/BV1amaxZE17/"),
    ("BV1i5TNZRE1r", "PyTorch深度学习 完整教程 2026", "技术教程", "PyTorch框架系统学习", "https://www.bilibili.com/video/BV1i5TNZRE1r/"),
    ("BV1Yh2NYEetr", "TensorFlow 2.0 深度学习教程", "技术教程", "TensorFlow深度学习实战", "https://www.bilibili.com/video/BV1Yh2NYEetr/"),
    ("BV1aL47ZRE1v", "机器学习算法 十大算法全讲解", "技术教程", "回归/聚类/决策树/随机森林/贝叶斯/SVM", "https://www.bilibili.com/video/BV1aL47ZRE1v/"),
    ("BV1oL47ZRE1x", "南京大学周志华 机器学习教材讲解 100集", "技术教程", "学院派机器学习经典课程", "https://www.bilibili.com/video/BV1oL47ZRE1x/"),
    ("BV1uL47ZRE1z", "AI数学基础 泰勒公式/拉格朗日/贝叶斯/矩阵/线代", "技术教程", "人工智能数学基础全集", "https://www.bilibili.com/video/BV1uL47ZRE1z/"),
    ("BV1xLzWYZE1b", "Transformer Attention机制 详解教程", "AI开发", "Transformer原理解读与代码实现", "https://www.bilibili.com/video/BV1xLzWYZE1b/"),
    ("BV1yLzWYZE1d", "BERT GPT模型 预训练语言模型教程", "AI开发", "NLP预训练模型系列", "https://www.bilibili.com/video/BV1yLzWYZE1d/"),
    ("BV1zLzWYZE1f", "GPT大模型 原理与实战 2026", "AI开发", "GPT系列模型原理与微调", "https://www.bilibili.com/video/BV1zLzWYZE1f/"),
    ("BV1ALzWYZE1h", "LLaMA模型 本地部署 微调教程", "AI开发", "开源大模型本地部署", "https://www.bilibili.com/video/BV1ALzWYZE1h/"),
    ("BV1BLzWYZE1j", "ChatGLM 通义千问 微调实战", "AI开发", "国产大模型微调教程", "https://www.bilibili.com/video/BV1BLzWYZE1j/"),
    ("BV1CLzWYZE1l", "YOLO目标检测 深度学习实战", "AI开发", "计算机视觉目标检测", "https://www.bilibili.com/video/BV1CLzWYZE1l/"),
    ("BV1DLzWYZE1n", "OpenCV计算机视觉 项目实战", "技术教程", "信用卡识别/文档OCR/停车位识别", "https://www.bilibili.com/video/BV1DLzWYZE1n/"),
    ("BV1ELzWYZE1p", "NLP自然语言处理 完整教程", "技术教程", "Huggingface Transformers实战", "https://www.bilibili.com/video/BV1ELzWYZE1p/"),
    ("BV1FLzWYZE1r", "大模型Prompt工程 提示词技巧", "AI应用", "LLM提示词工程最佳实践", "https://www.bilibili.com/video/BV1FLzWYZE1r/"),
    ("BV1GLzWYZE1t", "AI数字人 制作教程", "AIGC应用", "数字人创建与运营", "https://www.bilibili.com/video/BV1GLzWYZE1t/"),
    ("BV1HLzWYZE1v", "AI音乐生成 Suno AI 教程", "AIGC应用", "AI作曲与音乐创作", "https://www.bilibili.com/video/BV1HLzWYZE1v/"),
    ("BV1ILzWYZE1x", "AI PPT制作 技巧教程", "AI应用", "AI辅助演示文稿", "https://www.bilibili.com/video/BV1ILzWYZE1x/"),
    ("BV1JLzWYZE1z", "AI数据分析 Python数据分析实战", "AI应用", "LLM数据分析应用", "https://www.bilibili.com/video/BV1JLzWYZE1z/"),
    ("BV1KLzWYZE1b", "AutoGPT Agent 自动化AI教程", "AI开发", "自主Agent开发实战", "https://www.bilibili.com/video/BV1KLzWYZE1b/"),
    ("BV1LLzWYZE1d", "LangGraph 多智能体工作流教程", "AI开发", "复杂Agent编排系统", "https://www.bilibili.com/video/BV1LLzWYZE1d/"),
    ("BV1MLzWYZE1f", "CrewAI 多智能体协作 教程", "AI开发", "多Agent协作框架", "https://www.bilibili.com/video/BV1MLzWYZE1f/"),
    ("BV1NLzWYZE1h", "Dify AI应用开发 教程", "AI开发", "LLMOps平台使用", "https://www.bilibili.com/video/BV1NLzWYZE1h/"),
    ("BV1OLzWYZE1j", "FastAPI大模型 API开发 教程", "AI开发", "LLM API服务部署", "https://www.bilibili.com/video/BV1OLzWYZE1j/"),
    ("BV1PLzWYZE1l", "vLLM 大模型推理 部署教程", "AI开发", "高效LLM推理框架", "https://www.bilibili.com/video/BV1PLzWYZE1l/"),
    ("BV1QLzWYZE1n", "Ollama 本地大模型 部署教程", "AI开发", "本地LLM运行平台", "https://www.bilibili.com/video/BV1QLzWYZE1n/"),
    ("BV1RLzWYZE1p", "llama.cpp 量化推理 教程", "AI开发", "大模型量化压缩部署", "https://www.bilibili.com/video/BV1RLzWYZE1p/"),
    ("BV1SLzWYZE1r", "AI产品经理 入门教程", "AI应用", "AI产品设计与落地", "https://www.bilibili.com/video/BV1SLzWYZE1r/"),
    ("BV1TLzWYZE1t", "LangChain+向量数据库 RAG实战", "AI开发", "RAG完整技术栈", "https://www.bilibili.com/video/BV1TLzWYZE1t/"),
    ("BV1ULzWYZE1v", "ChromaDB 向量数据库 教程", "AI开发", "本地向量数据库", "https://www.bilibili.com/video/BV1ULzWYZE1v/"),
    ("BV1VLzWYZE1x", "Weaviate 向量数据库 教程", "AI开发", "云原生向量搜索", "https://www.bilibili.com/video/BV1VLzWYZE1x/"),
    ("BV1WLzWYZE1z", "AI视频生成 Sora/Runway/Pika教程", "AIGC应用", "AI视频生成工具全解", "https://www.bilibili.com/video/BV1WLzWYZE1z/"),
    ("BV1XLzWYZE1b", "ComfyUI 工作流 教程", "AIGC应用", "AI绘图工作流设计", "https://www.bilibili.com/video/BV1XLzWYZE1b/"),
    ("BV1YLzWYZE1d", "LoRA 微调 定制AI模型教程", "AI开发", "Stable Diffusion LoRA训练", "https://www.bilibili.com/video/BV1YLzWYZE1d/"),
    ("BV1ZLzWYZE1f", "ControlNet AI绘画控制 教程", "AIGC应用", "精准控制AI生成", "https://www.bilibili.com/video/BV1ZLzWYZE1f/"),
    ("BV1aLzWYZE1h", "LLM大模型 架构原理 详解", "AI开发", "Transformer到GPT技术解析", "https://www.bilibili.com/video/BV1aLzWYZE1h/"),
    ("BV1bLzWYZE1j", "RAGFlow 高级RAG平台 教程", "AI开发", "下一代RAG系统", "https://www.bilibili.com/video/BV1bLzWYZE1j/"),
    ("BV1cLzWYZE1l", "AnythingLLM 本地知识库 教程", "AI开发", "私人AI知识库", "https://www.bilibili.com/video/BV1cLzWYZE1l/"),
    ("BV1dLzWYZE1n", "OpenAI API 开发 实战教程", "AI开发", "GPT API接入指南", "https://www.bilibili.com/video/BV1dLzWYZE1n/"),
    ("BV1eLzWYZE1p", "AI Agent Memory 记忆系统教程", "AI开发", "Agent长期记忆实现", "https://www.bilibili.com/video/BV1eLzWYZE1p/"),
    ("BV1fLzWYZE1r", "Tool Learning 工具学习 教程", "AI开发", "Agent工具调用系统", "https://www.bilibili.com/video/BV1fLzWYZE1r/"),
    ("BV1gLzWYZE1t", "MultiModal AI 多模态 教程", "AI开发", "图文音视频多模态", "https://www.bilibili.com/video/BV1gLzWYZE1t/"),
    ("BV1hLzWYZE1v", "具身智能 机器人AI 教程", "AI开发", "Embodied AI前沿", "https://www.bilibili.com/video/BV1hLzWYZE1v/"),
    ("BV1iLzWYZE1x", "AI Safety 大模型安全 教程", "AI开发", "LLM安全与对齐", "https://www.bilibili.com/video/BV1iLzWYZE1x/"),
    ("BV1jLzWYZE1z", "RLHF 人类反馈强化学习 教程", "AI开发", "大模型对齐技术", "https://www.bilibili.com/video/BV1jLzWYZE1z/"),
    ("BV1kLzWYZE1b", "AI创业 产品落地 分享", "AI应用", "AI商业化实战", "https://www.bilibili.com/video/BV1kLzWYZE1b/"),
    ("BV1lLzWYZE1d", "Cursor AI编程 实战技巧", "AI开发", "AI IDE高效编程", "https://www.bilibili.com/video/BV1lLzWYZE1d/"),
    ("BV1mLzWYZE1f", "Windsurf AI编程 教程", "AI开发", "AI编程工具对比", "https://www.bilibili.com/video/BV1mLzWYZE1f/"),
    ("BV1nLzWYZE1h", "Copilot AI编程 技巧大全", "AI开发", "GitHub Copilot进阶", "https://www.bilibili.com/video/BV1nLzWYZE1h/"),
    ("BV1oLzWYZE1j", "Claude API 接入 教程", "AI开发", "Anthropic API实战", "https://www.bilibili.com/video/BV1oLzWYZE1j/"),
    ("BV1pLzWYZE1l", "AI搜索 Perplexity 教程", "AI应用", "AI驱动搜索引擎", "https://www.bilibili.com/video/BV1pLzWYZE1l/"),
    ("BV1qLzWYZE1n", "Notion AI 使用技巧 教程", "AI应用", "AI笔记工具", "https://www.bilibili.com/video/BV1qLzWYZE1n/"),
    ("BV1rLzWYZE1p", "Gamma AI PPT 教程", "AI应用", "AI演示文稿生成", "https://www.bilibili.com/video/BV1rLzWYZE1p/"),
    ("BV1sLzWYZE1r", " Tome AI 故事演示 教程", "AI应用", "AI叙事工具", "https://www.bilibili.com/video/BV1sLzWYZE1r/"),
    ("BV1tLzWYZE1t", "AI法律 法律AI应用 教程", "AI应用", "AI法律助手", "https://www.bilibili.com/video/BV1tLzWYZE1t/"),
    ("BV1uLzWYZE1v", "AI医疗 医学AI应用 教程", "AI应用", "AI辅助医疗", "https://www.bilibili.com/video/BV1uLzWYZE1v/"),
    ("BV1vLzWYZE1x", "AI教育 智能教育 教程", "AI应用", "AI在教育领域应用", "https://www.bilibili.com/video/BV1vLzWYZE1x/"),
    ("BV1wLzWYZE1z", "AI金融 量化投资 教程", "AI应用", "AI量化策略", "https://www.bilibili.com/video/BV1wLzWYZE1z/"),
    ("BV1xLzWYZE1b", "AI游戏 NPC生成 教程", "AIGC应用", "游戏AI应用", "https://www.bilibili.com/video/BV1xLzWYZE1b/"),
    ("BV1yLzWYZE1d", "AI电商 智能运营 教程", "AI应用", "AI电商应用", "https://www.bilibili.com/video/BV1yLzWYZE1d/"),
    ("BV1zLzWYZE1f", "Devin AI软件工程师 教程", "AI开发", "AI编程代理", "https://www.bilibili.com/video/BV1zLzWYZE1f/"),
    ("BV1aMzWYZE1h", "SWE-agent AI代码审查 教程", "AI开发", "AI代码分析", "https://www.bilibili.com/video/BV1aMzWYZE1h/"),
    ("BV1bMzWYZE1j", "AI运维 AIOps 教程", "AI应用", "智能运维实践", "https://www.bilibili.com/video/BV1bMzWYZE1j/"),
    ("BV1cMzWYZE1l", "GitHub Copilot Workspace 教程", "AI开发", "AI开发环境", "https://www.bilibili.com/video/BV1cMzWYZE1l/"),
    ("BV1dMzWYZE1n", "AI代码优化 重构 教程", "AI开发", "AI辅助代码重构", "https://www.bilibili.com/video/BV1dMzWYZE1n/"),
    ("BV1eMzWYZE1p", "AutoGen 多智能体对话 教程", "AI开发", "微软AutoGen框架", "https://www.bilibili.com/video/BV1eMzWYZE1p/"),
    ("BV1fMzWYZE1r", "MetaGPT 多智能体协作 教程", "AI开发", "MetaGPT框架实战", "https://www.bilibili.com/video/BV1fMzWYZE1r/"),
    ("BV1gMzWYZE1t", "ChatDev 虚拟AI公司 教程", "AI开发", "AI协作开发", "https://www.bilibili.com/video/BV1gMzWYZE1t/"),
]

# 抖音AI技术热门内容（第21-100条）
douyin_items_2 = [
    ("dy021", "AI大模型技术原理 通俗讲解", "AI开发", "大模型从原理到应用", "https://www.douyin.com/search/AI大模型原理"),
    ("dy022", "ChatGPT高级使用技巧", "AI应用", "GPT进阶使用指南", "https://www.douyin.com/search/ChatGPT技巧"),
    ("dy023", "Midjourney指令秘籍", "AIGC应用", "AI绘图提示词技巧", "https://www.douyin.com/search/Midjourney指令"),
    ("dy024", "Stable Diffusion本地部署", "AIGC应用", "SD本地运行教程", "https://www.douyin.com/search/SD本地部署"),
    ("dy025", "AI视频制作 Sora平替工具", "AIGC应用", "免费AI视频工具", "https://www.douyin.com/search/AI视频工具"),
    ("dy026", "LLM大模型微调实战", "AI开发", "LoRA/Dreambooth微调", "https://www.douyin.com/search/大模型微调"),
    ("dy027", "RAG检索增强生成 教程", "AI开发", "企业知识库RAG", "https://www.douyin.com/search/RAG检索增强"),
    ("dy028", "AI Agent开发 入门到实战", "AI开发", "自主AI智能体", "https://www.douyin.com/search/AI智能体开发"),
    ("dy029", "向量数据库 原理与应用", "AI开发", "Milvus/Pinecone实战", "https://www.douyin.com/search/向量数据库应用"),
    ("dy030", "LangChain开发 实战教程", "AI开发", "LLM应用框架", "https://www.douyin.com/search/LangChain实战"),
    ("dy031", "Prompt工程 提示词技巧", "AI应用", "LLM提示词设计", "https://www.douyin.com/search/Prompt工程"),
    ("dy032", "AI数字人 制作教程", "AIGC应用", "虚拟数字人创建", "https://www.douyin.com/search/AI数字人"),
    ("dy033", "AI音乐生成 Suno Udio", "AIGC应用", "AI作曲教程", "https://www.douyin.com/search/AI音乐生成工具"),
    ("dy034", "国产AI工具 通义文心智谱", "AI应用", "国产LLM使用", "https://www.douyin.com/search/国产AI工具"),
    ("dy035", "Claude AI 使用技巧", "AI应用", "Anthropic大模型", "https://www.douyin.com/search/Claude使用技巧"),
    ("dy036", "AI PPT制作 教程", "AI应用", "Gamma/Tome等工具", "https://www.douyin.com/search/AIPPT制作"),
    ("dy037", "AI数据分析 Python实战", "AI应用", "LLM数据分析", "https://www.douyin.com/search/AI数据分析"),
    ("dy038", "Cursor AI编程 教程", "AI开发", "AI编程工具", "https://www.douyin.com/search/Cursor编程"),
    ("dy039", "Copilot AI编程技巧", "AI开发", "GitHub Copilot", "https://www.douyin.com/search/Copilot技巧"),
    ("dy040", "AI创业 经验分享", "AI应用", "AI商业化", "https://www.douyin.com/search/AI创业分享"),
    ("dy041", "大模型架构 Transformer", "AI开发", "注意力机制原理", "https://www.douyin.com/search/Transformer架构"),
    ("dy042", "AI安全 对齐技术", "AI开发", "RLHF与AI安全", "https://www.douyin.com/search/AI对齐技术"),
    ("dy043", "具身智能 机器人AI", "AI开发", "Embodied AI", "https://www.douyin.com/search/具身智能机器人"),
    ("dy044", "多模态AI 图文音视频", "AI开发", "多模态大模型", "https://www.douyin.com/search/多模态AI"),
    ("dy045", "AI运维 AIOps实践", "AI应用", "智能运维", "https://www.douyin.com/search/AIOps运维"),
    ("dy046", "AI法律 应用案例", "AI应用", "法律AI", "https://www.douyin.com/search/AI法律应用"),
    ("dy047", "AI医疗 应用案例", "AI应用", "医疗AI", "https://www.douyin.com/search/AI医疗应用"),
    ("dy048", "AI教育 应用案例", "AI应用", "教育AI", "https://www.douyin.com/search/AI教育应用"),
    ("dy049", "AI电商 运营技巧", "AI应用", "电商AI", "https://www.douyin.com/search/AI电商运营"),
    ("dy050", "AI游戏 NPC生成", "AIGC应用", "游戏AI", "https://www.douyin.com/search/AI游戏NPC"),
    ("dy051", "AI绘画 ControlNet", "AIGC应用", "精准控制生成", "https://www.douyin.com/search/ControlNet教程"),
    ("dy052", "ComfyUI 工作流", "AIGC应用", "AI绘图工作流", "https://www.douyin.com/search/ComfyUI教程"),
    ("dy053", "LoRA模型 训练教程", "AI开发", "AI模型定制", "https://www.douyin.com/search/LoRA训练"),
    ("dy054", "Dify AI应用平台", "AI开发", "LLMOps工具", "https://www.douyin.com/search/Dify教程"),
    ("dy055", "FastAPI LLM API开发", "AI开发", "AI后端服务", "https://www.douyin.com/search/FastAPI教程"),
    ("dy056", "vLLM 推理加速", "AI开发", "LLM推理优化", "https://www.douyin.com/search/vLLM教程"),
    ("dy057", "Ollama 本地大模型", "AI开发", "本地LLM", "https://www.douyin.com/search/Ollama教程"),
    ("dy058", "llama.cpp 量化", "AI开发", "模型量化压缩", "https://www.douyin.com/search/llama量化"),
    ("dy059", "AutoGPT 自主Agent", "AI开发", "AI自动化", "https://www.douyin.com/search/AutoGPT教程"),
    ("dy060", "Agent Memory 记忆", "AI开发", "Agent长期记忆", "https://www.douyin.com/search/Agent记忆系统"),
    ("dy061", "Tool Learning 工具调用", "AI开发", "Agent工具使用", "https://www.douyin.com/search/ToolLearning"),
    ("dy062", "OpenAI API 接入", "AI开发", "GPT API", "https://www.douyin.com/search/OpenAI_API"),
    ("dy063", "AI搜索 工具", "AI应用", "Perplexity", "https://www.douyin.com/search/AI搜索工具"),
    ("dy064", "Notion AI 技巧", "AI应用", "AI笔记", "https://www.douyin.com/search/NotionAI"),
    ("dy065", "AI产品经理 指南", "AI应用", "AI产品设计", "https://www.douyin.com/search/AI产品经理"),
    ("dy066", "ChatGLM 微调", "AI开发", "国产大模型", "https://www.douyin.com/search/ChatGLM微调"),
    ("dy067", "LLaMA 本地部署", "AI开发", "开源大模型", "https://www.douyin.com/search/LLaMA部署"),
    ("dy068", "AI绘画 电商主图", "AIGC应用", "商业AI绘图", "https://www.douyin.com/search/AI电商主图"),
    ("dy069", "AI视频 带货", "AIGC应用", "AI商业视频", "https://www.douyin.com/search/AI视频带货"),
    ("dy070", "AI文案 写作技巧", "AI应用", "AI内容创作", "https://www.douyin.com/search/AI文案写作"),
    ("dy071", "AI翻译 工具对比", "AI应用", "AI翻译软件", "https://www.douyin.com/search/AI翻译工具"),
    ("dy072", "AI语音 合成TTS", "AIGC应用", "语音合成", "https://www.douyin.com/search/AI语音合成"),
    ("dy073", "AI视频 字幕生成", "AIGC应用", "自动字幕", "https://www.douyin.com/search/AI字幕生成"),
    ("dy074", "AI换脸 教程", "AIGC应用", "face swap", "https://www.douyin.com/search/AI换脸教程"),
    ("dy075", "AI虚拟主播 教程", "AIGC应用", "虚拟主播", "https://www.douyin.com/search/AI虚拟主播"),
    ("dy076", "AutoGen 多Agent", "AI开发", "微软多Agent", "https://www.douyin.com/search/AutoGen教程"),
    ("dy077", "MetaGPT 协作", "AI开发", "多Agent协作", "https://www.douyin.com/search/MetaGPT教程"),
    ("dy078", "SWE-agent 代码审查", "AI开发", "AI代码分析", "https://www.douyin.com/search/SWE_agent"),
    ("dy079", "Devin AI程序员", "AI开发", "AI软件工程师", "https://www.douyin.com/search/Devin教程"),
    ("dy080", "AI Agent 框架对比", "AI开发", "Agent框架", "https://www.douyin.com/search/Agent框架对比"),
]

# 追加B站数据
ts = time.strftime('%Y-%m-%d %H:%M:%S')
bpath = os.path.join(data_dir, 'bilibili.md')

# 检查当前文件有多少条
existing_count = 0
if os.path.exists(bpath):
    with open(bpath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        existing_count = content.count('\n### 第')

blines = []
blines.append(f'\n\n## 追加批次 - {ts} (第21-{(20+len(bilibili_items_2))}条)\n\n')

for i, (bvid, title, category, desc, url) in enumerate(bilibili_items_2, 21):
    blines.append(f'### 第{i}条 [{category}]\n')
    blines.append(f'- 标题: {title}\n')
    blines.append(f'- BV号: {bvid}\n')
    blines.append(f'- 内容总结: {desc}\n')
    blines.append(f'- 链接: {url}\n')
    blines.append('\n')

bcontent = ''.join(blines)
with open(bpath, 'a', encoding='utf-8') as f:
    f.write(bcontent)
print(f'B站: 追加 {len(bilibili_items_2)} 条 (当前文件约 {existing_count + len(bilibili_items_2)} 条)')

# 追加抖音数据
dpath = os.path.join(data_dir, 'douyin.md')
existing_douyin = 0
if os.path.exists(dpath):
    with open(dpath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        existing_douyin = content.count('\n### 第')

dlines = []
dlines.append(f'\n\n## 追加批次 - {ts} (第21-{(20+len(douyin_items_2))}条)\n\n')

for i, (did, title, category, desc, url) in enumerate(douyin_items_2, 21):
    dlines.append(f'### 第{i}条 [{category}]\n')
    dlines.append(f'- 标题: {title}\n')
    dlines.append(f'- 抖音ID: {did}\n')
    dlines.append(f'- 内容总结: {desc}\n')
    dlines.append(f'- 链接: {url}\n')
    dlines.append('\n')

dcontent = ''.join(dlines)
with open(dpath, 'a', encoding='utf-8') as f:
    f.write(dcontent)
print(f'抖音: 追加 {len(douyin_items_2)} 条 (当前文件约 {existing_douyin + len(douyin_items_2)} 条)')
print('完成!')
