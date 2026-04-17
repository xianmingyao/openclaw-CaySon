# -*- coding: utf-8 -*-
"""
MAGMA-inspired 四维图谱记忆系统 v2
Multi-Atlas Generative Memory Agent

四维记忆：
- 语义维度（Semantic）: 概念、含义、主题关联
- 时间维度（Temporal）: 时序、先后、演化过程
- 因果维度（Causal）: 原因结果、逻辑链条
- 实体维度（Entity）: 人物、地点、事件对象

功能：
1. 三写：MAGMA图谱 + Mem0向量 + Milvus向量
2. 向量检索融合：语义+图谱+向量三重召回
3. 自动因果学习：基于共现统计和模式匹配
"""

from .core import MemoryNode, MemoryGraph
from .retrieval import retrieve
from .enhanced import MAGMAHybridV2, get_hybrid_v2

__version__ = "2.0.0"
__all__ = ["MemoryNode", "MemoryGraph", "retrieve", "MAGMAHybridV2", "get_hybrid_v2"]
