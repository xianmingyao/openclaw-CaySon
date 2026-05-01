"""
京麦商品发布自动化 - 日志模块
从 scripts/jingmai_logger.py 迁移，保持接口兼容
"""
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler


class JingmaiLogger:
    """京麦自动化专用日志器"""

    COLORS = {
        'INFO': '\033[36m',
        'OK': '\033[32m',
        'WARN': '\033[33m',
        'ERROR': '\033[31m',
        'STEP': '\033[34m',
        'DEBUG': '\033[90m',
        'RESET': '\033[0m',
    }

    def __init__(self, name: str = "jingmai", log_file: Optional[str] = None, log_dir: str = None):
        self.name = name
        self.start_time = datetime.now()
        self._configure_stdio()

        # 日志目录
        if log_dir:
            log_path = Path(log_dir)
        else:
            log_path = Path(__file__).parent.parent / "logs"
        log_path.mkdir(exist_ok=True)

        if log_file is None:
            timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
            log_file = f"publish_{timestamp}.log"

        self.log_path = log_path / log_file

        # 创建 logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()

        file_handler = RotatingFileHandler(
            self.log_path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding='utf-8-sig'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        )
        self.logger.addHandler(file_handler)

        self.current_step = ""
        self.step_count = 0
        self.error_count = 0
        self.warning_count = 0
        self.use_color = False

    def _format(self, level: str, msg: str) -> str:
        timestamp = datetime.now().strftime('%H:%M:%S')
        return f"[{timestamp}] [{level}] {msg}"

    def _print(self, level: str, msg: str):
        print(self._format(level, msg))
        # 按实际级别写入文件（不再全用 DEBUG）
        level_map = {
            'INFO': logging.INFO,
            'OK': logging.INFO,
            'STEP': logging.INFO,
            'WARN': logging.WARNING,
            'ERROR': logging.ERROR,
            'DEBUG': logging.DEBUG,
        }
        self.logger.log(level_map.get(level, logging.DEBUG), msg)

    def info(self, msg: str):
        self._print('INFO', msg)

    def ok(self, msg: str):
        self._print('OK', msg)

    def warn(self, msg: str):
        self.warning_count += 1
        self._print('WARN', msg)

    def warning(self, msg: str):
        self.warn(msg)

    def error(self, msg: str):
        self.error_count += 1
        self._print('ERROR', msg)

    def step(self, msg: str):
        self.step_count += 1
        self.current_step = msg
        self._print('STEP', msg)

    def debug(self, msg: str):
        self._print('DEBUG', msg)

    @staticmethod
    def _configure_stdio():
        for stream_name in ("stdout", "stderr"):
            stream = getattr(sys, stream_name, None)
            reconfigure = getattr(stream, "reconfigure", None)
            if callable(reconfigure):
                try:
                    reconfigure(encoding="utf-8", errors="replace")
                except Exception:
                    pass

    def header(self, msg: str):
        line = "=" * 60
        self.info(line)
        self.info(msg)
        self.info(line)

    def section(self, msg: str):
        self.info("")
        self.info(f"--- {msg} ---")

    def sub(self, msg: str):
        self._print('INFO', f"  {msg}")

    def sub_ok(self, msg: str):
        self._print('OK', f"  {msg}")

    def sub_error(self, msg: str):
        self.error_count += 1
        self._print('ERROR', f"  {msg}")

    def progress(self, current: int, total: int, msg: str = ""):
        pct = int(current / total * 100) if total > 0 else 0
        bar_len = 20
        filled = int(bar_len * current / total) if total > 0 else 0
        bar = "#" * filled + "-" * (bar_len - filled)
        self._print('STEP', f"[{bar}] {pct}% ({current}/{total}) {msg}")

    def get_elapsed(self) -> str:
        elapsed = datetime.now() - self.start_time
        total_seconds = int(elapsed.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"

    def summary(self) -> bool:
        self.info("")
        self.info("-" * 50)
        self.info("[SUMMARY]")
        self.info(f"  Steps: {self.step_count}")
        self.info(f"  Errors: {self.error_count}")
        self.info(f"  Warnings: {self.warning_count}")
        self.info(f"  Elapsed: {self.get_elapsed()}")
        self.info(f"  Log: {self.log_path}")
        self.info("-" * 50)
        if self.error_count == 0:
            self.ok("All operations completed!")
        else:
            self.error(f"{self.error_count} error(s) found")
        return self.error_count == 0


# 全局日志实例
_logger: Optional[JingmaiLogger] = None


def get_logger(name: str = "jingmai") -> JingmaiLogger:
    global _logger
    if _logger is None:
        _logger = JingmaiLogger(name)
    return _logger


def init_logger(name: str = "jingmai", log_file: Optional[str] = None) -> JingmaiLogger:
    global _logger
    _logger = JingmaiLogger(name, log_file)
    return _logger
