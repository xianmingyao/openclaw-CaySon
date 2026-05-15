"""配置加载模块。

当前项目以 `.env` 作为统一配置事实源。这里先提供最小可用配置，
支撑数据库、日志与任务运行时的基础初始化。
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import os


def _load_env_file(env_path: Path) -> None:
    """从本地 `.env` 文件加载环境变量。

    只在对应环境变量尚未存在时写入，避免覆盖外部注入配置。
    """

    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        os.environ.setdefault(key, value)


def _get_bool(name: str, default: bool = False) -> bool:
    """读取布尔环境变量。"""

    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    """读取整型环境变量。"""

    value = os.getenv(name)
    if value is None:
        return default
    return int(value)


@dataclass(slots=True)
class Settings:
    """应用运行配置。"""

    app_name: str
    app_version: str
    debug: bool
    mysql_host: str
    mysql_port: int
    mysql_user: str
    mysql_password: str
    mysql_database: str
    mysql_charset: str
    mysql_pool_size: int
    mysql_max_overflow: int
    redis_url: str
    milvus_host: str
    milvus_port: int
    milvus_collection: str
    feishu_app_id: str | None
    feishu_app_secret: str | None
    feishu_verify_token: str | None
    feishu_encrypt_key: str | None
    log_dir: Path
    memory_dir: Path
    log_retention_days: int
    screenshot_dir: Path
    screenshot_enabled: bool

    @property
    def mysql_url(self) -> str:
        """构造 SQLAlchemy 使用的 MySQL 连接串。"""

        return (
            "mysql+pymysql://"
            f"{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/"
            f"{self.mysql_database}?charset={self.mysql_charset}"
        )


@lru_cache(maxsize=1)
def load_settings(root_dir: str | Path | None = None) -> Settings:
    """加载项目配置。

    参数:
        root_dir: 项目根目录。为空时默认使用当前文件的上级目录。
    """

    base_dir = Path(root_dir) if root_dir else Path(__file__).resolve().parents[1]
    _load_env_file(base_dir / ".env")

    log_dir = base_dir / os.getenv("LOG_DIR", "logs")
    memory_dir = base_dir / os.getenv("MEMORY_DIR", "logs/memory")
    screenshot_dir = base_dir / os.getenv("SCREENSHOT_DIR", "resources/screenshots")

    return Settings(
        app_name=os.getenv("APP_NAME", "京麦桌面商品上架系统"),
        app_version=os.getenv("APP_VERSION", "v1.0.0"),
        debug=_get_bool("DEBUG", False),
        mysql_host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        mysql_port=_get_int("MYSQL_PORT", 3306),
        mysql_user=os.getenv("MYSQL_USER", "root"),
        mysql_password=os.getenv("MYSQL_PASSWORD", ""),
        mysql_database=os.getenv("MYSQL_DATABASE", "jingmai_agent"),
        mysql_charset=os.getenv("MYSQL_CHARSET", "utf8mb4"),
        mysql_pool_size=_get_int("MYSQL_POOL_SIZE", 10),
        mysql_max_overflow=_get_int("MYSQL_MAX_OVERFLOW", 20),
        redis_url=os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0"),
        milvus_host=os.getenv("MILVUS_HOST", "127.0.0.1"),
        milvus_port=_get_int("MILVUS_PORT", 19530),
        milvus_collection=os.getenv("MILVUS_COLLECTION", "jingmai_agent_memory"),
        feishu_app_id=os.getenv("FEISHU_APP_ID"),
        feishu_app_secret=os.getenv("FEISHU_APP_SECRET"),
        feishu_verify_token=os.getenv("FEISHU_VERIFY_TOKEN"),
        feishu_encrypt_key=os.getenv("FEISHU_ENCRYPT_KEY"),
        log_dir=log_dir,
        memory_dir=memory_dir,
        log_retention_days=3,
        screenshot_dir=screenshot_dir,
        screenshot_enabled=_get_bool("SCREENSHOT_ENABLED", True),
    )
