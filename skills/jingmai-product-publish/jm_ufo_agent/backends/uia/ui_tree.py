"""UI 树 — 层次化 UI 结构表示与差异计算。

参考 UFO ui_tree.py 的 UITree 实现，
支持递归构建控件树、宽度优先扁平化、JSON 序列化和差异计算。
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class UITreeNode:
    """UI 树节点 — 表示单个 UI 元素。

    # 参考 UFO ui_tree.py 的节点结构。
    # id 唯一标识节点（通常为控件句柄或自动化 ID）。
    # rectangle 是 (left, top, right, bottom) 绝对像素坐标。
    # level 是树的深度层级，root 为 0。
    # children 是子节点列表。
    """

    id: str
    name: str
    control_type: str
    rectangle: tuple[int, int, int, int]
    level: int = 0
    children: list["UITreeNode"] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """序列化为字典。"""
        return {
            "id": self.id,
            "name": self.name,
            "control_type": self.control_type,
            "rectangle": list(self.rectangle),
            "level": self.level,
            "children": [c.to_dict() for c in self.children],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UITreeNode":
        """从字典反序列化。"""
        children = [cls.from_dict(c) for c in data.get("children", [])]
        rect = tuple(data.get("rectangle", [0, 0, 0, 0]))
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            control_type=data.get("control_type", ""),
            rectangle=rect,  # type: ignore[arg-type]
            level=data.get("level", 0),
            children=children,
        )


@dataclass
class UITreeDiff:
    """UI 树差异。

    # added: 新增节点列表。
    # removed: 移除节点列表。
    # modified: 变更节点列表（属性发生变化但路径不变）。
    """

    added: list[UITreeNode] = field(default_factory=list)
    removed: list[UITreeNode] = field(default_factory=list)
    modified: list[dict[str, Any]] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        """是否有变化。"""
        return bool(self.added or self.removed or self.modified)


class UITree:
    """UI 树 — 层次化 UI 结构表示。

    # 参考 UFO UITree 类。
    # 从 pywinauto 窗口对象递归构建控件树。
    # 支持 JSON 序列化、扁平化和差异计算。
    # 差异计算用于检测页面变化，辅助 OBSERVE_PAGE 节点。
    """

    def __init__(self, root: Any | None = None) -> None:
        """初始化 UI 树。"""
        self.root: UITreeNode | None = None
        if root is not None:
            self.root = self._build_node(root, level=0)

    def to_json(self, indent: int = 2) -> str:
        """序列化为 JSON 字符串。"""
        if self.root is None:
            return "{}"
        return json.dumps(self.root.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> "UITree":
        """从 JSON 字符串反序列化。"""
        tree = cls()
        data = json.loads(json_str)
        tree.root = UITreeNode.from_dict(data)
        return tree

    def flatten(self) -> list[UITreeNode]:
        """宽度优先扁平化控件树。

        # 参考 UFO UITree.flatten_ui_tree。
        # 宽度优先遍历保持层级顺序。
        """
        if self.root is None:
            return []

        result: list[UITreeNode] = []
        queue: list[UITreeNode] = [self.root]
        while queue:
            node = queue.pop(0)
            result.append(node)
            queue.extend(node.children)
        return result

    @staticmethod
    def diff(tree_a: "UITree", tree_b: "UITree") -> UITreeDiff:
        """计算两棵 UI 树的差异。

        # 参考 UFO UITree.ui_tree_diff。
        # 按 id 路径比较节点，检测新增、移除和变更。
        # 返回 UITreeDiff 对象。
        """
        nodes_a = {n.id: n for n in tree_a.flatten()} if tree_a.root else {}
        nodes_b = {n.id: n for n in tree_b.flatten()} if tree_b.root else {}

        added_ids = set(nodes_b.keys()) - set(nodes_a.keys())
        removed_ids = set(nodes_a.keys()) - set(nodes_b.keys())
        common_ids = set(nodes_a.keys()) & set(nodes_b.keys())

        diff = UITreeDiff(
            added=[nodes_b[i] for i in added_ids],
            removed=[nodes_a[i] for i in removed_ids],
        )

        for nid in common_ids:
            a, b = nodes_a[nid], nodes_b[nid]
            changes: dict[str, Any] = {"id": nid}
            has_change = False
            if a.name != b.name:
                changes["name"] = {"before": a.name, "after": b.name}
                has_change = True
            if a.rectangle != b.rectangle:
                changes["rectangle"] = {"before": a.rectangle, "after": b.rectangle}
                has_change = True
            if a.control_type != b.control_type:
                changes["control_type"] = {"before": a.control_type, "after": b.control_type}
                has_change = True
            if has_change:
                diff.modified.append(changes)

        return diff

    def _build_node(self, element: Any, level: int) -> UITreeNode:
        """递归构建 UI 树节点。"""
        try:
            elem_id = str(hash(element)) if not hasattr(element, "element_info") else str(
                getattr(element.element_info, "automation_id", "") or id(element)
            )
            name = ""
            try:
                name = element.window_text() or ""
            except Exception:
                pass

            control_type = ""
            try:
                control_type = element.element_info.control_type or ""
            except Exception:
                pass

            rect = (0, 0, 0, 0)
            try:
                r = element.rectangle()
                rect = (r.left, r.top, r.right, r.bottom)
            except Exception:
                pass

            children: list[UITreeNode] = []
            try:
                for child in element.children():
                    children.append(self._build_node(child, level + 1))
            except Exception:
                pass

            return UITreeNode(
                id=elem_id,
                name=name,
                control_type=control_type,
                rectangle=rect,
                level=level,
                children=children,
            )
        except Exception as exc:
            logger.debug("构建 UI 树节点异常: %s", exc)
            return UITreeNode(id="error", name="", control_type="", rectangle=(0, 0, 0, 0), level=level)
