import pytest

from jingmai_publish.config import ConfigValidationError, load_settings, validate_settings


def test_load_settings_from_env():
    settings = load_settings()
    assert settings.mysql_database == "jingmai_agent"
    assert settings.log_retention_days == 3


def test_validate_settings_flags_bad_values(monkeypatch):
    load_settings.cache_clear()
    monkeypatch.setenv("LOG_RETENTION_DAYS", "0")
    settings = load_settings()
    assert "LOG_RETENTION_DAYS 必须大于 0" in validate_settings(settings)
    load_settings.cache_clear()


def test_load_settings_rejects_invalid_int(monkeypatch):
    load_settings.cache_clear()
    monkeypatch.setenv("MYSQL_PORT", "not-a-number")
    with pytest.raises(ConfigValidationError, match="MYSQL_PORT"):
        load_settings()
    load_settings.cache_clear()
