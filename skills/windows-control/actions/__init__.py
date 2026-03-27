#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Windows Control Actions

提供完整的 Windows UI 自动化 Action 体系

使用方式:
    from actions.registry import get_registry
    registry = get_registry()
"""

# Action 注册表
from actions.action_registry import (
    ActionRegistry,
    get_registry,
    register_action,
)

__all__ = [
    "ActionRegistry",
    "get_registry",
    "register_action",
]
