from pathlib import Path

from jm_ufo_agent.core.settings import load_settings


def test_load_settings_uses_safe_defaults_when_env_is_missing(tmp_path: Path):
    settings = load_settings(tmp_path / "missing.env")

    assert settings.mysql.database == "jingmai_agent"
    assert settings.redis.lock_ttl_sec == 600
    assert settings.milvus.collection == "jingmai_experience"
    assert settings.review_scorer.model == "MiniMax-M3"
    assert settings.runtime.form_completion_threshold == 0.90


def test_load_settings_reads_jingmai_prefixed_values():
    settings = load_settings(
        environ={
            "JINGMAI_MYSQL_HOST": "db.local",
            "JINGMAI_MYSQL_PORT": "3307",
            "JINGMAI_REDIS_PASSWORD": "secret",
            "JINGMAI_MILVUS_DIMENSION": "1024",
            "JINGMAI_LLM_BASE_URL": "http://llm.local",
            "JINGMAI_REVIEW_SCORER_MAX_LOOP_STEPS": "2",
            "JINGMAI_ARTIFACT_DIR": "out/artifacts",
        }
    )

    assert settings.mysql.host == "db.local"
    assert settings.mysql.port == 3307
    assert settings.redis.password == "secret"
    assert settings.milvus.dimension == 1024
    assert settings.llm.base_url == "http://llm.local"
    assert settings.review_scorer.max_loop_steps == 2
    assert settings.runtime.artifact_dir == Path("out/artifacts")


def test_load_settings_keeps_generic_llm_fallback_for_compatibility():
    settings = load_settings(environ={"LLM_BASE_URL": "http://ollama.local", "LLM_MODEL": "qwen-test"})

    assert settings.llm.base_url == "http://ollama.local"
    assert settings.llm.model == "qwen-test"
