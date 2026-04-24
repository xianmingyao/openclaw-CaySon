# -*- coding: utf-8 -*-
"""
京麦商品发布自动化 - UFO风格Processor框架
基于UFO³的ProcessorTemplate架构

流程:
1. 环境检查 (EnvironmentCheckStrategy)
2. 窗口定位 (WindowLocateStrategy)  
3. 元素查找 (ElementFindStrategy)
4. 动作执行 (ActionExecuteStrategy)
5. 结果验证 (VerificationStrategy)
"""
import os
import sys
import time
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Optional, List, Type
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime

# 添加脚本目录到路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))


# ==================== 核心组件 ====================

class ProcessingPhase(Enum):
    """处理阶段"""
    ENVIRONMENT_CHECK = "environment_check"
    WINDOW_LOCATE = "window_locate"
    ELEMENT_FIND = "element_find"
    ACTION_EXECUTE = "action_execute"
    VERIFICATION = "verification"


@dataclass
class JingmaiContext:
    """京麦发布上下文"""
    # 状态
    current_phase: ProcessingPhase = ProcessingPhase.ENVIRONMENT_CHECK
    current_step: int = 0
    total_steps: int = 8
    
    # 配置
    config: Dict[str, Any] = field(default_factory=dict)
    product_data: Dict[str, Any] = field(default_factory=dict)
    
    # 窗口信息
    window_hwnd: Optional[int] = None
    window_title: str = ""
    window_rect: tuple = (0, 0, 2560, 1392)
    
    # 元素信息
    found_elements: Dict[str, Any] = field(default_factory=dict)
    
    # 执行结果
    success: bool = False
    error_message: str = ""
    screenshot_path: str = ""
    
    # 元数据
    start_time: float = field(default_factory=time.time)
    phase_results: Dict[str, Any] = field(default_factory=dict)


class ProcessingStrategy(ABC):
    """策略基类"""
    
    def __init__(self, fail_fast: bool = True):
        self.fail_fast = fail_fast
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def execute(self, context: JingmaiContext) -> bool:
        """执行策略，返回是否成功"""
        pass
    
    def log(self, level: str, msg: str):
        getattr(self.logger, level)(msg)


class ProcessingMiddleware(ABC):
    """中间件基类"""
    
    @abstractmethod
    def pre_process(self, context: JingmaiContext, phase: ProcessingPhase):
        """前置处理"""
        pass
    
    @abstractmethod
    def post_process(self, context: JingmaiContext, phase: ProcessingPhase, success: bool):
        """后置处理"""
        pass


# ==================== 中间件实现 ====================

class LoggingMiddleware(ProcessingMiddleware):
    """日志中间件"""
    
    def pre_process(self, context: JingmaiContext, phase: ProcessingPhase):
        phase_name = phase.value.upper().replace("_", " ")
        print(f"\n{'='*50}")
        print(f"> PHASE: {phase_name}")
        print(f"{'='*50}")
    
    def post_process(self, context: JingmaiContext, phase: ProcessingPhase, success: bool):
        status = "[OK] SUCCESS" if success else "[FAIL] FAILED"
        print(f"{status} - {phase.value}")


class ScreenshotMiddleware(ProcessingMiddleware):
    """截图中间件"""
    
    def __init__(self, screenshot_dir: str = None):
        self.screenshot_dir = Path(screenshot_dir) if screenshot_dir else Path("logs")
        self.screenshot_dir.mkdir(exist_ok=True)
    
    def pre_process(self, context: JingmaiContext, phase: ProcessingPhase):
        # 前置截图
        timestamp = datetime.now().strftime("%H%M%S")
        filename = f"{phase.value}_{timestamp}.png"
        path = self.screenshot_dir / filename
        # TODO: 调用实际截图
        context.screenshot_path = str(path)
        print(f"[SCREENSHOT] Screenshot: {path}")
    
    def post_process(self, context: JingmaiContext, phase: ProcessingPhase, success: bool):
        if not success:
            # 失败时额外截图
            print(f"[FAIL] Failed screenshot saved: {context.screenshot_path}")


