#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Windows Control 配置加载器

参考 UFO/ufo/config/config_loader.py
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """配置对象"""

    def __init__(self, config_dict: Dict[str, Any]):
        for key, value in config_dict.items():
            if isinstance(value, dict):
                setattr(self, key, Config(value))
            else:
                setattr(self, key, value)

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，支持点号分隔的路径"""
        keys = key.split(".")
        value = self
        for k in keys:
            if hasattr(value, k):
                value = getattr(value, k)
            else:
                return default
        return value

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def __repr__(self):
        return f"Config({self.__dict__})"


class ConfigLoader:
    """配置加载器"""

    _instance: Optional['ConfigLoader'] = None
    _config: Optional[Config] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._config is None:
            self._load_config()

    def _find_config_file(self) -> Path:
        """查找配置文件"""
        # 按优先级查找
        search_paths = [
            Path("E:/workspace/skills/windows-control/config/config.yaml"),
            Path(__file__).parent.parent / "config" / "config.yaml",
            Path.home() / ".windows-control" / "config.yaml",
        ]

        for path in search_paths:
            if path.exists():
                return path

        # 返回默认路径
        return search_paths[0]

    def _load_config(self):
        """加载配置"""
        config_path = self._find_config_file()

        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config_dict = yaml.safe_load(f)
        else:
            # 使用默认配置
            config_dict = self._get_default_config()

        self._config = Config(config_dict)

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "system": {
                "click_api": "click_input",
                "input_text_api": "type_keys",
                "input_text_enter": False,
                "input_text_inter_key_pause": 0.01,
                "after_click_wait": 0.1,
                "mouse_move_duration": 0.1,
                "drag_duration": 0.5,
                "screenshot_quality": 85,
                "enable_screenshot": True,
                "after_screenshot_wait": 0.2,
                "log_level": "INFO",
                "pywinauto_backend": "win32",
                "max_retries": 3,
                "operation_timeout": 30,
            },
            "window": {
                "window_find_timeout": 10,
                "window_startup_timeout": 30,
                "auto_maximize": False,
            },
            "automation": {
                "use_native_accessibility": True,
                "dpi_aware": True,
                "max_ui_depth": 15,
                "ui_cache_ttl": 300,
            },
            "office": {
                "word_timeout": 30,
                "excel_timeout": 30,
                "powerpoint_timeout": 30,
                "visible": True,
            },
            "browser": {
                "default_browser": "chrome",
                "browser_timeout": 30,
                "headless": False,
            },
        }

    @property
    def config(self) -> Config:
        """获取配置对象"""
        return self._config

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self._config.get(key, default)

    def reload(self):
        """重新加载配置"""
        self._load_config()


def get_config() -> Config:
    """获取配置单例"""
    return ConfigLoader().config


def get_config_value(key: str, default: Any = None) -> Any:
    """获取配置值"""
    return ConfigLoader().get(key, default)
