from jingmai_publish.config import load_settings


def test_load_settings_from_env():
    settings = load_settings()
    assert settings.mysql_database == "jingmai_agent"
    assert settings.log_retention_days == 3
