"""
京麦商品发布自动化 - 统一配置
支持环境变量 + .env 文件
"""
import os
from pathlib import Path
from typing import List, Optional

# 项目根目录
BASE_DIR = Path(__file__).parent


class Settings:
    """统一配置类"""

    # 窗口
    WINDOW_TITLES: List[str] = ["jd_", "京麦", "jingmai", "JD"]
    WINDOW_WIDTH: int = 1280
    WINDOW_HEIGHT: int = 800

    # 数据库
    MYSQL_URL: str = ""
    SQLITE_URL: str = f"sqlite:///{BASE_DIR / 'data' / 'jingmai.db'}"

    # LLM
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3-vl"
    VLLM_BASE_URL: str = "http://localhost:8000"
    VLLM_MODEL: str = "qwen3-vl"
    LLM_TIMEOUT: int = 120

    # Milvus
    MILVUS_HOST: str = "8.137.122.11"
    MILVUS_PORT: int = 19530

    # 记忆
    SHORT_TERM_TTL_DAYS: int = 7
    MEMORY_BASE_DIR: str = str(BASE_DIR / "logs" / "memory")

    # Agent 安全
    MAX_RECURSION_DEPTH: int = 10
    MAX_SAME_ACTION_REPEATS: int = 3
    EXECUTION_TIMEOUT: int = 600
    CIRCUIT_BREAKER_BASE_DELAY: int = 60

    # 重试
    MAX_RETRY_ATTEMPTS: int = 3
    RETRY_BASE_DELAY: float = 2.0

    # 日志
    LOG_DIR: str = str(BASE_DIR / "logs")

    # 坐标配置分辨率
    COORDS_SCREEN_WIDTH: int = 2560
    COORDS_SCREEN_HEIGHT: int = 1392

    def __init__(self, **kwargs):
        """从环境变量或 kwargs 加载配置"""
        env_map = {
            "MYSQL_URL": "MYSQL_URL",
            "SQLITE_URL": "SQLITE_URL",
            "OLLAMA_BASE_URL": "OLLAMA_BASE_URL",
            "OLLAMA_MODEL": "OLLAMA_MODEL",
            "VLLM_BASE_URL": "VLLM_BASE_URL",
            "VLLM_MODEL": "VLLM_MODEL",
            "MILVUS_HOST": "MILVUS_HOST",
            "MILVUS_PORT": "MILVUS_PORT",
        }
        for attr, env_key in env_map.items():
            env_val = os.environ.get(env_key)
            if env_val:
                setattr(self, attr, env_val)

        for key, val in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, val)

    def ensure_dirs(self):
        """确保必要目录存在"""
        dirs = [
            self.LOG_DIR,
            self.MEMORY_BASE_DIR,
            str(BASE_DIR / "data"),
        ]
        for d in dirs:
            Path(d).mkdir(parents=True, exist_ok=True)


# 全局单例
_settings: Optional[Settings] = None


def get_settings(**kwargs) -> Settings:
    """获取全局配置"""
    global _settings
    if _settings is None:
        _settings = Settings(**kwargs)
        _settings.ensure_dirs()
    return _settings
