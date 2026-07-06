"""
京麦商品发布自动化 - 日志模块
完善的代码日志记录与打印功能
"""
import os
import sys
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler

# 日志目录
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


class JingmaiLogger:
    """京麦自动化专用日志器"""
    
    # 日志级别颜色映射（Windows CMD支持）
    COLORS = {
        'INFO': '\033[36m',      # 青色
        'OK': '\033[32m',       # 绿色
        'WARN': '\033[33m',     # 黄色
        'ERROR': '\033[31m',    # 红色
        'STEP': '\033[34m',     # 蓝色
        'DEBUG': '\033[90m',    # 灰色
        'RESET': '\033[0m',     # 重置
    }
    
    def __init__(self, name: str = "jingmai", log_file: Optional[str] = None):
        self.name = name
        self.start_time = datetime.now()
        
        # 生成日志文件名
        if log_file is None:
            timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
            log_file = f"publish_{timestamp}.log"
        
        self.log_path = LOG_DIR / log_file
        
        # 创建logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()
        
        # 文件Handler - 记录所有级别
        file_handler = RotatingFileHandler(
            self.log_path,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # 状态追踪
        self.current_step = ""
        self.step_count = 0
        self.error_count = 0
        self.warning_count = 0
        
        # 是否使用颜色（检测终端支持）
        self.use_color = self._check_color_support()
        
    def _check_color_support(self) -> bool:
        """检测终端是否支持颜色"""
        # Windows默认不支持颜色，且GBK编码无法处理emoji
        return False
    
    def _color(self, level: str, msg: str) -> str:
        """给消息添加颜色"""
        if not self.use_color:
            return msg
        color = self.COLORS.get(level, '')
        reset = self.COLORS['RESET']
        return f"{color}{msg}{reset}"
    
    def _format(self, level: str, msg: str) -> str:
        """格式化日志消息"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        return f"[{timestamp}] [{level}] {msg}"
    
    def _print(self, level: str, msg: str):
        """打印并记录日志"""
        formatted = self._format(level, msg)
        colored = self._color(level, formatted)
        
        # 打印到控制台
        print(colored)
        
        # 记录到文件
        self.logger.debug(msg)
    
    # ==================== 公共接口 ====================
    
    def info(self, msg: str):
        """一般信息"""
        self._print('INFO', msg)
        
    def ok(self, msg: str):
        """成功操作"""
        self._print('OK', msg)
        
    def warn(self, msg: str):
        """警告信息"""
        self.warning_count += 1
        self._print('WARN', msg)
        
    def error(self, msg: str):
        """错误信息"""
        self.error_count += 1
        self._print('ERROR', msg)
        
    def step(self, msg: str):
        """步骤指示"""
        self.step_count += 1
        self.current_step = msg
        self._print('STEP', msg)
        
    def debug(self, msg: str):
        """调试信息"""
        self._print('DEBUG', msg)
    
    def header(self, msg: str):
        """标题横幅"""
        line = "=" * 60
        self.info(line)
        self.info(msg)
        self.info(line)
    
    def section(self, msg: str):
        """分段标题"""
        self.info("")
        self.info(f"━━━ {msg} ━━━")
    
    def sub(self, msg: str):
        """子步骤"""
        self._print('INFO', f"├─ {msg}")
        
    def sub_ok(self, msg: str):
        """子步骤成功"""
        self._print('OK', f"└─ {msg}")
        
    def sub_error(self, msg: str):
        """子步骤失败"""
        self.error_count += 1
        self._print('ERROR', f"└─ {msg}")
    
    def progress(self, current: int, total: int, msg: str = ""):
        """进度显示"""
        pct = int(current / total * 100) if total > 0 else 0
        bar_len = 20
        filled = int(bar_len * current / total) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_len - filled)
        progress_msg = f"[{bar}] {pct}% ({current}/{total}) {msg}"
        self._print('STEP', progress_msg)
    
    def info_block(self, msg: str, prefix: str = "  "):
        """信息块（多行）"""
        for line in msg.split('\n'):
            self._print('INFO', f"{prefix}{line}")
    
    def get_elapsed(self) -> str:
        """获取已用时间"""
        elapsed = datetime.now() - self.start_time
        total_seconds = int(elapsed.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def summary(self):
        """输出执行摘要"""
        self.info("")
        self.info("-" * 50)
        self.info("[SUMMARY] Execution Summary")
        self.info("-" * 50)
        self.info(f"  Total Steps: {self.step_count}")
        self.info(f"  Errors: {self.error_count}")
        self.info(f"  Warnings: {self.warning_count}")
        self.info(f"  Elapsed: {self.get_elapsed()}")
        self.info(f"  Log File: {self.log_path}")
        self.info("-" * 50)
        
        if self.error_count == 0:
            self.ok("[SUCCESS] All operations completed!")
        else:
            self.error(f"[WARNING] {self.error_count} error(s) found, check log")
        
        return self.error_count == 0


# 全局日志实例
_logger: Optional[JingmaiLogger] = None


def get_logger(name: str = "jingmai") -> JingmaiLogger:
    """获取全局日志实例"""
    global _logger
    if _logger is None:
        _logger = JingmaiLogger(name)
    return _logger


def init_logger(name: str = "jingmai", log_file: Optional[str] = None) -> JingmaiLogger:
    """初始化日志"""
    global _logger
    _logger = JingmaiLogger(name, log_file)
    return _logger


if __name__ == "__main__":
    # 测试日志模块
    log = init_logger("test")
    
    log.header("京麦商品发布自动化 - 日志模块测试")
    
    log.info("这是一条普通信息")
    log.ok("操作成功!")
    log.warn("警告信息")
    log.error("错误信息")
    log.step("第1步：检查环境")
    log.sub("检查窗口")
    log.sub_ok("窗口正常")
    log.progress(3, 10, "处理中...")
    
    log.section("测试信息块")
    log.info_block("第一行\n第二行\n第三行")
    
    log.summary()
