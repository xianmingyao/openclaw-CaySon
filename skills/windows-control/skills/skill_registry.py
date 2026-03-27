#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
技能注册表
提供技能注册、检索和管理功能
"""
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
from loguru import logger
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime
import hashlib

from app.service.skills.skill import Skill, SkillCategory
from app.service.base import BaseService


class PermissionLevel(Enum):
    """权限级别"""
    # 公开 - 所有用户可访问
    PUBLIC = "public"
    # 基础 - 需要基础用户权限
    BASIC = "basic"
    # 高级 - 需要高级用户权限
    ADVANCED = "advanced"
    # 管理 - 仅管理员可访问
    ADMIN = "admin"
    # 系统 - 系统内部使用
    SYSTEM = "system"


class ExecutionContext(Enum):
    """执行上下文"""
    # CLI 命令行
    CLI = "cli"
    # REST API
    API = "api"
    # WebSocket
    WEBSOCKET = "websocket"
    # 飞书集成
    FEISHU = "feishu"
    # Agent 内部调用
    AGENT_INTERNAL = "agent_internal"
    # 批处理
    BATCH = "batch"


@dataclass
class SkillPermission:
    """技能权限配置"""
    skill_name: str
    permission_level: PermissionLevel = PermissionLevel.PUBLIC
    allowed_contexts: Set[ExecutionContext] = field(default_factory=lambda: {
        ExecutionContext.CLI, ExecutionContext.API
    })
    allowed_roles: Set[str] = field(default_factory=set)
    blocked_roles: Set[str] = field(default_factory=set)
    max_rate_per_minute: Optional[int] = None
    require_confirmation: bool = False
    enabled: bool = True

    def can_access(
        self,
        user_role: str = "user",
        context: ExecutionContext = ExecutionContext.API,
        permission_level: PermissionLevel = PermissionLevel.BASIC
    ) -> Tuple[bool, Optional[str]]:
        """
        检查是否可以访问技能

        Args:
            user_role: 用户角色
            context: 执行上下文
            permission_level: 用户权限级别

        Returns:
            Tuple[bool, Optional[str]]: (是否允许, 拒绝原因)
        """
        # 检查技能是否启用
        if not self.enabled:
            return False, "技能已禁用"

        # 检查角色黑名单
        if user_role in self.blocked_roles:
            return False, f"角色 '{user_role}' 被禁止访问此技能"

        # 检查角色白名单（如果配置了）
        if self.allowed_roles and user_role not in self.allowed_roles:
            return False, f"角色 '{user_role}' 无权访问此技能"

        # 检查上下文
        if context not in self.allowed_contexts:
            return False, f"技能不允许在 '{context.value}' 上下文中执行"

        # 检查权限级别
        level_hierarchy = {
            PermissionLevel.PUBLIC: 0,
            PermissionLevel.BASIC: 1,
            PermissionLevel.ADVANCED: 2,
            PermissionLevel.ADMIN: 3,
            PermissionLevel.SYSTEM: 4
        }

        if level_hierarchy[permission_level] < level_hierarchy[self.permission_level]:
            return False, f"需要 {self.permission_level.value} 权限级别"

        return True, None


@dataclass
class SkillExecutionRecord:
    """技能执行记录"""
    skill_name: str
    timestamp: datetime
    user_role: str
    context: ExecutionContext
    success: bool
    duration_ms: int


class SkillRegistry(BaseService):
    """
    技能注册表

    管理所有已注册的技能，提供：
    1. 技能注册和注销
    2. 两阶段检索（向量粗排 + LLM 精排）
    3. 技能分类过滤
    4. 技能元数据管理
    5. 权限控制和白名单机制
    6. 执行历史和速率限制
    """

    def __init__(self):
        """初始化技能注册表"""
        super().__init__()
        self._skills: Dict[str, Skill] = {}
        self._embeddings: Dict[str, List[float]] = {}
        self._categories: Dict[SkillCategory, List[str]] = {
            cat: [] for cat in SkillCategory
        }

        # 权限管理
        self._permissions: Dict[str, SkillPermission] = {}
        self._global_whitelist: Set[str] = set()
        self._global_blacklist: Set[str] = set()

        # 执行历史（用于速率限制）
        self._execution_history: List[SkillExecutionRecord] = []
        self._max_history_size = 1000

        # 默认权限配置
        self._default_permission = SkillPermission(
            skill_name="",
            permission_level=PermissionLevel.PUBLIC,
            allowed_contexts={
                ExecutionContext.CLI,
                ExecutionContext.API,
                ExecutionContext.AGENT_INTERNAL
            },
            max_rate_per_minute=60
        )

    async def initialize(self):
        """初始化注册表"""
        logger.info("技能注册表初始化完成")

    async def register_skill(
        self,
        skill: Skill,
        embedding: Optional[List[float]] = None,
        permission: Optional[SkillPermission] = None
    ) -> bool:
        """
        注册技能

        Args:
            skill: 技能对象
            embedding: 技能描述嵌入向量（可选，如果不提供将延迟生成）
            permission: 技能权限配置（可选，使用默认配置）

        Returns:
            bool: 是否成功
        """
        try:
            # 检查全局黑名单
            if skill.name in self._global_blacklist:
                logger.warning(f"Skill '{skill.name}' is in global blacklist, skipping")
                return False

            # 检查名称冲突
            if skill.name in self._skills:
                logger.warning(f"Skill '{skill.name}' already registered, updating...")

            self._skills[skill.name] = skill

            # 添加到分类索引
            if skill.category not in self._categories:
                self._categories[skill.category] = []
            if skill.name not in self._categories[skill.category]:
                self._categories[skill.category].append(skill.name)

            # 存储嵌入向量
            if embedding:
                self._embeddings[skill.name] = embedding

            # 设置权限配置
            if permission:
                permission.skill_name = skill.name
                self._permissions[skill.name] = permission
            else:
                # 使用默认配置
                default_perm = SkillPermission(
                    skill_name=skill.name,
                    permission_level=self._default_permission.permission_level,
                    allowed_contexts=self._default_permission.allowed_contexts.copy(),
                    max_rate_per_minute=self._default_permission.max_rate_per_minute
                )
                self._permissions[skill.name] = default_perm

            logger.info(f"Registered skill: {skill.name} ({skill.category.value})")
            return True

        except Exception as e:
            logger.error(f"Failed to register skill '{skill.name}': {str(e)}")
            return False

    async def unregister_skill(self, skill_name: str) -> bool:
        """
        注销技能

        Args:
            skill_name: 技能名称

        Returns:
            bool: 是否成功
        """
        if skill_name not in self._skills:
            logger.warning(f"Skill '{skill_name}' not found")
            return False

        skill = self._skills[skill_name]

        # 从分类索引中移除
        if skill.category in self._categories:
            if skill_name in self._categories[skill.category]:
                self._categories[skill.category].remove(skill_name)

        # 删除技能、嵌入和权限配置
        del self._skills[skill_name]
        self._embeddings.pop(skill_name, None)
        self._permissions.pop(skill_name, None)

        logger.info(f"Unregistered skill: {skill_name}")
        return True

    def get_skill(self, skill_name: str) -> Optional[Skill]:
        """
        获取技能

        Args:
            skill_name: 技能名称

        Returns:
            Optional[Skill]: 技能对象，不存在则返回 None
        """
        return self._skills.get(skill_name)

    def list_skills(
        self,
        category: Optional[SkillCategory] = None,
        enabled_only: bool = True
    ) -> List[Skill]:
        """
        列出技能

        Args:
            category: 技能分类过滤
            enabled_only: 是否只返回启用的技能

        Returns:
            List[Skill]: 技能列表
        """
        skills = list(self._skills.values())

        # 分类过滤
        if category:
            skills = [s for s in skills if s.category == category]

        # 状态过滤
        if enabled_only:
            skills = [s for s in skills if s.enabled]

        return skills

    def list_skills_by_category(self) -> Dict[SkillCategory, List[Skill]]:
        """
        按分类列出技能

        Returns:
            Dict[SkillCategory, List[Skill]]: 分类到技能列表的映射
        """
        result = {}
        for category, skill_names in self._categories.items():
            result[category] = [
                self._skills[name] for name in skill_names
                if name in self._skills and self._skills[name].enabled
            ]
        return result

    async def search_skills(
        self,
        query: str,
        query_embedding: Optional[List[float]] = None,
        top_k: int = 5,
        category: Optional[SkillCategory] = None
    ) -> List[tuple[str, Skill, float]]:
        """
        两阶段技能检索

        Args:
            query: 查询文本
            query_embedding: 查询嵌入向量（可选）
            top_k: 返回结果数量
            category: 技能分类过滤

        Returns:
            List[tuple[str, Skill, float]]: [(技能名称, 技能对象, 相关度分数)]
        """
        try:
            # 如果没有提供嵌入向量，使用关键词匹配
            if query_embedding is None:
                return await self._keyword_search(query, top_k, category)

            # 阶段 1：向量粗排（召回 topK × 2）
            candidates = await self._vector_search(
                query_embedding,
                top_k * 2,
                category
            )

            if not candidates:
                return []

            # 阶段 2：精排（使用 LLM 或更复杂的相似度计算）
            ranked = await self._rerank(
                query,
                query_embedding,
                candidates,
                top_k
            )

            return ranked

        except Exception as e:
            logger.error(f"Skill search failed: {str(e)}")
            return []

    async def _keyword_search(
        self,
        query: str,
        top_k: int,
        category: Optional[SkillCategory] = None
    ) -> List[tuple[str, Skill, float]]:
        """
        关键词搜索

        Args:
            query: 查询文本
            top_k: 返回结果数量
            category: 技能分类过滤

        Returns:
            List[tuple[str, Skill, float]]: 搜索结果
        """
        query_lower = query.lower()
        scores = []

        for skill_name, skill in self._skills.items():
            # 分类过滤
            if category and skill.category != category:
                continue

            if not skill.enabled:
                continue

            # 计算关键词匹配分数
            score = 0.0
            text = f"{skill.name} {skill.description} {skill.create_embedding_text()}".lower()

            # 名称匹配（权重高）
            if query_lower in skill.name.lower():
                score += 10.0

            # 描述匹配
            if query_lower in skill.description.lower():
                score += 5.0

            # 动作名称匹配
            for action_name in skill.list_actions():
                if query_lower in action_name.lower():
                    score += 2.0

            # 关键词出现次数
            score += text.count(query_lower) * 0.1

            if score > 0:
                scores.append((skill_name, skill, score))

        # 排序并返回 topK
        scores.sort(key=lambda x: x[2], reverse=True)
        return scores[:top_k]

    async def _vector_search(
        self,
        query_embedding: List[float],
        top_k: int,
        category: Optional[SkillCategory] = None
    ) -> List[str]:
        """
        向量粗排

        Args:
            query_embedding: 查询嵌入向量
            top_k: 返回结果数量
            category: 技能分类过滤

        Returns:
            List[str]: 候选技能名称列表
        """
        candidates = []

        for skill_name, skill in self._skills.items():
            # 分类过滤
            if category and skill.category != category:
                continue

            if not skill.enabled:
                continue

            # 检查是否有嵌入向量
            if skill_name not in self._embeddings:
                continue

            # 计算余弦相似度
            skill_embedding = self._embeddings[skill_name]
            score = self._cosine_similarity(query_embedding, skill_embedding)

            candidates.append((skill_name, score))

        # 排序并返回 topK
        candidates.sort(key=lambda x: x[1], reverse=True)
        return [name for name, _ in candidates[:top_k]]

    async def _rerank(
        self,
        query: str,
        query_embedding: List[float],
        candidates: List[str],
        top_k: int
    ) -> List[tuple[str, Skill, float]]:
        """
        精排候选技能

        使用更复杂的相似度计算或 LLM 重新排序

        Args:
            query: 查询文本
            query_embedding: 查询嵌入向量
            candidates: 候选技能名称
            top_k: 返回结果数量

        Returns:
            List[tuple[str, Skill, float]]: 重排序后的结果
        """
        # 这里使用改进的相似度计算
        # 实际应用中可以使用 LLM 进行重排序
        scores = []

        for skill_name in candidates:
            skill = self._skills[skill_name]

            # 结合语义相似度和关键词匹配
            semantic_score = 0.0
            if skill_name in self._embeddings:
                semantic_score = self._cosine_similarity(
                    query_embedding,
                    self._embeddings[skill_name]
                )

            # 关键词匹配分数
            keyword_score = await self._calculate_keyword_score(query, skill)

            # 加权组合
            final_score = 0.7 * semantic_score + 0.3 * keyword_score

            scores.append((skill_name, skill, final_score))

        # 排序并返回 topK
        scores.sort(key=lambda x: x[2], reverse=True)
        return scores[:top_k]

    async def _calculate_keyword_score(self, query: str, skill: Skill) -> float:
        """
        计算关键词匹配分数

        Args:
            query: 查询文本
            skill: 技能对象

        Returns:
            float: 匹配分数
        """
        query_lower = query.lower()
        score = 0.0

        # 名称匹配
        if query_lower in skill.name.lower():
            score += 3.0

        # 描述匹配
        query_words = set(query_lower.split())
        desc_words = set(skill.description.lower().split())

        # 词重叠度
        overlap = query_words & desc_words
        score += len(overlap) * 0.5

        return score

    def _cosine_similarity(
        self,
        vec1: List[float],
        vec2: List[float]
    ) -> float:
        """
        计算余弦相似度

        Args:
            vec1: 向量1
            vec2: 向量2

        Returns:
            float: 相似度分数 [0, 1]
        """
        try:
            arr1 = np.array(vec1)
            arr2 = np.array(vec2)

            dot_product = np.dot(arr1, arr2)
            norm1 = np.linalg.norm(arr1)
            norm2 = np.linalg.norm(arr2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            return float(dot_product / (norm1 * norm2))

        except Exception:
            return 0.0

    async def update_skill_embedding(
        self,
        skill_name: str,
        embedding: List[float]
    ) -> bool:
        """
        更新技能的嵌入向量

        Args:
            skill_name: 技能名称
            embedding: 新的嵌入向量

        Returns:
            bool: 是否成功
        """
        if skill_name not in self._skills:
            logger.warning(f"Skill '{skill_name}' not found")
            return False

        self._embeddings[skill_name] = embedding
        logger.info(f"Updated embedding for skill: {skill_name}")
        return True

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取注册表统计信息

        Returns:
            Dict[str, Any]: 统计信息
        """
        total_skills = len(self._skills)
        enabled_skills = sum(1 for s in self._skills.values() if s.enabled)

        category_counts = {}
        for category, skill_names in self._categories.items():
            enabled = sum(
                1 for name in skill_names
                if name in self._skills and self._skills[name].enabled
            )
            category_counts[category.value] = {
                "total": len(skill_names),
                "enabled": enabled
            }

        total_actions = sum(
            len(skill.list_actions())
            for skill in self._skills.values()
        )

        return {
            "total_skills": total_skills,
            "enabled_skills": enabled_skills,
            "disabled_skills": total_skills - enabled_skills,
            "total_actions": total_actions,
            "categories": category_counts,
            "skills_with_embeddings": len(self._embeddings)
        }

    # ==================== 权限管理 ====================

    def set_skill_permission(self, skill_name: str, permission: SkillPermission) -> bool:
        """
        设置技能权限

        Args:
            skill_name: 技能名称
            permission: 权限配置

        Returns:
            bool: 是否成功
        """
        if skill_name not in self._skills:
            logger.warning(f"Skill '{skill_name}' not found")
            return False

        permission.skill_name = skill_name
        self._permissions[skill_name] = permission
        logger.info(f"Updated permission for skill: {skill_name}")
        return True

    def get_skill_permission(self, skill_name: str) -> Optional[SkillPermission]:
        """
        获取技能权限配置

        Args:
            skill_name: 技能名称

        Returns:
            Optional[SkillPermission]: 权限配置，不存在则返回 None
        """
        return self._permissions.get(skill_name)

    def check_permission(
        self,
        skill_name: str,
        user_role: str = "user",
        context: ExecutionContext = ExecutionContext.API,
        permission_level: PermissionLevel = PermissionLevel.BASIC
    ) -> Tuple[bool, Optional[str]]:
        """
        检查技能执行权限

        Args:
            skill_name: 技能名称
            user_role: 用户角色
            context: 执行上下文
            permission_level: 用户权限级别

        Returns:
            Tuple[bool, Optional[str]]: (是否允许, 拒绝原因)
        """
        # 检查全局黑名单
        if skill_name in self._global_blacklist:
            return False, "技能在全局黑名单中"

        # 检查技能是否存在
        if skill_name not in self._skills:
            return False, "技能不存在"

        # 检查技能权限配置
        permission = self._permissions.get(skill_name)
        if not permission:
            # 使用默认配置
            permission = self._default_permission
            permission.skill_name = skill_name

        return permission.can_access(user_role, context, permission_level)

    def add_to_whitelist(self, skill_name: str) -> bool:
        """
        添加到全局白名单

        Args:
            skill_name: 技能名称

        Returns:
            bool: 是否成功
        """
        if skill_name not in self._skills:
            logger.warning(f"Skill '{skill_name}' not found")
            return False

        self._global_whitelist.add(skill_name)
        logger.info(f"Added '{skill_name}' to global whitelist")
        return True

    def add_to_blacklist(self, skill_name: str) -> bool:
        """
        添加到全局黑名单

        Args:
            skill_name: 技能名称

        Returns:
            bool: 是否成功
        """
        self._global_blacklist.add(skill_name)
        self._global_whitelist.discard(skill_name)
        logger.info(f"Added '{skill_name}' to global blacklist")
        return True

    def remove_from_blacklist(self, skill_name: str) -> bool:
        """
        从全局黑名单移除

        Args:
            skill_name: 技能名称

        Returns:
            bool: 是否成功
        """
        if skill_name in self._global_blacklist:
            self._global_blacklist.remove(skill_name)
            logger.info(f"Removed '{skill_name}' from global blacklist")
            return True
        return False

    def is_whitelisted(self, skill_name: str) -> bool:
        """
        检查是否在白名单中

        Args:
            skill_name: 技能名称

        Returns:
            bool: 是否在白名单
        """
        return skill_name in self._global_whitelist

    def is_blacklisted(self, skill_name: str) -> bool:
        """
        检查是否在黑名单中

        Args:
            skill_name: 技能名称

        Returns:
            bool: 是否在黑名单
        """
        return skill_name in self._global_blacklist

    def list_whitelist(self) -> List[str]:
        """
        列出白名单

        Returns:
            List[str]: 白名单技能列表
        """
        return list(self._global_whitelist)

    def list_blacklist(self) -> List[str]:
        """
        列出黑名单

        Returns:
            List[str]: 黑名单技能列表
        """
        return list(self._global_blacklist)

    async def execute_skill_with_permission_check(
        self,
        skill_name: str,
        action: str,
        params: Dict[str, Any],
        user_role: str = "user",
        context: ExecutionContext = ExecutionContext.API,
        permission_level: PermissionLevel = PermissionLevel.BASIC
    ) -> Tuple[bool, Any, Optional[str]]:
        """
        带权限检查的技能执行

        Args:
            skill_name: 技能名称
            action: 动作名称
            params: 动作参数
            user_role: 用户角色
            context: 执行上下文
            permission_level: 用户权限级别

        Returns:
            Tuple[bool, Any, Optional[str]]: (是否成功, 结果, 错误消息)
        """
        # 检查权限
        allowed, reason = self.check_permission(
            skill_name, user_role, context, permission_level
        )

        if not allowed:
            logger.warning(f"Permission denied for skill '{skill_name}': {reason}")
            return False, None, reason

        # 检查速率限制
        rate_limit_ok, rate_limit_reason = await self._check_rate_limit(skill_name)
        if not rate_limit_ok:
            logger.warning(f"Rate limit exceeded for skill '{skill_name}'")
            return False, None, rate_limit_reason

        # 执行技能
        skill = self._skills[skill_name]
        start_time = datetime.now()

        try:
            result = await skill.execute_action(action, **params)
            success = True

            # 记录执行历史
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            self._add_execution_record(
                skill_name, user_role, context, True, duration_ms
            )

            return True, result, None

        except Exception as e:
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            self._add_execution_record(
                skill_name, user_role, context, False, duration_ms
            )
            logger.error(f"Skill '{skill_name}' execution failed: {str(e)}")
            return False, None, str(e)

    async def _check_rate_limit(
        self,
        skill_name: str
    ) -> Tuple[bool, Optional[str]]:
        """
        检查速率限制

        Args:
            skill_name: 技能名称

        Returns:
            Tuple[bool, Optional[str]]: (是否允许, 拒绝原因)
        """
        permission = self._permissions.get(skill_name)
        if not permission:
            permission = self._default_permission

        if permission.max_rate_per_minute is None:
            return True, None

        # 获取过去一分钟的执行记录
        now = datetime.now()
        one_minute_ago = now.timestamp() - 60

        recent_executions = [
            r for r in self._execution_history
            if r.skill_name == skill_name
            and r.timestamp.timestamp() > one_minute_ago
        ]

        if len(recent_executions) >= permission.max_rate_per_minute:
            return False, f"速率限制: 每分钟最多 {permission.max_rate_per_minute} 次调用"

        return True, None

    def _add_execution_record(
        self,
        skill_name: str,
        user_role: str,
        context: ExecutionContext,
        success: bool,
        duration_ms: int
    ):
        """
        添加执行记录

        Args:
            skill_name: 技能名称
            user_role: 用户角色
            context: 执行上下文
            success: 是否成功
            duration_ms: 执行时长（毫秒）
        """
        record = SkillExecutionRecord(
            skill_name=skill_name,
            timestamp=datetime.now(),
            user_role=user_role,
            context=context,
            success=success,
            duration_ms=duration_ms
        )

        self._execution_history.append(record)

        # 清理旧记录
        if len(self._execution_history) > self._max_history_size:
            self._execution_history = self._execution_history[-self._max_history_size:]

    def get_execution_stats(
        self,
        skill_name: Optional[str] = None,
        minutes: int = 5
    ) -> Dict[str, Any]:
        """
        获取执行统计

        Args:
            skill_name: 技能名称（None 表示全部）
            minutes: 统计时间范围（分钟）

        Returns:
            Dict[str, Any]: 统计信息
        """
        now = datetime.now()
        cutoff_time = now.timestamp() - (minutes * 60)

        records = [
            r for r in self._execution_history
            if r.timestamp.timestamp() > cutoff_time
        ]

        if skill_name:
            records = [r for r in records if r.skill_name == skill_name]

        if not records:
            return {
                "total_executions": 0,
                "successful": 0,
                "failed": 0,
                "avg_duration_ms": 0
            }

        total = len(records)
        successful = sum(1 for r in records if r.success)
        failed = total - successful
        avg_duration = sum(r.duration_ms for r in records) // total

        return {
            "total_executions": total,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total if total > 0 else 0,
            "avg_duration_ms": avg_duration
        }

    def set_default_permission(self, permission: SkillPermission):
        """
        设置默认权限配置

        Args:
            permission: 默认权限配置
        """
        self._default_permission = permission
        logger.info("Updated default permission configuration")

    def get_permission_summary(self) -> Dict[str, Any]:
        """
        获取权限配置摘要

        Returns:
            Dict[str, Any]: 权限摘要
        """
        level_counts = {}
        context_counts = {}
        rate_limited = 0
        require_confirmation = 0

        for perm in self._permissions.values():
            # 权限级别统计
            level = perm.permission_level.value
            level_counts[level] = level_counts.get(level, 0) + 1

            # 上下文统计
            for ctx in perm.allowed_contexts:
                context_counts[ctx.value] = context_counts.get(ctx.value, 0) + 1

            # 速率限制统计
            if perm.max_rate_per_minute is not None:
                rate_limited += 1

            # 确认要求统计
            if perm.require_confirmation:
                require_confirmation += 1

        return {
            "total_skills_with_permissions": len(self._permissions),
            "permission_levels": level_counts,
            "execution_contexts": context_counts,
            "rate_limited_skills": rate_limited,
            "require_confirmation": require_confirmation,
            "whitelist_size": len(self._global_whitelist),
            "blacklist_size": len(self._global_blacklist)
        }


__all__ = [
    'SkillRegistry',
    'PermissionLevel',
    'ExecutionContext',
    'SkillPermission',
    'SkillExecutionRecord'
]
