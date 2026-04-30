"""
京麦商品发布自动化 - Action 注册表
装饰器注册 + 动态发现，302→28 参数化 Action
"""
from typing import Dict, Any, Callable, Optional, List


class ActionRegistry:
    """Action 注册表 — 装饰器模式"""

    _actions: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register(cls, name: str, category: str, description: str = ""):
        """装饰器：注册 Action"""
        def decorator(func):
            cls._actions[name] = {
                "func": func,
                "category": category,
                "description": description or func.__doc__ or "",
            }
            return func
        return decorator

    @classmethod
    def get(cls, name: str) -> Optional[Dict[str, Any]]:
        """获取 Action 信息"""
        return cls._actions.get(name)

    @classmethod
    def execute(cls, name: str, **kwargs) -> Any:
        """执行 Action"""
        action = cls._actions.get(name)
        if not action:
            raise ValueError(f"未知 Action: {name}")
        return action["func"](**kwargs)

    @classmethod
    def list_actions(cls, category: str = None) -> List[str]:
        """列出所有 Action（可按分类过滤）"""
        if category:
            return [name for name, info in cls._actions.items() if info["category"] == category]
        return list(cls._actions.keys())

    @classmethod
    def list_categories(cls) -> Dict[str, int]:
        """列出分类及其 Action 数量"""
        cats: Dict[str, int] = {}
        for info in cls._actions.values():
            cat = info["category"]
            cats[cat] = cats.get(cat, 0) + 1
        return cats

    @classmethod
    def summary(cls) -> str:
        """打印 Action 汇总"""
        cats = cls.list_categories()
        total = len(cls._actions)
        lines = [f"ActionRegistry: {total} actions"]
        for cat, count in sorted(cats.items()):
            lines.append(f"  {cat}: {count}")
        return "\n".join(lines)


def auto_discover():
    """自动发现并导入所有 Action 模块（触发 @register 装饰器）"""
    from actions import window, form, popup, navigation, verification
    return ActionRegistry.summary()