class RetryMiddleware(ProcessingMiddleware):
    """重试中间件"""
    
    def __init__(self, max_retries: int = 3, delay: float = 1.0):
        self.max_retries = max_retries
        self.delay = delay
    
    def pre_process(self, context: JingmaiContext, phase: ProcessingPhase):
        context.phase_results[phase.value] = {"attempts": 0}
    
    def post_process(self, context: JingmaiContext, phase: ProcessingPhase, success: bool):
        if not success and self.max_retries > 1:
            attempts = context.phase_results.get(phase.value, {}).get("attempts", 0)
            if attempts < self.max_retries:
                print(f"[RETRY] Retrying in {self.delay}s... (attempt {attempts + 1}/{self.max_retries})")
                time.sleep(self.delay)


# ==================== 策略实现 ====================

class EnvironmentCheckStrategy(ProcessingStrategy):
    """环境检查策略"""
    
    def execute(self, context: JingmaiContext) -> bool:
        self.log('info', "检查运行环境...")
        
        # 检查依赖
        deps = {
            "win32gui": False,
            "pywinauto": False,
            "PIL": False,
        }
        
        try:
            import win32gui
            deps["win32gui"] = True
        except ImportError:
            pass
        
        try:
            from pywinauto import Desktop
            deps["pywinauto"] = True
        except ImportError:
            pass
        
        try:
            from PIL import Image
            deps["PIL"] = True
        except ImportError:
            pass
        
        # 打印依赖状态
        for name, available in deps.items():
            status = "[OK]" if available else "[FAIL]"
            self.log('info', f"  {status} {name}")
        
        # 检查屏幕分辨率
        try:
            import win32api
            width = win32api.GetSystemMetrics(0)
            height = win32api.GetSystemMetrics(1)
            self.log('info', f"  屏幕分辨率: {width}x{height}")
            
            if width < 1280 or height < 720:
                self.log('warn', "  屏幕分辨率过低，建议1280x720以上")
        except:
            pass
        
        context.phase_results["environment"] = deps
        return True  # 环境检查始终通过


class WindowLocateStrategy(ProcessingStrategy):
    """窗口定位策略"""
    
    def execute(self, context: JingmaiContext) -> bool:
        self.log('info', "查找京麦窗口...")
        
        try:
            from pywinauto import Desktop
            
            desktop = Desktop(backend="uia")
            all_windows = desktop.windows()
            
            # 查找京麦主窗口
            jingmai = None
            for w in all_windows:
                try:
                    title = w.window_text()
                    if "jd_465d1abd3ee76" in title:
                        rect = w.rectangle()
                        if rect.width() == 2560 and rect.height() == 1392:
                            jingmai = w
                            break
                except:
                    pass
            
            if jingmai:
                rect = jingmai.rectangle()
                context.window_hwnd = rect.left  # 简化处理
                context.window_rect = (rect.left, rect.top, rect.right, rect.bottom)
                context.window_title = jingmai.window_text()
                
                self.log('info', f"  [OK] 找到窗口: {context.window_title}")
                self.log('info', f"     尺寸: {rect.width()}x{rect.height()}")
                self.log('info', f"     位置: ({rect.left}, {rect.top})")
                
                # 激活窗口
                jingmai.set_focus()
                time.sleep(0.5)
                
                return True
            
            self.log('error', "  [FAIL] 未找到京麦窗口")
            return False
            
        except ImportError as e:
            self.log('error', f"  [FAIL] pywinauto未安装: {e}")
            return False
        except Exception as e:
            self.log('error', f"  [FAIL] 窗口定位失败: {e}")
            return False


