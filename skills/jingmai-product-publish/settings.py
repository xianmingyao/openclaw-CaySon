"""
京麦商品发布自动化 - 统一配置
优先级: kwargs > 环境变量 > .env 文件 > 类默认值
"""
import os
from pathlib import Path
from typing import List, Optional

# 项目根目录
BASE_DIR = Path(__file__).parent


def _load_dotenv(env_path: Path = None):
    """
    手动加载 .env 文件到 os.environ（不依赖 python-dotenv）

    格式:
      - KEY=VALUE
      - # 开头为注释
      - 空行跳过
    """
    if env_path is None:
        env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return

    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            # 去掉引号包裹
            if value and value[0] in ('"', "'") and value[-1] == value[0]:
                value = value[1:-1]
            # 只设置未定义的环境变量（不覆盖已有的）
            if key and key not in os.environ:
                os.environ[key] = value


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
    VLLM_BASE_URL: str = "http://localhost:8001"
    VLLM_MODEL: str = "qwen3-vl"
    LLM_TIMEOUT: int = 120

    # Milvus
    MILVUS_HOST: str = "8.137.122.11"
    MILVUS_PORT: int = 19530
    MILVUS_COLLECTION: str = "jingmai_publish_memory"
    MILVUS_DIM: int = 768

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

    # 截图
    SCREENSHOT_DIR: str = str(BASE_DIR / "resources" / "screenshots")
    SCREENSHOT_MAX_WIDTH: int = 2560       # 截图原始宽度
    SCREENSHOT_MAX_HEIGHT: int = 1392      # 截图原始高度
    SCREENSHOT_PLAN_MAX_WIDTH: int = 1024  # LLM 识别图宽度
    SCREENSHOT_PLAN_MAX_HEIGHT: int = 550  # LLM 识别图高度

    # 坐标配置分辨率（坐标文件中的参考分辨率）
    COORDS_SCREEN_WIDTH: int = 2560
    COORDS_SCREEN_HEIGHT: int = 1392

    def __init__(self, **kwargs):
        """
        从 .env 文件 + 环境变量 + kwargs 加载配置

        优先级: kwargs > 环境变量 > .env 文件 > 类默认值
        """
        # 1. 加载 .env 文件到 os.environ（只在首次调用时执行）
        _load_dotenv()

        # 2. 环境变量 → 覆盖类属性（字符串类型）
        env_map = {
            # LLM
            "OLLAMA_BASE_URL": "OLLAMA_BASE_URL",
            "OLLAMA_MODEL": "OLLAMA_MODEL",
            "VLLM_BASE_URL": "VLLM_BASE_URL",
            "VLLM_MODEL": "VLLM_MODEL",
            "LLM_TIMEOUT": "LLM_TIMEOUT",
            # 数据库
            "MYSQL_URL": "MYSQL_URL",
            "SQLITE_URL": "SQLITE_URL",
            "MYSQL_HOST": "MYSQL_HOST",
            "MYSQL_PORT": "MYSQL_PORT",
            "MYSQL_USER": "MYSQL_USER",
            "MYSQL_PASSWORD": "MYSQL_PASSWORD",
            "MYSQL_DATABASE": "MYSQL_DATABASE",
            # Milvus
            "MILVUS_HOST": "MILVUS_HOST",
            "MILVUS_PORT": "MILVUS_PORT",
            "MILVUS_COLLECTION": "MILVUS_COLLECTION",
            "MILVUS_DIM": "MILVUS_DIM",
            # Agent
            "MAX_RECURSION_DEPTH": "MAX_RECURSION_DEPTH",
            "MAX_SAME_ACTION_REPEATS": "MAX_SAME_ACTION_REPEATS",
            "EXECUTION_TIMEOUT": "EXECUTION_TIMEOUT",
            "CIRCUIT_BREAKER_BASE_DELAY": "CIRCUIT_BREAKER_BASE_DELAY",
            # 日志
            "LOG_DIR": "LOG_DIR",
            # 截图
            "SCREENSHOT_DIR": "SCREENSHOT_DIR",
            "SCREENSHOT_MAX_WIDTH": "SCREENSHOT_MAX_WIDTH",
            "SCREENSHOT_MAX_HEIGHT": "SCREENSHOT_MAX_HEIGHT",
            "SCREENSHOT_PLAN_MAX_WIDTH": "SCREENSHOT_PLAN_MAX_WIDTH",
            "SCREENSHOT_PLAN_MAX_HEIGHT": "SCREENSHOT_PLAN_MAX_HEIGHT",
            # 坐标参考分辨率
            "COORDS_SCREEN_WIDTH": "COORDS_SCREEN_WIDTH",
            "COORDS_SCREEN_HEIGHT": "COORDS_SCREEN_HEIGHT",
        }
        for attr, env_key in env_map.items():
            env_val = os.environ.get(env_key)
            if env_val:
                # 自动类型转换
                default_val = getattr(self.__class__, attr, None)
                if isinstance(default_val, int):
                    try:
                        setattr(self, attr, int(env_val))
                    except ValueError:
                        pass
                elif isinstance(default_val, float):
                    try:
                        setattr(self, attr, float(env_val))
                    except ValueError:
                        pass
                else:
                    setattr(self, attr, env_val)

        # 3. kwargs 最高优先级
        for key, val in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, val)

    def ensure_dirs(self):
        """确保必要目录存在"""
        dirs = [
            self.LOG_DIR,
            self.MEMORY_BASE_DIR,
            self.SCREENSHOT_DIR,
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
