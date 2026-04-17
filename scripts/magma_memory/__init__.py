# -*- coding: utf-8 -*-
"""
MAGMA-inspired 四维图谱记忆系统
Multi-Atlas Generative Memory Agent

四维记忆：
- 语义维度（Semantic）: 概念、含义、主题关联
- 时间维度（Temporal）: 时序、先后、演化过程  
- 因果维度（Causal）: 原因结果、逻辑链条
- 实体维度（Entity）: 人物、地点、事件对象
"""

from .core import MemoryNode, MemoryGraph
from .retrieval import retrieve

__version__ = "1.0.0"
__all__ = ["MemoryNode", "MemoryGraph", "retrieve"]
