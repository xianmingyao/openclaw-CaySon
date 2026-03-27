#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
技能加载器
从文件系统或配置动态加载技能
"""
from typing import Dict, List, Optional, Type, Any
from pathlib import Path
from loguru import logger
import importlib
import importlib.util
import json
import yaml

from app.service.skills.skill import Skill, SkillCategory, SkillBuilder
from app.service.skills.base_action import BaseAction
from app.service.skills.skill_registry import SkillRegistry
from app.service.base import BaseService


class SkillLoadError(Exception):
    """技能加载异常"""
    pass


class SkillLoader(BaseService):
    """
    技能加载器

    支持从以下来源加载技能：
    1. Python 模块（.py 文件）
    2. YAML 配置文件
    3. 动态注册的技能类
    """

    def __init__(self, registry: Optional[SkillRegistry] = None):
        """
        初始化技能加载器

        Args:
            registry: 技能注册表（可选）
        """
        super().__init__()
        self._registry = registry
        self._loaded_skills: Dict[str, Skill] = {}

    async def initialize(self):
        """初始化加载器"""
        if self._registry is None:
            self._registry = SkillRegistry()
            await self._registry.initialize()

        logger.info("技能加载器初始化完成")

    async def load_from_directory(
        self,
        directory: str,
        pattern: str = "*.py",
        auto_register: bool = True
    ) -> List[Skill]:
        """
        从目录加载技能模块

        支持加载:
        1. .py 模块文件 (pattern 匹配)
        2. SKILL.md 文件 (CoPaw 架构: YAML front matter + Markdown body)

        Args:
            directory: 目录路径
            pattern: 文件匹配模式 (用于 .py 文件)
            auto_register: 是否自动注册到注册表

        Returns:
            List[Skill]: 加载的技能列表
        """
        dir_path = Path(directory)
        if not dir_path.exists():
            logger.warning(f"Skill directory not found: {directory}")
            return []

        skills = []

        # 加载 .py 模块文件
        for file_path in dir_path.glob(pattern):
            if file_path.name.startswith("_"):
                continue

            try:
                skill = await self.load_from_module(str(file_path))

                if skill:
                    skills.append(skill)

                    if auto_register and self._registry:
                        await self._registry.register_skill(skill)

            except Exception as e:
                logger.error(
                    f"Failed to load skill from {file_path}: {str(e)}"
                )

        # 加载 SKILL.md 文件 (CoPaw: 目录即技能)
        for file_path in dir_path.glob("SKILL.md"):
            try:
                skill = await self.load_from_skill_md(str(file_path), auto_register=auto_register)
                if skill:
                    skills.append(skill)
            except Exception as e:
                logger.error(
                    f"Failed to load skill from SKILL.md {file_path}: {str(e)}"
                )

        # 加载子目录中的 SKILL.md (CoPaw: 一级子目录各为一个技能)
        for sub_dir in dir_path.iterdir():
            if sub_dir.is_dir() and not sub_dir.name.startswith("_"):
                skill_md = sub_dir / "SKILL.md"
                if skill_md.exists():
                    try:
                        skill = await self.load_from_skill_md(str(skill_md), auto_register=auto_register)
                        if skill:
                            skills.append(skill)
                    except Exception as e:
                        logger.error(
                            f"Failed to load skill from {skill_md}: {str(e)}"
                        )

        logger.info(f"Loaded {len(skills)} skills from {directory}")
        return skills

    async def load_from_skill_md(
        self,
        skill_md_path: str,
        auto_register: bool = True
    ) -> Optional[Skill]:
        """
        从 SKILL.md 文件加载技能 (CoPaw 架构)

        SKILL.md 格式: YAML front matter (---包裹) + Markdown body
        YAML front matter: 技能元数据 (name, description, category, version, author)
        Markdown body: 技能内容 (作为 Agent prompt 注入)

        Args:
            skill_md_path: SKILL.md 文件路径
            auto_register: 是否自动注册到注册表

        Returns:
            Optional[Skill]: 加载的技能
        """
        try:
            with open(skill_md_path, "r", encoding="utf-8") as f:
                raw = f.read()

            # 分离 YAML front matter 和 Markdown body
            if not raw.startswith("---"):
                raise SkillLoadError(f"SKILL.md must start with '---': {skill_md_path}")

            # 找到第二个 ---
            parts = raw.split("---", 2)
            if len(parts) < 3:
                raise SkillLoadError(f"SKILL.md must have closing '---': {skill_md_path}")

            front_matter = parts[1].strip()
            content = parts[2].strip()  # Markdown body (技能内容)

            # 解析 YAML front matter
            config = yaml.safe_load(front_matter)
            if not isinstance(config, dict):
                raise SkillLoadError(f"Invalid YAML front matter in {skill_md_path}")

            # 构建 Skill 对象
            builder = SkillBuilder(name=config.get("name", "unknown"))
            builder.description(config.get("description", ""))
            builder.content(content)

            # 解析 category
            if "category" in config:
                cat_str = str(config["category"]).upper()
                try:
                    builder.category(SkillCategory[cat_str])
                except KeyError:
                    logger.warning(f"Unknown category: {cat_str}, using CUSTOM")
                    builder.category(SkillCategory.CUSTOM)

            if "version" in config:
                builder.version(str(config["version"]))
            if "author" in config:
                builder.author(str(config["author"]))
            if "metadata" in config and isinstance(config["metadata"], dict):
                builder.metadata(**config["metadata"])

            skill = builder.build()

            self._loaded_skills[skill.name] = skill
            logger.info(
                f"Loaded skill '{skill.name}' from SKILL.md ({skill_md_path}), "
                f"content length={len(content)} chars"
            )

            if auto_register and self._registry:
                await self._registry.register_skill(skill)

            return skill

        except FileNotFoundError:
            raise SkillLoadError(f"SKILL.md not found: {skill_md_path}")
        except yaml.YAMLError as e:
            raise SkillLoadError(f"YAML parsing failed: {str(e)}")
        except Exception as e:
            if isinstance(e, SkillLoadError):
                raise
            raise SkillLoadError(f"Failed to load SKILL.md: {str(e)}")

    async def load_from_module(
        self,
        module_path: str
    ) -> Optional[Skill]:
        """
        从 Python 模块加载技能

        Args:
            module_path: 模块路径（文件路径或模块名）

        Returns:
            Optional[Skill]: 加载的技能
        """
        try:
            # 判断是文件路径还是模块名
            path = Path(module_path)

            if path.exists() and path.suffix == ".py":
                # 从文件加载
                spec = importlib.util.spec_from_file_location(
                    path.stem,
                    module_path
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                else:
                    raise SkillLoadError(f"Cannot load module from {module_path}")
            else:
                # 从模块名加载
                module = importlib.import_module(module_path)

            # 查找技能定义
            skill = self._extract_skill_from_module(module)

            if skill:
                self._loaded_skills[skill.name] = skill
                logger.info(f"Loaded skill '{skill.name}' from {module_path}")

            return skill

        except ImportError as e:
            raise SkillLoadError(f"Module import failed: {str(e)}")
        except Exception as e:
            raise SkillLoadError(f"Failed to load from module: {str(e)}")

    def _extract_skill_from_module(self, module: Any) -> Optional[Skill]:
        """
        从模块对象中提取技能定义

        Args:
            module: 模块对象

        Returns:
            Optional[Skill]: 技能对象
        """
        # 方法 1：查找 SKILL 变量
        if hasattr(module, "SKILL"):
            return module.SKILL

        # 方法 2：查找 get_skill() 函数
        if hasattr(module, "get_skill"):
            if callable(module.get_skill):
                return module.get_skill()

        # 方法 3：查找 Skill 类的子类并实例化
        for attr_name in dir(module):
            attr = getattr(module, attr_name)

            try:
                # 检查是否是 Skill 的子类（排除 Skill 本身）
                if (
                    isinstance(attr, type) and
                    issubclass(attr, Skill) and
                    attr != Skill
                ):
                    # 尝试实例化（无参数）
                    try:
                        return attr()
                    except:
                        pass
            except TypeError:
                continue

        return None

    async def load_from_yaml(
        self,
        yaml_path: str,
        auto_register: bool = True
    ) -> Optional[Skill]:
        """
        从 YAML 配置文件加载技能

        Args:
            yaml_path: YAML 文件路径
            auto_register: 是否自动注册到注册表

        Returns:
            Optional[Skill]: 加载的技能
        """
        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            skill = self._parse_skill_config(config)

            if skill:
                self._loaded_skills[skill.name] = skill
                logger.info(f"Loaded skill '{skill.name}' from {yaml_path}")

                if auto_register and self._registry:
                    await self._registry.register_skill(skill)

            return skill

        except FileNotFoundError:
            raise SkillLoadError(f"YAML file not found: {yaml_path}")
        except yaml.YAMLError as e:
            raise SkillLoadError(f"YAML parsing failed: {str(e)}")
        except Exception as e:
            raise SkillLoadError(f"Failed to load from YAML: {str(e)}")

    def _parse_skill_config(self, config: Dict[str, Any]) -> Skill:
        """
        解析技能配置

        Args:
            config: 配置字典

        Returns:
            Skill: 技能对象
        """
        # 构建技能
        builder = SkillBuilder(
            name=config.get("name", "unknown")
        )

        # 设置基本属性
        if "description" in config:
            builder.description(config["description"])

        if "category" in config:
            cat_str = config["category"].upper()
            try:
                category = SkillCategory[cat_str]
                builder.category(category)
            except KeyError:
                logger.warning(f"Unknown category: {cat_str}, using CUSTOM")
                builder.category(SkillCategory.CUSTOM)

        if "version" in config:
            builder.version(config["version"])

        if "author" in config:
            builder.author(config["author"])

        if "metadata" in config:
            builder.metadata(**config["metadata"])

        # 加载动作
        actions_config = config.get("actions", [])
        for action_config in actions_config:
            action = self._create_action_from_config(action_config)
            if action:
                builder.add_action(action)

        return builder.build()

    def _create_action_from_config(
        self,
        config: Dict[str, Any]
    ) -> Optional[Type[BaseAction]]:
        """
        从配置创建动作类

        Args:
            config: 动作配置

        Returns:
            Optional[Type[BaseAction]]: 动作类
        """
        from app.service.skills.base_action import (
            ActionParameter, ParameterType, ActionResult
        )

        action_name = config.get("name", "unknown")
        description = config.get("description", "")

        # 创建动态动作类
        class ConfiguredAction(BaseAction):
            name = action_name
            description = description
            parameters = []

            async def _execute(self, **kwargs):
                # 这里可以实现从配置加载的动作逻辑
                # 例如调用外部命令、API 等
                return ActionResult(
                    success=True,
                    data={"message": f"Action {action_name} executed"}
                )

        # 添加参数定义
        params_config = config.get("parameters", [])
        for param_config in params_config:
            try:
                param_type = ParameterType.STRING
                if "type" in param_config:
                    type_str = param_config["type"].upper()
                    if type_str in ParameterType.__members__:
                        param_type = ParameterType[type_str]

                param = ActionParameter(
                    name=param_config.get("name", "param"),
                    type=param_type,
                    description=param_config.get("description", ""),
                    required=param_config.get("required", True),
                    default=param_config.get("default"),
                    enum=param_config.get("enum")
                )
                ConfiguredAction.parameters.append(param)
            except Exception as e:
                logger.warning(
                    f"Failed to parse parameter {param_config.get('name')}: {e}"
                )

        return ConfiguredAction

    async def load_builtin_skills(
        self,
        skills_dir: str = "resources"
    ) -> List[Skill]:
        """
        加载内置技能 (从 resources/ 目录加载 SKILL.md)

        Args:
            skills_dir: 技能目录

        Returns:
            List[Skill]: 加载的技能列表
        """
        return await self.load_from_directory(skills_dir)

    def create_skill_from_actions(
        self,
        name: str,
        description: str,
        actions: List[Type[BaseAction]],
        category: SkillCategory = SkillCategory.CUSTOM,
        **metadata
    ) -> Skill:
        """
        从动作列表创建技能

        Args:
            name: 技能名称
            description: 技能描述
            actions: 动作类列表
            category: 技能分类
            **metadata: 元数据

        Returns:
            Skill: 技能对象
        """
        builder = SkillBuilder(name)
        builder.description(description)
        builder.category(category)
        builder.metadata(**metadata)

        for action_class in actions:
            builder.add_action(action_class)

        skill = builder.build()
        self._loaded_skills[skill.name] = skill

        logger.info(f"Created skill '{skill.name}' with {len(actions)} actions")
        return skill

    def get_loaded_skill(self, skill_name: str) -> Optional[Skill]:
        """
        获取已加载的技能

        Args:
            skill_name: 技能名称

        Returns:
            Optional[Skill]: 技能对象
        """
        return self._loaded_skills.get(skill_name)

    def list_loaded_skills(self) -> List[str]:
        """
        列出已加载的技能名称

        Returns:
            List[str]: 技能名称列表
        """
        return list(self._loaded_skills.keys())

    async def unload_skill(self, skill_name: str) -> bool:
        """
        卸载技能

        Args:
            skill_name: 技能名称

        Returns:
            bool: 是否成功
        """
        if skill_name not in self._loaded_skills:
            logger.warning(f"Skill '{skill_name}' not loaded")
            return False

        # 从注册表注销
        if self._registry:
            await self._registry.unregister_skill(skill_name)

        # 从已加载列表移除
        del self._loaded_skills[skill_name]

        logger.info(f"Unloaded skill: {skill_name}")
        return True

    async def reload_skill(
        self,
        skill_name: str,
        module_path: str
    ) -> Optional[Skill]:
        """
        重新加载技能

        Args:
            skill_name: 技能名称
            module_path: 模块路径

        Returns:
            Optional[Skill]: 重新加载的技能
        """
        await self.unload_skill(skill_name)
        return await self.load_from_module(module_path)


__all__ = [
    'SkillLoadError',
    'SkillLoader',
]
