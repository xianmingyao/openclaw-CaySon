#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
全局配置文件
京麦智能体自动化系统

优化说明：
- 添加配置验证，防止无效配置
- 改进类型注解，提供更好的IDE支持
- 增强文档注释，说明每个配置的用途
- 保持向后兼容，不影响现有代码
"""

import os
from pathlib import Path
from typing import Optional, Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("警告: python-dotenv 未安装，无法加载 .env 文件")

ROOT_PATH = Path(__file__).parent


class Settings:
    """
    应用配置类

    优化要点：
    - 添加了配置验证方法
    - 改进了类型注解
    - 增强了文档说明
    - 保持向后兼容性
    """

    # ==================== 应用基础配置 ====================
    APP_NAME: str = os.getenv("APP_NAME", "京麦智能体系统")
    APP_VERSION: str = os.getenv("APP_VERSION", "v1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # ==================== 服务器配置 ====================
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    RELOAD: bool = os.getenv("RELOAD", "False").lower() == "true"

    # ==================== API 配置 ====================
    API_PREFIX: str = "/api/v1"

    # ==================== Redis 配置 ====================
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD") or None
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_MAX_CONNECTIONS: int = int(os.getenv("REDIS_MAX_CONNECTIONS", "20"))

    # ==================== 数据库配置 ====================
    DATABASE_ECHO: bool = False  # 数据库 SQL 日志输出
    DATABASE_TYPE: str = os.getenv("DATABASE_TYPE", "mysql")  # mysql 或 sqlite

    # MySQL 配置
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "jingmai_agent")
    MYSQL_CHARSET: str = os.getenv("MYSQL_CHARSET", "utf8mb4")
    MYSQL_POOL_SIZE: int = int(os.getenv("MYSQL_POOL_SIZE", "10"))
    MYSQL_MAX_OVERFLOW: int = int(os.getenv("MYSQL_MAX_OVERFLOW", "20"))

    # ==================== LLM 配置 ====================
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama")
    LLM_SIMPLE_MODEL: str = os.getenv("LLM_SIMPLE_MODEL", "qwen3-vl:32b")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen3-vl:32b")
    LLM_COMPLEX_MODEL: str = os.getenv("LLM_COMPLEX_MODEL", "qwen3-vl:32b")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "http://localhost:11434")
    LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "60"))
    LLM_MAX_RETRIES: int = int(os.getenv("LLM_MAX_RETRIES", "3"))
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "2048"))
    LLM_EMBEDDING_MODEL: str = os.getenv("LLM_EMBEDDING_MODEL", "nomic-embed-text")

    # ==================== 向量数据库配置 (Milvus) ====================
    MILVUS_HOST: str = os.getenv("MILVUS_HOST", "localhost")
    MILVUS_PORT: int = int(os.getenv("MILVUS_PORT", "19530"))
    MILVUS_COLLECTION: str = os.getenv("MILVUS_COLLECTION", "jingmai_kb")
    MILVUS_DIMENSION: int = int(os.getenv("MILVUS_DIMENSION", "1024"))

    # ==================== 阿里云 OSS 配置 ====================
    OSS_ENABLED: bool = os.getenv("OSS_ENABLED", "False").lower() == "true"
    OSS_ACCESS_KEY_ID: Optional[str] = os.getenv("OSS_ACCESS_KEY_ID") or None
    OSS_ACCESS_KEY_SECRET: Optional[str] = os.getenv("OSS_ACCESS_KEY_SECRET") or None
    OSS_ENDPOINT: Optional[str] = os.getenv("OSS_ENDPOINT") or None
    OSS_BUCKET_NAME: str = os.getenv("OSS_BUCKET_NAME", "")

    # ==================== 飞书集成配置 ====================
    FEISHU_APP_ID: Optional[str] = os.getenv("FEISHU_APP_ID") or None
    FEISHU_APP_SECRET: Optional[str] = os.getenv("FEISHU_APP_SECRET") or None
    FEISHU_ENCRYPT_KEY: Optional[str] = os.getenv("FEISHU_ENCRYPT_KEY") or None
    FEISHU_VERIFY_TOKEN: Optional[str] = os.getenv("FEISHU_VERIFY_TOKEN") or None

    # ==================== 日志配置 ====================
    LOG_DIR: str = os.getenv("LOG_DIR", "logs")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "{time:YYYY-MM-DD HH:mm:ss} | {name} | {level} | {message}"
    LOG_ROTATION: str = os.getenv("LOG_ROTATION", "100 MB")
    LOG_RETENTION: str = os.getenv("LOG_RETENTION", "30 days")

    # ==================== Skill 配置 ====================
    SKILL_EXTRA_DIRS: str = os.getenv("SKILL_EXTRA_DIRS", "")

    # ==================== 安全配置 ====================
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    # ==================== RAG 配置 ====================
    RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "5"))
    RAG_CHUNK_SIZE: int = int(os.getenv("RAG_CHUNK_SIZE", "1024"))
    RAG_CHUNK_OVERLAP: int = int(os.getenv("RAG_CHUNK_OVERLAP", "100"))

    # ==================== 截图配置 ====================
    SCREENSHOT_ENABLED: bool = os.getenv("SCREENSHOT_ENABLED", "True").lower() == "true"
    SCREENSHOT_MAX_WIDTH: int = int(os.getenv("SCREENSHOT_MAX_WIDTH", "2400"))
    SCREENSHOT_MAX_HEIGHT: int = int(os.getenv("SCREENSHOT_MAX_HEIGHT", "1350"))
    SCREENSHOT_PLAN_MAX_WIDTH: int = int(os.getenv("SCREENSHOT_PLAN_MAX_WIDTH", "1280"))
    SCREENSHOT_PLAN_MAX_HEIGHT: int = int(os.getenv("SCREENSHOT_PLAN_MAX_HEIGHT", "720"))
    SCREENSHOT_FORMAT: str = os.getenv("SCREENSHOT_FORMAT", "PNG")

    # ==================== 任务配置 ====================
    MAX_TASK_STEPS: int = int(os.getenv("MAX_TASK_STEPS", "20"))
    TASK_TIMEOUT: int = int(os.getenv("TASK_TIMEOUT", "600"))
    MAX_CONCURRENT_TASKS: int = int(os.getenv("MAX_CONCURRENT_TASKS", "20"))

    # ==================== LangChain 配置 ====================
    LANGCHAIN_VERBOSE: bool = os.getenv("LANGCHAIN_VERBOSE", "False").lower() == "true"
    LANGCHAIN_MAX_ITERATIONS: int = int(os.getenv("LANGCHAIN_MAX_ITERATIONS", "10"))
    LANGCHAIN_MAX_EXECUTION_TIME: int = int(
        os.getenv("LANGCHAIN_MAX_EXECUTION_TIME", "600")
    )

    # ==================== RAG 服务配置 ====================
    RAG_HYBRID_ALPHA: float = float(os.getenv("RAG_HYBRID_ALPHA", "0.5"))
    RAG_MIN_THOUGHT_LENGTH: int = int(os.getenv("RAG_MIN_THOUGHT_LENGTH", "10"))
    RAG_MAX_CONSECUTIVE_FAILURES: int = int(os.getenv("RAG_MAX_CONSECUTIVE_FAILURES", "6"))
    RAG_QUERY_TOP_K: int = int(os.getenv("RAG_QUERY_TOP_K", "20"))
    RAG_RERANK_TOP_K: int = int(os.getenv("RAG_RERANK_TOP_K", "10"))

    # ==================== Agent 执行配置 ====================
    AGENT_MAX_EXECUTION_TIME: int = int(os.getenv("AGENT_MAX_EXECUTION_TIME", "300"))
    AGENT_MAX_RECURSION_DEPTH: int = int(os.getenv("AGENT_MAX_RECURSION_DEPTH", "10"))
    AGENT_MAX_SAME_ACTION_REPEATS: int = int(os.getenv("AGENT_MAX_SAME_ACTION_REPEATS", "3"))
    AGENT_BACKOFF_BASE: int = int(os.getenv("AGENT_BACKOFF_BASE", "1"))
    AGENT_BACKOFF_MAX: int = int(os.getenv("AGENT_BACKOFF_MAX", "10"))

    # ==================== Agent UI 操作配置 ====================
    AGENT_DEFAULT_TIMEOUT: float = float(os.getenv("AGENT_DEFAULT_TIMEOUT", "3.0"))
    AGENT_POLLING_INTERVAL: float = float(os.getenv("AGENT_POLLING_INTERVAL", "0.2"))
    AGENT_CROP_PADDING_BOTTOM: int = int(os.getenv("AGENT_CROP_PADDING_BOTTOM", "100"))
    AGENT_RECENT_STEPS_KEEP: int = int(os.getenv("AGENT_RECENT_STEPS_KEEP", "3"))
    AGENT_ACTION_WAIT_AFTER_INPUT: float = float(os.getenv("AGENT_ACTION_WAIT_AFTER_INPUT", "2.0"))
    AGENT_ACTION_WAIT_OTHER: float = float(os.getenv("AGENT_ACTION_WAIT_OTHER", "1.0"))
    AGENT_WINDOW_WAIT_TIMEOUT: float = float(os.getenv("AGENT_WINDOW_WAIT_TIMEOUT", "1.5"))
    AGENT_MIN_KEYWORD_LENGTH: int = int(os.getenv("AGENT_MIN_KEYWORD_LENGTH", "2"))
    AGENT_MAX_TYPE_RETRIES: int = int(os.getenv("AGENT_MAX_TYPE_RETRIES", "2"))
    AGENT_MIN_DESCRIPTION_LENGTH: int = int(os.getenv("AGENT_MIN_DESCRIPTION_LENGTH", "1"))
    AGENT_MIN_LONG_DESC_LENGTH: int = int(os.getenv("AGENT_MIN_LONG_DESC_LENGTH", "4"))
    AGENT_MIN_STRIPPED_RESULT_LENGTH: int = int(os.getenv("AGENT_MIN_STRIPPED_RESULT_LENGTH", "50"))
    AGENT_MAX_NAV_RETRIES: int = int(os.getenv("AGENT_MAX_NAV_RETRIES", "3"))
    AGENT_PLAN_RETRY_OPEN_APP_TIMEOUT: float = float(os.getenv("AGENT_PLAN_RETRY_OPEN_APP_TIMEOUT", "3.0"))

    # ==================== Session 配置 ====================
    SESSION_MODE: str = os.getenv("SESSION_MODE", "auto")  # auto / force_same / manual
    TARGET_APP_PROCESS: str = os.getenv("TARGET_APP_PROCESS", "Jingmai.exe")

    # ==================== RAG Agent 配置 ====================
    RAG_AGENT_MAX_SUMMARY_DOCS: int = int(os.getenv("RAG_AGENT_MAX_SUMMARY_DOCS", "5"))
    RAG_AGENT_MAX_FORMAT_DOCS: int = int(os.getenv("RAG_AGENT_MAX_FORMAT_DOCS", "3"))
    RAG_AGENT_MAX_KEYWORDS: int = int(os.getenv("RAG_AGENT_MAX_KEYWORDS", "3"))

    # ==================== Planner Agent 配置 ====================
    PLANNER_MAX_SUBTASKS: int = int(os.getenv("PLANNER_MAX_SUBTASKS", "7"))
    PLANNER_MIN_SUBTASKS: int = int(os.getenv("PLANNER_MIN_SUBTASKS", "3"))
    PLANNER_SUBTASK_MAX_STEPS: int = int(os.getenv("PLANNER_SUBTASK_MAX_STEPS", "5"))

    # ==================== 记忆和路由配置 ====================
    MEMORY_DEFAULT_PRIORITY: int = int(os.getenv("MEMORY_DEFAULT_PRIORITY", "5"))
    MEMORY_CONTENT_PREVIEW_LENGTH: int = int(os.getenv("MEMORY_CONTENT_PREVIEW_LENGTH", "100"))

    # ==================== RAG 文档配置 ====================
    RAG_CHUNK_SIZE_ESTIMATE: int = int(os.getenv("RAG_CHUNK_SIZE_ESTIMATE", "500"))

    # ==================== LLM 提供者配置 ====================
    LLM_PROVIDER_TIMEOUT: int = int(os.getenv("LLM_PROVIDER_TIMEOUT", "120"))

    def validate(self) -> bool:
        """
        验证配置的有效性

        Returns:
            bool: 配置是否有效
        """
        try:
            # 验证日志级别
            valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if self.LOG_LEVEL.upper() not in valid_log_levels:
                raise ValueError(f'日志级别必须是 {valid_log_levels} 之一')

            # 验证端口范围
            if not (1 <= self.PORT <= 65535):
                raise ValueError(f'端口号必须在 1-65535 范围内')

            if not (1 <= self.REDIS_PORT <= 65535):
                raise ValueError(f'Redis端口号必须在 1-65535 范围内')

            if not (1 <= self.MYSQL_PORT <= 65535):
                raise ValueError(f'MySQL端口号必须在 1-65535 范围内')

            # 验证LLM配置
            if self.LLM_TEMPERATURE < 0.0 or self.LLM_TEMPERATURE > 2.0:
                raise ValueError(f'LLM温度参数必须在 0.0-2.0 范围内')

            if self.LLM_TIMEOUT < 1 or self.LLM_TIMEOUT > 600:
                raise ValueError(f'LLM超时时间必须在 1-600 秒范围内')

            # 验证任务配置
            if self.MAX_TASK_STEPS < 1 or self.MAX_TASK_STEPS > 100:
                raise ValueError(f'最大任务步骤数必须在 1-100 范围内')

            if self.TASK_TIMEOUT < 10 or self.TASK_TIMEOUT > 3600:
                raise ValueError(f'任务超时时间必须在 10-3600 秒范围内')

            # 验证RAG配置
            if self.RAG_TOP_K < 1 or self.RAG_TOP_K > 20:
                raise ValueError(f'RAG检索TopK必须在 1-20 范围内')

            # 验证Agent执行配置
            if self.AGENT_DEFAULT_TIMEOUT < 0.1 or self.AGENT_DEFAULT_TIMEOUT > 60:
                raise ValueError(f'Agent默认超时时间必须在 0.1-60 秒范围内')

            if self.AGENT_POLLING_INTERVAL < 0.05 or self.AGENT_POLLING_INTERVAL > 5:
                raise ValueError(f'Agent轮询间隔必须在 0.05-5 秒范围内')

            if self.AGENT_MIN_KEYWORD_LENGTH < 1 or self.AGENT_MIN_KEYWORD_LENGTH > 10:
                raise ValueError(f'Agent最小关键词长度必须在 1-10 范围内')

            if self.AGENT_MAX_TYPE_RETRIES < 0 or self.AGENT_MAX_TYPE_RETRIES > 10:
                raise ValueError(f'Agent最大重试次数必须在 0-10 范围内')

            # 验证子任务配置
            if self.PLANNER_MIN_SUBTASKS < 1 or self.PLANNER_MIN_SUBTASKS > 10:
                raise ValueError(f'最小子任务数必须在 1-10 范围内')

            if self.PLANNER_MAX_SUBTASKS < self.PLANNER_MIN_SUBTASKS:
                raise ValueError(f'最大子任务数必须大于等于最小子任务数')

            # 验证记忆配置
            if self.MEMORY_DEFAULT_PRIORITY < 1 or self.MEMORY_DEFAULT_PRIORITY > 10:
                raise ValueError(f'记忆默认优先级必须在 1-10 范围内')

            if self.MEMORY_CONTENT_PREVIEW_LENGTH < 50 or self.MEMORY_CONTENT_PREVIEW_LENGTH > 500:
                raise ValueError(f'记忆内容预览长度必须在 50-500 范围内')

            # 验证RAG文档配置
            if self.RAG_CHUNK_SIZE_ESTIMATE < 100 or self.RAG_CHUNK_SIZE_ESTIMATE > 2000:
                raise ValueError(f'RAG分块估算大小必须在 100-2000 范围内')

            # 验证LLM提供者配置
            if self.LLM_PROVIDER_TIMEOUT < 30 or self.LLM_PROVIDER_TIMEOUT > 600:
                raise ValueError(f'LLM提供者超时时间必须在 30-600 秒范围内')

            return True

        except ValueError as e:
            print(f"配置验证失败: {str(e)}")
            return False
        except Exception as e:
            print(f"配置验证时发生未知错误: {str(e)}")
            return False

    def get_database_url(self) -> str:
        """
        获取数据库连接URL

        Returns:
            str: 数据库连接URL
        """
        if self.DATABASE_TYPE == "mysql":
            return (
                f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
                f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
                f"?charset={self.MYSQL_CHARSET}"
            )
        elif self.DATABASE_TYPE == "sqlite":
            return f"sqlite+aiosqlite:///{self.MYSQL_DATABASE}.db"
        else:
            raise ValueError(f"不支持的数据库类型: {self.DATABASE_TYPE}")

    def get_redis_url(self) -> str:
        """
        获取Redis连接URL

        Returns:
            str: Redis连接URL
        """
        if self.REDIS_PASSWORD:
            return (
                f"redis://:{self.REDIS_PASSWORD}@"
                f"{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
            )
        else:
            return (
                f"redis://{self.REDIS_HOST}:"
                f"{self.REDIS_PORT}/{self.REDIS_DB}"
            )

    def __repr__(self) -> str:
        """配置对象的字符串表示"""
        return (
            f"Settings(APP_NAME={self.APP_NAME}, "
            f"VERSION={self.APP_VERSION}, "
            f"DEBUG={self.DEBUG}, "
            f"DB_TYPE={self.DATABASE_TYPE}, "
            f"LLM_PROVIDER={self.LLM_PROVIDER})"
        )


settings = Settings()

# 启动时验证配置
if not settings.validate():
    print("警告: 配置验证失败，使用默认值")
else:
    print(f"配置加载成功: {settings}")
