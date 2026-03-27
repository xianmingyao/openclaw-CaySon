#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Windows Control Action 注册表

参考 UFO/ufo/automator/ui_control/controller.py:_command_registry

提供 UFO 风格的动作注册机制

使用方式:
    from actions.action_registry import get_registry
    registry = get_registry()
    registry.print_summary()
"""

import inspect
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type

# 尝试导入 BaseAction
BaseAction = None
try:
    # 优先使用 jingmai-agent 的 BaseAction
    sys.path.insert(0, r"E:\PY\jingmai-agent")
    from app.service.skills.base_action import (
        BaseAction,
        ActionParameter,
        ActionResult,
    )
except ImportError:
    # 降级：创建简化的 BaseAction
    from pydantic import BaseModel

    class ActionParameter(BaseModel):
        name: str
        type: str = "string"
        description: str = ""
        required: bool = True
        default: Any = None
        enum: Optional[List[Any]] = None

    class ActionResult(BaseModel):
        success: bool = False
        data: Optional[Dict] = None
        error: Optional[str] = None
        metadata: Dict = {}

    class BaseAction:
        name: str = ""
        description: str = ""
        parameters: List[ActionParameter] = []

        def get_schema(self) -> Dict[str, Any]:
            properties = {}
            required = []
            for param in self.parameters:
                properties[param.name] = {
                    "type": param.type,
                    "description": param.description
                }
                if param.default is not None:
                    properties[param.name]["default"] = param.default
                if param.required:
                    required.append(param.name)
            return {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }


class ActionRegistry:
    """
    动作注册表

    管理所有注册的 Actions
    """

    _instance: Optional['ActionRegistry'] = None
    _actions: Dict[str, Type[BaseAction]] = {}
    _categories: Dict[str, List[str]] = {}
    _llm_visible: Dict[str, bool] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._actions:
            self._discover_actions()

    def _discover_actions(self):
        """自动发现并注册 Actions"""
        # 扫描 actions 目录
        actions_dir = Path(__file__).parent

        modules = [
            "mouse_actions",
            "keyboard_actions",
            "scroll_actions",
            "system_actions",
            "shell_actions",
            "window_actions",
            "ui_collect_actions",
            "info_actions",
            "office_actions",
            "web_actions",
            "advanced_mouse_actions",
        ]

        for module_name in modules:
            module_path = actions_dir / f"{module_name}.py"
            if module_path.exists():
                self._import_module(module_name, actions_dir)

        # 也尝试从 jingmai-agent 导入
        jm_path = Path(r"E:\PY\jingmai-agent\app\service\actions")
        if jm_path.exists():
            for module_name in modules:
                if module_name not in self._actions:
                    self._import_module_from_path(module_name, jm_path)

    def _import_module(self, module_name: str, base_path: Path):
        """从本地 actions 目录导入模块"""
        try:
            spec = __import__(
                f"actions.{module_name}",
                fromlist=[""],
                level=0
            )
            self._scan_module(spec, module_name)
        except ImportError:
            pass

    def _import_module_from_path(self, module_name: str, base_path: Path):
        """从 jingmai-agent 导入模块"""
        try:
            sys.path.insert(0, str(base_path.parent.parent.parent))
            module = __import__(
                f"app.service.actions.{module_name}",
                fromlist=[""]
            )
            mod = getattr(module, module_name, None)
            if mod:
                self._scan_module(mod, module_name)
        except (ImportError, AttributeError):
            pass

    def _scan_module(self, module, category: str):
        """扫描模块中的所有 Action 类"""
        for name, obj in inspect.getmembers(module):
            if (
                inspect.isclass(obj)
                and hasattr(obj, "name")
                and obj.name
                and hasattr(obj, "description")
            ):
                # 排除基类
                if name in ("BaseAction", "UFOBaseAction", "Action"):
                    continue

                # 判断是否 LLM 可见
                llm_visible = True
                # 以下 Action 默认不可见（Operator 坐标风格）
                invisible_patterns = [
                    "Click", "DoubleClick", "Drag", "Move", "Type",
                    "Keypress", "Scroll", "Wait", "NoAction",
                    "GetSystemInfo", "GetFileInfo", "FindFiles",
                    "ListFiles", "CheckFileExists", "ChangeDirectory",
                    "GetCurrentDirectory"
                ]
                if any(p in name for p in invisible_patterns):
                    llm_visible = False

                self.register(obj, category, llm_visible=llm_visible)

    def register(
        self,
        action_class: Type[BaseAction],
        category: str = "general",
        aliases: List[str] = None,
        llm_visible: bool = True
    ):
        """注册一个 Action"""
        name = action_class.name
        if not name or name in self._actions:
            return

        self._actions[name] = action_class
        self._llm_visible[name] = llm_visible

        if category not in self._categories:
            self._categories[category] = []
        if name not in self._categories[category]:
            self._categories[category].append(name)

    def get(self, name: str) -> Optional[Type[BaseAction]]:
        """获取 Action"""
        return self._actions.get(name)

    def get_all(self) -> Dict[str, Type[BaseAction]]:
        """获取所有 Actions"""
        return self._actions.copy()

    def get_by_category(self, category: str) -> Dict[str, Type[BaseAction]]:
        """按分类获取"""
        return {
            name: self._actions[name]
            for name in self._categories.get(category, [])
            if name in self._actions
        }

    def get_llm_visible(self) -> Dict[str, Type[BaseAction]]:
        """获取 LLM 可见的 Actions"""
        return {
            name: action
            for name, action in self._actions.items()
            if self._llm_visible.get(name, True)
        }

    def get_categories(self) -> List[str]:
        """获取所有分类"""
        return list(self._categories.keys())

    def is_llm_visible(self, name: str) -> bool:
        """检查是否 LLM 可见"""
        return self._llm_visible.get(name, True)

    def get_schema(self, name: str) -> Optional[Dict[str, Any]]:
        """获取 JSON Schema"""
        action_class = self.get(name)
        if action_class and hasattr(action_class, "get_schema"):
            return action_class.get_schema()
        return None

    def get_all_schemas(self, llm_only: bool = False) -> List[Dict[str, Any]]:
        """获取所有 Schema"""
        actions = self.get_llm_visible() if llm_only else self.get_all()
        return [
            action.get_schema()
            for action in actions.values()
            if hasattr(action, "get_schema")
        ]

    def print_summary(self):
        """打印摘要"""
        print(f"\n{'='*60}")
        print("Windows Control Action Registry")
        print(f"{'='*60}")
        print(f"Total Actions: {len(self._actions)}")
        print(f"LLM Visible: {sum(1 for v in self._llm_visible.values() if v)}")
        print(f"Internal: {sum(1 for v in self._llm_visible.values() if not v)}")
        print(f"\nCategories:")
        for cat, names in self._categories.items():
            visible = sum(1 for n in names if self._llm_visible.get(n, True))
            print(f"  {cat}: {len(names)} actions ({visible} visible)")
        print(f"{'='*60}\n")


# 全局注册表
_registry: Optional[ActionRegistry] = None


def get_registry() -> ActionRegistry:
    """获取注册表单例"""
    global _registry
    if _registry is None:
        _registry = ActionRegistry()
    return _registry


# 装饰器
def register_action(
    category: str = "general",
    llm_visible: bool = True
) -> Callable:
    """Action 注册装饰器"""
    def decorator(cls):
        get_registry().register(cls, category, llm_visible=llm_visible)
        return cls
    return decorator


__all__ = [
    "ActionRegistry",
    "get_registry",
    "register_action",
]