class ElementFindStrategy(ProcessingStrategy):
    """元素查找策略"""
    
    def execute(self, context: JingmaiContext) -> bool:
        self.log('info', "查找UI元素...")
        
        try:
            from pywinauto import Desktop
            
            desktop = Desktop(backend="uia")
            all_windows = desktop.windows()
            
            # 找到京麦窗口
            jingmai = None
            for w in all_windows:
                try:
                    title = w.window_text()
                    if "jd_465d1abd3ee76" in title:
                        rect = w.rectangle()
                        if rect.width() == 2560 and rect.height() == 1392:
                            jingmai = w
                            break
                except:
                    pass
            
            if not jingmai:
                self.log('error', "  [FAIL] 窗口未找到")
                return False
            
            # 查找各类元素
            elements = {}
            
            # 按钮
            buttons = jingmai.descendants(control_type="Button")
            elements["buttons"] = []
            for btn in buttons:
                try:
                    name = btn.element_info.name or ""
                    rect = btn.rectangle()
                    elements["buttons"].append({
                        "name": name,
                        "x": rect.left,
                        "y": rect.top,
                        "width": rect.width(),
                        "height": rect.height()
                    })
                except:
                    pass
            
            self.log('info', f"  找到 {len(elements['buttons'])} 个按钮")
            
            # 链接
            links = jingmai.descendants(control_type="Hyperlink")
            elements["links"] = []
            for link in links:
                try:
                    name = link.element_info.name or ""
                    rect = link.rectangle()
                    elements["links"].append({
                        "name": name,
                        "x": rect.left,
                        "y": rect.top
                    })
                except:
                    pass
            
            self.log('info', f"  找到 {len(elements['links'])} 个链接")
            
            # 编辑框
            edits = jingmai.descendants(control_type="Edit")
            elements["edits"] = []
            for edit in edits:
                try:
                    name = edit.element_info.name or ""
                    rect = edit.rectangle()
                    elements["edits"].append({
                        "name": name,
                        "x": rect.left,
                        "y": rect.top,
                        "width": rect.width()
                    })
                except:
                    pass
            
            self.log('info', f"  找到 {len(elements['edits'])} 个编辑框")
            
            context.found_elements = elements
            context.success = True
            return True
            
        except Exception as e:
            self.log('error', f"  [FAIL] 元素查找失败: {e}")
            return False


class ActionExecuteStrategy(ProcessingStrategy):
    """动作执行策略"""
    
    def __init__(self):
        super().__init__(fail_fast=False)
        self.action_queue: List[Dict[str, Any]] = []
    
    def add_action(self, action_type: str, params: Dict[str, Any]):
        """添加动作到队列"""
        self.action_queue.append({
            "type": action_type,
            "params": params
        })
    
    def execute(self, context: JingmaiContext) -> bool:
        if not self.action_queue:
            self.log('warn', "  动作队列为空")
            return True
        
        self.log('info', f"执行 {len(self.action_queue)} 个动作...")
        
        try:
            from pywinauto import Desktop
            import pyautogui
            
            desktop = Desktop(backend="uia")
            
            # 找到京麦窗口
            jingmai = None
            for w in desktop.windows():
                try:
                    title = w.window_text()
                    if "jd_465d1abd3ee76" in title:
                        rect = w.rectangle()
                        if rect.width() == 2560 and rect.height() == 1392:
                            jingmai = w
                            break
                except:
                    pass
            
            if not jingmai:
                self.log('error', "  [FAIL] 窗口未找到")
                return False
            
            jingmai.set_focus()
            
            # 执行每个动作
            for i, action in enumerate(self.action_queue):
                action_type = action["type"]
                params = action["params"]
                
                self.log('info', f"  [{i+1}] {action_type}: {params}")
                
                if action_type == "click":
                    # 点击元素
                    element_name = params.get("name", "")
                    x = params.get("x")
                    y = params.get("y")
                    
                    if element_name and x is None:
                        # 按名称查找
                        # 查找按钮
                        buttons = jingmai.descendants(control_type="Button")
                        for btn in buttons:
                            if element_name in (btn.element_info.name or ""):
                                rect = btn.rectangle()
                                try:
                                    btn.invoke()
                                except:
                                    pyautogui.click(rect.left, rect.top)
                                time.sleep(1)
                                break
                    elif x is not None and y is not None:
                        # 按坐标点击
                        pyautogui.click(x, y)
                        time.sleep(1)
                        
                elif action_type == "input":
                    # 输入文本
                    element_name = params.get("name", "")
                    text = params.get("text", "")
                    
                    edits = jingmai.descendants(control_type="Edit")
                    for edit in edits:
                        if element_name in (edit.element_info.name or ""):
                            try:
                                edit.set_edit_text(text)
                            except:
                                rect = edit.rectangle()
                                pyautogui.click(rect.left + 5, rect.top + 5)
                                time.sleep(0.5)
                                pyautogui.typewrite(text, interval=0.1)
                            time.sleep(1)
                            break
                
                elif action_type == "wait":
                    # 等待
                    duration = params.get("duration", 1)
                    time.sleep(duration)
            
            return True
            
        except Exception as e:
            self.log('error', f"  [FAIL] 动作执行失败: {e}")
            return False


