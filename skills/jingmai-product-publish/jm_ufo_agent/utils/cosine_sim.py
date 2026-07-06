"""向量相似度工具。"""

from __future__ import annotations

import math
from collections.abc import Sequence


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    """计算两个向量的余弦相似度。

    # 向量维度必须一致，否则相似度没有意义。
    # 任一向量为零向量时返回 0，避免除零并表达“没有方向信息”。
    # 该函数不依赖 numpy，便于在最小环境下跑单测。
    """

    if len(left) != len(right):
        raise ValueError("向量维度不一致")
    dot = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)
