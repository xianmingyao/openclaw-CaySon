"""v2 配置加载。

该模块只负责把 `.env` 中的文本值转换成强类型配置对象，不在导入时连接
MySQL、Redis、Milvus 或任何外部服务，确保测试和 CLI 启动都可预测。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class MySQLSettings:
    """MySQL 持久化配置。"""

    host: str = "127.0.0.1"
    port: int = 3306
    user: str = "root"
    password: str = ""
    database: str = "jingmai_agent"
    charset: str = "utf8mb4"
    min_size: int = 1
    max_size: int = 5


@dataclass(frozen=True)
class RedisSettings:
    """Redis 短期缓存与锁配置。"""

    host: str = "127.0.0.1"
    port: int = 6379
    password: str | None = None
    db: int = 0
    lock_ttl_sec: int = 600


@dataclass(frozen=True)
class MilvusSettings:
    """Milvus 向量经验库配置。"""

    host: str = "127.0.0.1"
    port: int = 19530
    db: str = "jingmai_kb"
    collection: str = "jingmai_experience"
    dimension: int = 768


@dataclass(frozen=True)
class LLMSettings:
    """通用 LLM/VLM 配置。"""

    provider: str = "ollama"
    base_url: str = "http://localhost:11434"
    api_key: str = "ollama"
    model: str = "qwen3-vl:8b-instruct"
    timeout_sec: int = 60
    max_retries: int = 3


@dataclass(frozen=True)
class ReviewScorerSettings:
    """MiniMax-M3 需求评审器配置。"""

    provider: str = "minimax"
    base_url: str = "https://api.minimaxi.com/anthropic"
    api_key: str | None = None
    model: str = "MiniMax-M3"
    thinking: str = "adaptive"
    max_loop_steps: int = 3
    max_call_attempts: int = 5
    backoff_base_sec: float = 1.0
    backoff_max_sec: float = 60.0


@dataclass(frozen=True)
class RuntimeSettings:
    """运行时本地目录配置。"""

    artifact_dir: Path = Path("artifacts")
    temp_dir: Path = Path("tmp")
    form_completion_threshold: float = 0.90


@dataclass(frozen=True)
class Settings:
    """进程级总配置对象。"""

    mysql: MySQLSettings = MySQLSettings()
    redis: RedisSettings = RedisSettings()
    milvus: MilvusSettings = MilvusSettings()
    llm: LLMSettings = LLMSettings()
    review_scorer: ReviewScorerSettings = ReviewScorerSettings()
    runtime: RuntimeSettings = RuntimeSettings()


def load_settings(path: str | Path = ".env", environ: dict[str, str] | None = None) -> Settings:
    """加载配置并返回不可变 `Settings`。

    # 先读取调用者传入的环境字典，方便单元测试不污染真实环境。
    # 如果没有传入环境字典，再读取指定 `.env` 文件中的键值。
    # 所有字段都有保守默认值，因此缺少 `.env` 时也可以运行 dry-run 测试。
    """

    source = dict(environ or {})
    if environ is None:
        source.update(_read_env_file(Path(path)))

    return Settings(
        mysql=MySQLSettings(
            host=_str(source, "JINGMAI_MYSQL_HOST", "127.0.0.1"),
            port=_int(source, "JINGMAI_MYSQL_PORT", 3306),
            user=_str(source, "JINGMAI_MYSQL_USER", "root"),
            password=_str(source, "JINGMAI_MYSQL_PASSWORD", ""),
            database=_str(source, "JINGMAI_MYSQL_DB", "jingmai_agent"),
            charset=_str(source, "JINGMAI_MYSQL_CHARSET", "utf8mb4"),
            min_size=_int(source, "JINGMAI_MYSQL_MIN_SIZE", 1),
            max_size=_int(source, "JINGMAI_MYSQL_MAX_SIZE", 5),
        ),
        redis=RedisSettings(
            host=_str(source, "JINGMAI_REDIS_HOST", "127.0.0.1"),
            port=_int(source, "JINGMAI_REDIS_PORT", 6379),
            password=_optional_str(source, "JINGMAI_REDIS_PASSWORD"),
            db=_int(source, "JINGMAI_REDIS_DB", 0),
            lock_ttl_sec=_int(source, "JINGMAI_REDIS_LOCK_TTL_SEC", 600),
        ),
        milvus=MilvusSettings(
            host=_str(source, "JINGMAI_MILVUS_HOST", "127.0.0.1"),
            port=_int(source, "JINGMAI_MILVUS_PORT", 19530),
            db=_str(source, "JINGMAI_MILVUS_DB", "jingmai_kb"),
            collection=_str(source, "JINGMAI_MILVUS_COLLECTION", "jingmai_experience"),
            dimension=_int(source, "JINGMAI_MILVUS_DIMENSION", 768),
        ),
        llm=LLMSettings(
            provider=_str(source, "JINGMAI_LLM_PROVIDER", _str(source, "LLM_PROVIDER", "ollama")),
            base_url=_str(source, "JINGMAI_LLM_BASE_URL", _str(source, "LLM_BASE_URL", "http://localhost:11434")),
            api_key=_str(source, "JINGMAI_LLM_API_KEY", _str(source, "LLM_API_KEY", "ollama")),
            model=_str(source, "JINGMAI_LLM_MODEL", _str(source, "LLM_MODEL", "qwen3-vl:8b-instruct")),
            timeout_sec=_int(source, "JINGMAI_LLM_TIMEOUT_SEC", 60),
            max_retries=_int(source, "JINGMAI_LLM_MAX_RETRIES", 3),
        ),
        review_scorer=ReviewScorerSettings(
            provider=_str(source, "JINGMAI_REVIEW_SCORER_PROVIDER", "minimax"),
            base_url=_str(source, "JINGMAI_REVIEW_SCORER_BASE_URL", "https://api.minimaxi.com/anthropic"),
            api_key=_optional_str(source, "JINGMAI_REVIEW_SCORER_API_KEY"),
            model=_str(source, "JINGMAI_REVIEW_SCORER_MODEL", "MiniMax-M3"),
            thinking=_str(source, "JINGMAI_REVIEW_SCORER_THINKING", "adaptive"),
            max_loop_steps=_int(source, "JINGMAI_REVIEW_SCORER_MAX_LOOP_STEPS", 3),
            max_call_attempts=_int(source, "JINGMAI_REVIEW_SCORER_MAX_CALL_ATTEMPTS", 5),
            backoff_base_sec=_float(source, "JINGMAI_REVIEW_SCORER_BACKOFF_BASE_SEC", 1.0),
            backoff_max_sec=_float(source, "JINGMAI_REVIEW_SCORER_BACKOFF_MAX_SEC", 60.0),
        ),
        runtime=RuntimeSettings(
            artifact_dir=Path(_str(source, "JINGMAI_ARTIFACT_DIR", "artifacts")),
            temp_dir=Path(_str(source, "JINGMAI_TEMP_DIR", "tmp")),
            form_completion_threshold=_float(source, "JINGMAI_FORM_COMPLETION_THRESHOLD", 0.90),
        ),
    )


def _read_env_file(path: Path) -> dict[str, str]:
    """读取简单 `.env` 文件。

    # 这里不用第三方 dotenv，避免 Phase 1 骨架在依赖未安装时无法启动。
    # 空行和注释会被跳过，`export KEY=value` 也做兼容处理。
    # 引号只移除最外层一对，保留中间内容原样。
    """

    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = _strip_quotes(value.strip())
    return values


def _strip_quotes(value: str) -> str:
    """移除 `.env` 值最外层引号。"""

    # `.env` 中常见写法是 KEY="value" 或 KEY='value'。
    # 只有首尾同为一类引号时才移除，避免误删合法内容。
    # 不处理转义语义，保持 Phase 1 配置加载足够简单可控。
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _str(env: dict[str, Any], key: str, default: str) -> str:
    """读取字符串值。"""

    # 空字符串视为未配置，回落到默认值。
    # 非空值统一转成 str，兼容测试传入 int/Path 等对象。
    # 该 helper 只做类型转换，不负责业务合法性校验。
    value = env.get(key)
    return default if value in (None, "") else str(value)


def _optional_str(env: dict[str, Any], key: str) -> str | None:
    """读取可选字符串值。"""

    # 密码/API key 这类字段允许为空。
    # 空字符串和 None 都转换为 None，便于调用方判断是否配置。
    # 非空值不做脱敏，脱敏职责留给日志层。
    value = env.get(key)
    return None if value in (None, "") else str(value)


def _int(env: dict[str, Any], key: str, default: int) -> int:
    """读取整数值。"""

    # 未配置时直接返回默认值。
    # 已配置时让 int 抛出原生 ValueError，启动期尽早暴露错误配置。
    # 不做静默纠正，避免端口、重试次数等关键值被误读。
    value = env.get(key)
    return default if value in (None, "") else int(str(value))


def _float(env: dict[str, Any], key: str, default: float) -> float:
    """读取浮点值。"""

    # 未配置时使用默认值。
    # 已配置时通过 float 转换，非法值会立即报错。
    # 阈值和退避参数都走这里，保持解析规则一致。
    value = env.get(key)
    return default if value in (None, "") else float(str(value))
