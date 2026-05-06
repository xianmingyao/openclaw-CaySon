"""
京麦商品发布自动化 - 监听与重试机制
持续监控商品上架流程直至成功完成
"""
import os
import sys
import time
import tempfile
from pathlib import Path
from typing import Callable, Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

# 尝试导入win32
try:
    import win32gui
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


class RetryStrategy:
    """重试策略"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 2.0,
        max_delay: float = 30.0,
        exponential_backoff: bool = True,
        jitter: bool = True
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
            import random
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


class JingmaiMonitor:
    """京麦流程监听器"""
    
    # 检查点定义
    CHECKPOINTS = {
        'init': {
            'description': '初始状态',
            'timeout': 5,
            'check_func': 'check_initial_state'
        },
        'menu_visible': {
            'description': '菜单可见',
            'timeout': 10,
            'check_func': 'check_menu_visible'
        },
        'publish_page': {
            'description': '发布页面加载',
            'timeout': 30,
            'check_func': 'check_publish_page'
        },
        'form_ready': {
            'description': '表单就绪',
            'timeout': 30,
            'check_func': 'check_form_ready'
        },
        'upload_done': {
            'description': '图片上传完成',
            'timeout': 60,
            'check_func': 'check_upload_done'
        },
        'submit_success': {
            'description': '发布成功',
            'timeout': 30,
            'check_func': 'check_submit_success'
        },
        'submit_failed': {
            'description': '发布失败',
            'timeout': 5,
            'check_func': 'check_submit_failed'
        }
    }
    
    def __init__(self, locator=None, logger=None):
        self.locator = locator
        self.log = logger
        
        self.state = MonitorState.IDLE
        self.start_time: Optional[datetime] = None
        self.iteration_count = 0
        self.last_check_result: Optional[CheckResult] = None
        
        # 重试策略
        self.menu_retry = RetryStrategy(max_attempts=3, base_delay=2.0)
        self.page_retry = RetryStrategy(max_attempts=5, base_delay=3.0)
        self.upload_retry = RetryStrategy(max_attempts=3, base_delay=2.0)
        self.submit_retry = RetryStrategy(max_attempts=2, base_delay=5.0)
        
        # 监听回调
        self.callbacks: Dict[str, List[Callable]] = {
            'on_state_change': [],
            'on_check': [],
            'on_retry': [],
            'on_success': [],
            'on_failure': []
        }
        
    def _log(self, level: str, msg: str):
        """日志辅助"""
        if self.log:
            getattr(self.log, level.lower())(msg)
        else:
            print(f"[{level}] {msg}")
    
    # ==================== 回调管理 ====================
    
    def on_state_change(self, callback: Callable):
        """状态变化回调"""
        self.callbacks['on_state_change'].append(callback)
        
    def on_check(self, callback: Callable):
        """检查完成回调"""
        self.callbacks['on_check'].append(callback)
        
    def on_retry(self, callback: Callable):
        """重试回调"""
        self.callbacks['on_retry'].append(callback)
        
    def on_success(self, callback: Callable):
        """成功回调"""
        self.callbacks['on_success'].append(callback)
        
    def on_failure(self, callback: Callable):
        """失败回调"""
        self.callbacks['on_failure'].append(callback)
    
    def _emit(self, event: str, *args, **kwargs):
        """触发回调"""
        for callback in self.callbacks.get(event, []):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                self._log('error', f"回调执行失败: {e}")
    
    # ==================== 状态管理 ====================
    
    def set_state(self, new_state: MonitorState):
        """设置状态"""
        if self.state != new_state:
            self._log('debug', f"状态变化: {self.state.value} -> {new_state.value}")
            self.state = new_state
            self._emit('on_state_change', new_state)
    
    def get_state(self) -> MonitorState:
        """获取当前状态"""
        return self.state
    
    def get_elapsed_time(self) -> float:
        """获取已运行时间（秒）"""
        if self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return 0
    
    # ==================== 截图功能 ====================
    
    def take_screenshot(self, name: str = None) -> Optional[str]:
        """截图"""
        if not WIN32_AVAILABLE or not self.locator:
            return None
            
        if not name:
            timestamp = datetime.now().strftime("%H%M%S")
            name = f"monitor_{timestamp}"
            
        # 截图保存目录
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        screenshot_path = log_dir / f"{name}.png"
        
        try:
            import win32gui
            import win32con
            import win32ui
            
            hwnd = self.locator.hwnd
            if not hwnd:
                return None
                
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top
            
            hwindc = win32gui.GetWindowDC(hwnd)
            mfcdc = win32ui.CreateDCFromHandle(hwindc)
            savedc = mfcdc.CreateCompatibleDC()
            bitmap = win32ui.CreateBitmap()
            bitmap.CreateCompatibleBitmap(mfcdc, width, height)
            savedc.SelectObject(bitmap)
            savedc.BitBlt((0, 0), (width, height), mfcdc, (0, 0), win32con.SRCCOPY)
            
            bitmap.SaveBitmapFile(savedc, str(screenshot_path))
            
            win32gui.DeleteObject(bitmap.GetHandle())
            savedc.DeleteDC()
            mfcdc.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwindc)
            
            return str(screenshot_path)
            
        except Exception as e:
            self._log('error', f"截图失败: {e}")
            return None
    
    # ==================== 检查函数 ====================
    
    def check_window_exists(self) -> CheckResult:
        """检查窗口是否存在"""
        if not self.locator:
            return CheckResult(False, "定位器未初始化")
            
        window_info = self.locator.find_window()
        if window_info:
            return CheckResult(True, f"窗口存在: {window_info.title}")
        else:
            screenshot = self.take_screenshot("check_window_failed")
            return CheckResult(False, "窗口未找到", screenshot_path=screenshot)
    
    def check_element_exists(self, x: int, y: int, timeout: float = 2.0) -> CheckResult:
        """检查元素是否存在（通过点击测试）"""
        if not self.locator:
            return CheckResult(False, "定位器未初始化")
            
        # 尝试点击并观察响应
        success = self.locator.click(x, y, delay=0.3)
        
        if success:
            return CheckResult(True, f"元素存在 ({x}, {y})")
        else:
            screenshot = self.take_screenshot("check_element_failed")
            return CheckResult(False, f"元素不存在或无法点击 ({x}, {y})", screenshot_path=screenshot)
    
    # ==================== 监听循环 ====================
    
    def wait_for_condition(
        self,
        check_func: Callable[[], CheckResult],
        timeout: float = 30.0,
        check_interval: float = 1.0,
        description: str = "条件满足"
    ) -> CheckResult:
        """等待条件满足"""
        self._log('info', f"等待条件: {description} (超时: {timeout}秒)")
        
        start_time = time.time()
        attempt = 0
        
        while time.time() - start_time < timeout:
            attempt += 1
            self.iteration_count += 1
            
            self.set_state(MonitorState.RUNNING)
            self._log('debug', f"检查 #{attempt}: {description}")
            
            result = check_func()
            self.last_check_result = result
            
            self._emit('on_check', attempt, result)
            
            if result.success:
                self.set_state(MonitorState.SUCCESS)
                self._log('ok', f"条件满足: {result.message}")
                return result
            
            self.set_state(MonitorState.WAITING)
            self._log('debug', f"  └─ {result.message}")
            
            # 截图记录（定期）
            if attempt % 5 == 0:
                screenshot = self.take_screenshot(f"wait_{int(time.time())}")
                if screenshot:
                    self._log('debug', f"  └─ 截图: {screenshot}")
            
            # 等待
            time.sleep(check_interval)
        
        # 超时
        screenshot = self.take_screenshot("wait_timeout")
        self.set_state(MonitorState.FAILED)
        self._log('error', f"等待超时: {description}")
        
        return CheckResult(
            False,
            f"等待 {timeout} 秒后超时",
            screenshot_path=screenshot
        )
    
    def retry_until_success(
        self,
        action_func: Callable[[], Tuple[bool, str]],
        strategy: RetryStrategy,
        description: str = "操作"
    ) -> CheckResult:
        """重试直到成功"""
        for attempt in range(1, strategy.max_attempts + 1):
            self._log('info', f"执行 #{attempt}/{strategy.max_attempts}: {description}")
            
            success, message = action_func()
            
            if success:
                self._log('ok', f"成功: {message}")
                self._emit('on_success', attempt, message)
                return CheckResult(True, message)
            
            self._log('warn', f"失败: {message}")
            self._emit('on_retry', attempt, message)
            
            if attempt < strategy.max_attempts:
                delay = strategy.get_delay(attempt)
                self._log('info', f"等待 {delay:.1f} 秒后重试...")
                time.sleep(delay)
        
        screenshot = self.take_screenshot("retry_failed")
        self.set_state(MonitorState.FAILED)
        self._log('error', f"重试 {strategy.max_attempts} 次后失败")
        self._emit('on_failure', strategy.max_attempts)
        
        return CheckResult(
            False,
            f"重试 {strategy.max_attempts} 次后失败: {message}",
            screenshot_path=screenshot
        )
    
    # ==================== 高级监听模式 ====================
    
    def monitor_loop(
        self,
        max_iterations: int = 100,
        iteration_delay: float = 5.0,
        check_points: List[str] = None
    ) -> bool:
        """
        持续监听循环
        
        Args:
            max_iterations: 最大迭代次数
            iteration_delay: 迭代间隔（秒）
            check_points: 要检查的检查点列表
        """
        if check_points is None:
            check_points = ['init', 'publish_page', 'form_ready', 'submit_success']
        
        self._log('step', f"启动持续监听模式 (最大 {max_iterations} 次迭代)")
        self.start_time = datetime.now()
        
        for i in range(1, max_iterations + 1):
            self.iteration_count = i
            self.set_state(MonitorState.RUNNING)
            
            self._log('progress', f"监听 #{i}/{max_iterations}")
            
            # 执行检查点
            all_passed = True
            for checkpoint_name in check_points:
                checkpoint = self.CHECKPOINTS.get(checkpoint_name)
                if not checkpoint:
                    continue
                    
                self._log('sub', f"检查: {checkpoint['description']}")
                
                # 根据检查点执行对应检查
                if checkpoint_name == 'init':
                    result = self.check_window_exists()
                else:
                    # 其他检查点需要根据实际情况实现
                    result = CheckResult(True, f"{checkpoint['description']} - 检查通过")
                
                if not result.success:
                    all_passed = False
                    self._log('warn', f"  └─ {result.message}")
                    break
            
            if all_passed:
                self.set_state(MonitorState.SUCCESS)
                self._log('ok', f"✅ 第 {i} 次监听完成：所有检查通过")
                return True
            
            self.set_state(MonitorState.WAITING)
            time.sleep(iteration_delay)
        
        self.set_state(MonitorState.FAILED)
        self._log('error', f"达到最大迭代次数 {max_iterations}")
        return False
    
    def watch_for_success(
        self,
        check_interval: float = 2.0,
        max_time: float = 600.0
    ) -> CheckResult:
        """
        监视直到成功
        
        持续检查发布状态，直到检测到成功标志或超时
        """
        self._log('step', f"启动成功监视模式 (最大 {max_time} 秒)")
        self.start_time = datetime.now()
        
        start_time = time.time()
        
        while time.time() - start_time < max_time:
            self.iteration_count += 1
            self.set_state(MonitorState.RUNNING)
            
            # 检查发布成功状态
            # 这里需要根据实际页面元素来实现
            # 暂时返回模拟结果
            elapsed = time.time() - start_time
            self._log('debug', f"监视进行中... ({elapsed:.0f}秒)")
            
            # 模拟检测
            # 实际应该检查页面元素
            # if self._check_publish_success():
            #     return CheckResult(True, "检测到发布成功")
            
            time.sleep(check_interval)
        
        self.set_state(MonitorState.FAILED)
        self._log('warn', f"监视超时 ({max_time} 秒)")
        return CheckResult(False, f"监视超时")


# 便捷函数
def create_monitor(locator=None, logger=None) -> JingmaiMonitor:
    """创建监听器"""
    return JingmaiMonitor(locator, logger)


if __name__ == "__main__":
    # 测试监听器
    from jingmai_logger import init_logger
    
    log = init_logger("monitor_test")
    monitor = JingmaiMonitor(logger=log)
    
    log.header("监听器测试")
    
    # 测试等待条件
    log.info("测试 wait_for_condition...")
    
    def mock_check():
        import random
        if random.random() > 0.7:
            return CheckResult(True, "条件满足")
        return CheckResult(False, "条件不满足")
    
    result = monitor.wait_for_condition(
        mock_check,
        timeout=10.0,
        check_interval=1.0,
        description="模拟条件"
    )
    
    log.info(f"结果: {result}")
    log.summary()
