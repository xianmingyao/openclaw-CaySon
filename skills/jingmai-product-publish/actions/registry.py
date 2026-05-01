"""Action registry and execution hooks."""

import time
from typing import Any, Dict, List, Optional


class ActionRegistry:
    """Decorator-based action registry."""

    _actions: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register(cls, name: str, category: str, description: str = ""):
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
        return cls._actions.get(name)

    @classmethod
    def execute(cls, action_name: str, **kwargs) -> Any:
        action = cls._actions.get(action_name)
        if not action:
            raise ValueError(f"Unknown action: {action_name}")

        start_time = time.time()
        log = kwargs.get("log")

        try:
            result = action["func"](**kwargs)
        except Exception as exc:
            elapsed = time.time() - start_time
            if log:
                log.debug(f"[ActionHook] {action_name} failed ({elapsed:.2f}s): {exc}")
            raise

        elapsed = time.time() - start_time
        if log and elapsed > 2.0:
            log.debug(f"[ActionHook] {action_name} took {elapsed:.2f}s")

        return result

    @classmethod
    def list_actions(cls, category: str = None) -> List[str]:
        if category:
            return [name for name, info in cls._actions.items() if info["category"] == category]
        return list(cls._actions.keys())

    @classmethod
    def list_categories(cls) -> Dict[str, int]:
        cats: Dict[str, int] = {}
        for info in cls._actions.values():
            cat = info["category"]
            cats[cat] = cats.get(cat, 0) + 1
        return cats

    @classmethod
    def summary(cls) -> str:
        cats = cls.list_categories()
        total = len(cls._actions)
        lines = [f"ActionRegistry: {total} actions"]
        for cat, count in sorted(cats.items()):
            lines.append(f"  {cat}: {count}")
        return "\n".join(lines)


def auto_discover():
    from actions import form, navigation, popup, verification, window

    return ActionRegistry.summary()
