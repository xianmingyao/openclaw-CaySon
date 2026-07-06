"""哈希工具 — 内容去重与签名计算。

提供确定性哈希计算，用于页面签名、证据去重和状态指纹。
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


def content_hash(data: Any, algorithm: str = "sha256") -> str:
    """计算内容的确定性哈希。

    # 将任意可序列化数据转为 JSON 字符串后计算哈希。
    # sort_keys=True 保证相同内容产生相同哈希。
    # algorithm 支持 sha256（默认）和 md5。
    # 返回十六进制哈希字符串。
    """
    serialized = json.dumps(data, sort_keys=True, ensure_ascii=False, default=str)
    digest = hashlib.new(algorithm, serialized.encode("utf-8"))
    return digest.hexdigest()


def page_signature(
    window_title: str,
    visible_text: str,
    control_types: list[str] | None = None,
) -> str:
    """计算页面状态签名。

    # 基于窗口标题 + 可见文本 + 控件类型列表生成确定性指纹。
    # 用于 OBSERVE_PAGE 判断页面是否发生变化。
    # 控件类型列表可选，提供更精确的签名。
    """
    parts: list[str] = [window_title, visible_text]
    if control_types:
        parts.append(",".join(sorted(control_types)))
    combined = "|".join(parts)
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()[:16]


def evidence_fingerprint(evidence: dict[str, Any]) -> str:
    """计算证据指纹。

    # 对证据字典的所有键值进行排序后哈希。
    # 用于去重检查，避免重复记录相同证据。
    """
    return content_hash(evidence, algorithm="sha256")[:12]


def deduplicate_by_hash(items: list[dict[str, Any]], key: str = "hash") -> list[dict[str, Any]]:
    """根据哈希值去重。

    # 保留每个哈希值的第一次出现。
    # 适用于证据去重、操作轨迹去重等场景。
    """
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for item in items:
        h = item.get(key) or content_hash(item)
        if h not in seen:
            seen.add(h)
            result.append(item)
    return result
