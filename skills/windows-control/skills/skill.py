#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
技能定义
定义技能的数据结构和封装
"""
from typing import Dict, Any, List, Optional, Type
from pydantic import BaseModel, Field
from enum import Enum
from loguru import logger

from app.service.skills.base_action import BaseAction


class SkillCategory(str, Enum):
    """技能分类枚举"""
    AUTOMATION = "automation"      # 自动化类
    KNOWLEDGE = "knowledge"        # 知识检索类
    MEMORY = "memory"             # 记忆管理类
    COMMUNICATION = "communication"  # 通信类
    UTILITY = "utility"            # 工具类
    CUSTOM = "custom"              # 自定义


class Skill(BaseModel):
    """
    技能定义

    技能是一组相关动作的集合，代表 Agent 可以执行的一个功能模块
    """
    name: str = Field(description="技能名称")
    description: str = Field(description="技能描述")
    category: SkillCategory = Field(description="技能分类")
    version: str = Field(default="1.0.0", description="技能版本")
    author: str = Field(default="", description="作者")
    actions: Dict[str, Type[BaseAction]] = Field(
        default_factory=dict,
        description="动作映射 {action_name: action_class}"
    )
    content: str = Field(default="", description="技能内容 (SKILL.md Markdown 正文，用于 prompt 注入)")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="元数据"
    )
    enabled: bool = Field(default=True, description="是否启用")

    class Config:
        from_attributes = True

    def register_action(self, action_class: Type[BaseAction]) -> None:
        """
        注册动作到技能

        Args:
            action_class: 动作类
        """
        action = action_class()
        self.actions[action.name] = action_class
        logger.debug(f"Registered action '{action.name}' to skill '{self.name}'")

    def get_action(self, action_name: str) -> Optional[Type[BaseAction]]:
        """
        获取动作类

        Args:
            action_name: 动作名称

        Returns:
            Optional[Type[BaseAction]]: 动作类，不存在则返回 None
        """
        return self.actions.get(action_name)

    def list_actions(self) -> List[str]:
        """
        列出所有动作名称

        Returns:
            List[str]: 动作名称列表
        """
        return list(self.actions.keys())

    async def execute_action(
        self,
        action_name: str,
        **kwargs
    ) -> Any:
        """
        执行动作

        Args:
            action_name: 动作名称
            **kwargs: 动作参数

        Returns:
            Any: 执行结果

        Raises:
            ValueError: 动作不存在
        """
        action_class = self.get_action(action_name)
        if not action_class:
            raise ValueError(
                f"Action '{action_name}' not found in skill '{self.name}'"
            )

        action = action_class()
        return await action.execute(**kwargs)

    def get_schema(self) -> Dict[str, Any]:
        """
        获取技能的 JSON Schema

        Returns:
            Dict[str, Any]: JSON Schema
        """
        actions_schema = {}
        for action_name, action_class in self.actions.items():
            action = action_class()
            actions_schema[action_name] = action.get_schema()

        return {
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "version": self.version,
            "author": self.author,
            "actions": actions_schema,
            "enabled": self.enabled
        }

    def create_embedding_text(self) -> str:
        """
        创建用于嵌入生成的文本

        Returns:
            str: 技能描述文本
        """
        parts = [
            f"技能: {self.name}",
            f"描述: {self.description}",
            f"分类: {self.category.value}",
            f"版本: {self.version}"
        ]

        # 添加动作描述
        if self.actions:
            action_descriptions = []
            for action_name, action_class in self.actions.items():
                action = action_class()
                action_descriptions.append(
                    f"- {action.name}: {action.description}"
                )
            parts.append("动作:\n" + "\n".join(action_descriptions))

        return "\n".join(parts)


class SkillBuilder:
    """
    技能构建器

    提供流式 API 构建 Skill 对象
    """

    def __init__(self, name: str):
        """
        初始化构建器

        Args:
            name: 技能名称
        """
        self._name = name
        self._description = ""
        self._category = SkillCategory.CUSTOM
        self._version = "1.0.0"
        self._author = ""
        self._actions = {}
        self._content = ""
        self._metadata = {}

    def description(self, desc: str) -> 'SkillBuilder':
        """设置描述"""
        self._description = desc
        return self

    def category(self, cat: SkillCategory) -> 'SkillBuilder':
        """设置分类"""
        self._category = cat
        return self

    def version(self, ver: str) -> 'SkillBuilder':
        """设置版本"""
        self._version = ver
        return self

    def author(self, auth: str) -> 'SkillBuilder':
        """设置作者"""
        self._author = auth
        return self

    def content(self, text: str) -> 'SkillBuilder':
        """设置技能内容 (SKILL.md Markdown 正文)"""
        self._content = text
        return self

    def add_action(self, action_class: Type[BaseAction]) -> 'SkillBuilder':
        """添加动作"""
        action = action_class()
        self._actions[action.name] = action_class
        return self

    def add_actions(self, *action_classes: Type[BaseAction]) -> 'SkillBuilder':
        """批量添加动作"""
        for action_class in action_classes:
            self.add_action(action_class)
        return self

    def metadata(self, **meta) -> 'SkillBuilder':
        """添加元数据"""
        self._metadata.update(meta)
        return self

    def build(self) -> Skill:
        """
        构建技能对象

        Returns:
            Skill: 技能对象
        """
        return Skill(
            name=self._name,
            description=self._description,
            category=self._category,
            version=self._version,
            author=self._author,
            actions=self._actions,
            content=self._content,
            metadata=self._metadata
        )


__all__ = [
    'SkillCategory',
    'Skill',
    'SkillBuilder',
]
