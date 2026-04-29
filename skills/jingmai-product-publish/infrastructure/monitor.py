"""
京麦商品发布自动化 - 重试 + 熔断器
从 scripts/jingmai_monitor.py 迁移，新增 CircuitBreaker
"""
import time
import random
from typing import Callable, Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class RetryStrategy:
    """重试策略"""

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 2.0,
        max_delay: float = 30.0,
        exponential_backoff: bool = True,
        jitter: bool = True,
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_backoff = exponential_backoff
        self.jitter = jitter

    def get_delay(self, attempt: int) -> float:
        """计算重试延迟"""
        if self.exponential_backoff:
            delay = self.base_delay * (2 ** (attempt - 1))
        else:
            delay = self.base_delay
        delay = min(delay, self.max_delay)
        if self.jitter:
            delay = delay * (0.5 + random.random() * 0.5)
        return delay


@dataclass
class CheckResult:
    """检查结果"""
    success: bool
    message: str
    screenshot_path: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class MonitorState(Enum):
    """监听状态"""
    IDLE = "idle"
    RUNNING = "running"
    WAITING = "waiting"
    SUCCESS = "success"
    FAILED = "failed"
    STOPPED = "stopped"


class CircuitBreakerState(Enum):
    """熔断器状态"""
    CLOSED = "closed"       # 正常
    OPEN = "open"           # 熔断
    HALF_OPEN = "half_open" # 半恢复


class CircuitBreaker:
    """熔断器 — 借鉴 jingmai-putaway base.py"""

    def __init__(
        self,
        base_delay: int = 60,
        max_delay: int = 600,
        recovery_threshold: int = 3,
    ):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.recovery_threshold = recovery_threshold

        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.current_delay = base_delay

    def record_success(self):
        """记录成功"""
        self.success_count += 1
        if self.state == CircuitBreakerState.HALF_OPEN:
            if self.success_count >= self.recovery_threshold:
                self._reset()

    def record_failure(self):
        """记录失败"""
        self.failure_count += 1
        self.success_count = 0
        self.last_failure_time = time.time()
        self.current_delay = min(self.current_delay * 2, self.max_delay)
        self.state = CircuitBreakerState.OPEN

    def can_execute(self) -> bool:
        """是否可以执行"""
        if self.state == CircuitBreakerState.CLOSED:
            return True
        if self.state == CircuitBreakerState.HALF_OPEN:
            return True
        if self.state == CircuitBreakerState.OPEN:
            if self.last_failure_time:
                elapsed = time.time() - self.last_failure_time
                if elapsed >= self.current_delay:
                    self.state = CircuitBreakerState.HALF_OPEN
                    return True
            return False
        return False

    def _reset(self):
        """重置"""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.current_delay = self.base_delay


class JingmaiMonitor:
    """京麦流程监听器"""

    def __init__(self, locator=None, logger=None):
        self.locator = locator
        self.log = logger
        self.state = MonitorState.IDLE
        self.start_time: Optional[datetime] = None
        self.iteration_count = 0

    def _log(self, level: str, msg: str):
        if self.log:
            getattr(self.log, level.lower())(msg)
        else:
            print(f"[{level}] {msg}")

    def set_state(self, new_state: MonitorState):
        if self.state != new_state:
            self._log('debug', f"状态: {self.state.value} -> {new_state.value}")
            self.state = new_state

    def wait_for_condition(
        self,
        check_func: Callable[[], CheckResult],
        timeout: float = 30.0,
        check_interval: float = 1.0,
        description: str = "条件满足",
    ) -> CheckResult:
        """等待条件满足"""
        self._log('info', f"等待: {description} (超时: {timeout}秒)")
        start_time = time.time()
        attempt = 0

        while time.time() - start_time < timeout:
            attempt += 1
            self.set_state(MonitorState.RUNNING)
            result = check_func()

            if result.success:
                self.set_state(MonitorState.SUCCESS)
                self._log('ok', f"条件满足: {result.message}")
                return result

            self.set_state(MonitorState.WAITING)
            time.sleep(check_interval)

        self.set_state(MonitorState.FAILED)
        return CheckResult(False, f"等待 {timeout} 秒后超时")

    def retry_until_success(
        self,
        action_func: Callable[[], Tuple[bool, str]],
        strategy: RetryStrategy,
        description: str = "操作",
    ) -> CheckResult:
        """重试直到成功"""
        message = ""
        for attempt in range(1, strategy.max_attempts + 1):
            self._log('info', f"执行 #{attempt}/{strategy.max_attempts}: {description}")
            success, message = action_func()

            if success:
                self._log('ok', f"成功: {message}")
                return CheckResult(True, message)

            self._log('warn', f"失败: {message}")
            if attempt < strategy.max_attempts:
                delay = strategy.get_delay(attempt)
                self._log('info', f"等待 {delay:.1f} 秒后重试...")
                time.sleep(delay)

        self.set_state(MonitorState.FAILED)
        return CheckResult(False, f"重试 {strategy.max_attempts} 次后失败: {message}")