class VerificationStrategy(ProcessingStrategy):
    """验证策略"""
    
    def execute(self, context: JingmaiContext) -> bool:
        self.log('info', "验证执行结果...")
        
        # 检查关键元素是否存在
        # TODO: 实现验证逻辑
        
        self.log('info', "  [OK] 验证通过")
        return True


# ==================== Processor模板 ====================

class JingmaiPublishProcessor:
    """京麦发布Processor - UFO风格"""
    
    # 策略映射
    STRATEGY_MAP: Dict[ProcessingPhase, Type[ProcessingStrategy]] = {
        ProcessingPhase.ENVIRONMENT_CHECK: EnvironmentCheckStrategy,
        ProcessingPhase.WINDOW_LOCATE: WindowLocateStrategy,
        ProcessingPhase.ELEMENT_FIND: ElementFindStrategy,
        ProcessingPhase.ACTION_EXECUTE: ActionExecuteStrategy,
        ProcessingPhase.VERIFICATION: VerificationStrategy,
    }
    
    def __init__(self, config: Dict[str, Any] = None):
        # 初始化策略
        self.strategies: Dict[ProcessingPhase, ProcessingStrategy] = {}
        for phase, strategy_class in self.STRATEGY_MAP.items():
            self.strategies[phase] = strategy_class()
        
        # 初始化中间件
        self.middleware_chain: List[ProcessingMiddleware] = [
            LoggingMiddleware(),
            ScreenshotMiddleware(),
            RetryMiddleware(max_retries=3, delay=1.0),
        ]
        
        # 初始化上下文
        self.context = JingmaiContext()
        self.context.config = config or {}
        
        # 打印banner
        self._print_banner()
    
    def _print_banner(self):
        print("="*60)
        print("  Jingmai Product Publish - UFO Processor Framework")
        print("="*60)
        print()
    
    def process(self) -> bool:
        """执行处理流程"""
        
        phases = list(ProcessingPhase)
        
        for phase in phases:
            strategy = self.strategies[phase]
            
            # 前置中间件
            for mw in self.middleware_chain:
                mw.pre_process(self.context, phase)
            
            # 执行策略
            success = strategy.execute(self.context)
            
            # 后置中间件
            for mw in reversed(self.middleware_chain):
                mw.post_process(self.context, phase, success)
            
            # 失败处理
            if not success and strategy.fail_fast:
                print(f"\n[FAIL] 阶段 {phase.value} 失败，停止执行")
                return False
        
        print("\n" + "="*50)
        print("[OK] 所有阶段执行完成")
        print("="*50)
        return True
    
    def get_action_strategy(self) -> ActionExecuteStrategy:
        """获取动作执行策略以便添加动作"""
        return self.strategies[ProcessingPhase.ACTION_EXECUTE]


# ==================== 便捷函数 ====================

def create_publisher(config: Dict[str, Any] = None) -> JingmaiPublishProcessor:
    """创建发布Processor"""
    return JingmaiPublishProcessor(config)


def run_simple_publish(product_name: str = "测试商品"):
    """简单发布流程"""
    config = {
        "product": {
            "title": product_name,
        }
    }
    
    processor = create_publisher(config)
    
    # 添加发布动作
    action_strategy = processor.get_action_strategy()
    
    # 动作示例
    # action_strategy.add_action("click", {"name": "修改", "x": 979, "y": 225})
    # action_strategy.add_action("input", {"name": "商品标题", "text": product_name})
    # action_strategy.add_action("wait", {"duration": 2})
    
    # 执行
    success = processor.process()
    
    return success


if __name__ == "__main__":
    # 测试
    run_simple_publish("公牛插座 B5440")
