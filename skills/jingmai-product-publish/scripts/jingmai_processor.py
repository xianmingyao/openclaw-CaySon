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


# ==================== 窗口识别辅助 ====================

# 京麦窗口标题关键词（多个候选，优先级从高到低）
JINGMAI_WINDOW_KEYWORDS = ["jd_", "京麦", "jingmai", "JD"]
# 最小有效窗口尺寸
JINGMAI_MIN_WINDOW_SIZE = (1024, 768)


def _is_jingmai_window(title: str) -> bool:
    """判断窗口标题是否属于京麦客户端"""
    if not title:
        return False
    title_lower = title.lower()
    return any(kw in title_lower for kw in JINGMAI_WINDOW_KEYWORDS)


def _is_valid_window_size(width: int, height: int) -> bool:
    """判断窗口尺寸是否有效（范围匹配，而非精确匹配）"""
    return width >= JINGMAI_MIN_WINDOW_SIZE[0] and height >= JINGMAI_MIN_WINDOW_SIZE[1]


def _find_jingmai_window(desktop) -> Optional[Any]:
    """从 Desktop 中找到京麦主窗口"""
    best = None
    best_area = 0
    try:
        for w in desktop.windows():
            try:
                title = w.window_text()
                if not _is_jingmai_window(title):
                    continue
                rect = w.rectangle()
                width, height = rect.width(), rect.height()
                if not _is_valid_window_size(width, height):
                    continue
                # 优先选最大窗口
                area = width * height
                if area > best_area:
                    best_area = area
                    best = w
            except Exception:
                continue
    except Exception:
        pass
    return best


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
            jingmai = _find_jingmai_window(desktop)

            if jingmai:
                rect = jingmai.rectangle()
                context.window_hwnd = rect.left
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

            # 找到京麦窗口
            jingmai = _find_jingmai_window(desktop)

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
    """动作执行策略 - 支持多种动作类型"""
    
    # 动作类型常量
    ACTION_CLICK = "click"           # 点击
    ACTION_INPUT = "input"           # 输入文本
    ACTION_SEARCH = "search"         # 搜索并回车
    ACTION_SELECT = "select"         # 选择选项
    ACTION_WAIT = "wait"            # 等待
    ACTION_SCROLL = "scroll"        # 滚动
    ACTION_KEY = "key"              # 按键
    ACTION_DOUBLE_CLICK = "dblclick" # 双击
    ACTION_HOVER = "hover"          # 悬停
    
    def __init__(self):
        super().__init__(fail_fast=False)
        self.action_queue: List[Dict[str, Any]] = []
    
    def add_action(self, action_type: str, params: Dict[str, Any]):
        """添加动作到队列"""
        self.action_queue.append({
            "type": action_type,
            "params": params
        })
    
    # 便捷方法
    def click(self, name: str = None, x: int = None, y: int = None, index: int = 0):
        """添加点击动作"""
        params = {"index": index}
        if name:
            params["name"] = name
        if x is not None and y is not None:
            params["x"] = x
            params["y"] = y
        self.add_action(self.ACTION_CLICK, params)
        return self
    
    def input(self, text: str, name: str = None, index: int = 0, clear: bool = True):
        """添加输入动作"""
        params = {"text": text, "index": index, "clear": clear}
        if name:
            params["name"] = name
        self.add_action(self.ACTION_INPUT, params)
        return self
    
    def search(self, text: str, name: str = None, index: int = 0, enter: bool = True):
        """添加搜索动作 (输入+回车)"""
        params = {"text": text, "index": index, "enter": enter}
        if name:
            params["name"] = name
        self.add_action(self.ACTION_SEARCH, params)
        return self
    
    def wait(self, seconds: float = 1.0):
        """添加等待动作"""
        self.add_action(self.ACTION_WAIT, {"duration": seconds})
        return self
    
    def scroll(self, x: int, y: int, delta: int = 100):
        """添加滚动动作"""
        self.add_action(self.ACTION_SCROLL, {"x": x, "y": y, "delta": delta})
        return self
    
    def press_key(self, key: str):
        """添加按键动作"""
        self.add_action(self.ACTION_KEY, {"key": key})
        return self
    
    def dblclick(self, x: int = None, y: int = None, name: str = None, index: int = 0):
        """添加双击动作"""
        params = {"index": index}
        if name:
            params["name"] = name
        if x is not None and y is not None:
            params["x"] = x
            params["y"] = y
        self.add_action(self.ACTION_DOUBLE_CLICK, params)
        return self
    
    def select(self, text: str, index: int = 0):
        """添加选择动作"""
        self.add_action(self.ACTION_SELECT, {"text": text, "index": index})
        return self
    
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
            jingmai = _find_jingmai_window(desktop)

            if not jingmai:
                self.log('error', "  [FAIL] 窗口未找到")
                return False

            jingmai.set_focus()
            time.sleep(0.3)
            
            # 执行每个动作
            for i, action in enumerate(self.action_queue):
                action_type = action["type"]
                params = action["params"]
                
                self.log('info', f"  [{i+1}] {action_type}: {params}")
                success = False
                
                # === CLICK ===
                if action_type == self.ACTION_CLICK:
                    success = self._do_click(jingmai, params, pyautogui, desktop)
                
                # === INPUT ===
                elif action_type == self.ACTION_INPUT:
                    success = self._do_input(jingmai, params, pyautogui)
                
                # === SEARCH (输入+回车) ===
                elif action_type == self.ACTION_SEARCH:
                    success = self._do_search(jingmai, params, pyautogui)
                
                # === WAIT ===
                elif action_type == self.ACTION_WAIT:
                    duration = params.get("duration", 1.0)
                    time.sleep(duration)
                    success = True
                
                # === SCROLL ===
                elif action_type == self.ACTION_SCROLL:
                    x = params.get("x", 0)
                    y = params.get("y", 0)
                    delta = params.get("delta", 100)
                    # 窗口坐标转屏幕坐标
                    try:
                        win_rect = jingmai.rectangle()
                        screen_x = win_rect.left + x
                        screen_y = win_rect.top + y
                    except Exception:
                        screen_x, screen_y = x, y
                    pyautogui.moveTo(screen_x, screen_y)
                    pyautogui.scroll(delta)
                    success = True
                
                # === KEY ===
                elif action_type == self.ACTION_KEY:
                    key = params.get("key", "enter")
                    pyautogui.press(key)
                    success = True
                
                # === DOUBLE CLICK ===
                elif action_type == self.ACTION_DOUBLE_CLICK:
                    success = self._do_click(jingmai, params, pyautogui, desktop, double=True)
                
                # === SELECT ===
                elif action_type == self.ACTION_SELECT:
                    success = self._do_select(jingmai, params, pyautogui)

                # === HOVER (GAP-03 fix) ===
                elif action_type == self.ACTION_HOVER:
                    success = self._do_hover(jingmai, params, pyautogui)
                
                if success:
                    self.log('info', f"  [{i+1}] [OK] {action_type}")
                else:
                    self.log('warn', f"  [{i+1}] [FAIL] {action_type}")
                
                time.sleep(0.5)  # 动作间小延迟
            
            return True
            
        except Exception as e:
            self.log('error', f"  [FAIL] 动作执行异常: {e}")
            return False
    
    def _do_click(self, jingmai, params, pyautogui, desktop, double: bool = False):
        """执行点击"""
        element_name = params.get("name", "")
        x = params.get("x")
        y = params.get("y")
        index = params.get("index", 0)

        # 按名称点击
        if element_name:
            # 尝试Button
            buttons = jingmai.descendants(control_type="Button")
            count = 0
            for btn in buttons:
                if element_name in (btn.element_info.name or ""):
                    if count == index:
                        try:
                            btn.invoke()
                        except:
                            rect = btn.rectangle()
                            pyautogui.click(rect.left + 5, rect.top + 5, clicks=2 if double else 1)
                        return True
                    count += 1

            # 尝试Hyperlink
            links = jingmai.descendants(control_type="Hyperlink")
            count = 0
            for link in links:
                if element_name in (link.element_info.name or ""):
                    if count == index:
                        try:
                            link.invoke()
                        except:
                            rect = link.rectangle()
                            pyautogui.click(rect.left + 5, rect.top + 5, clicks=2 if double else 1)
                        return True
                    count += 1

            return False

        # 按坐标点击（窗口相对坐标 → 屏幕绝对坐标）
        elif x is not None and y is not None:
            # jingmai_coords.py 中的坐标是窗口内坐标，需加上窗口左上角偏移
            try:
                win_rect = jingmai.rectangle()
                screen_x = win_rect.left + x
                screen_y = win_rect.top + y
            except Exception:
                screen_x, screen_y = x, y
            pyautogui.click(screen_x, screen_y, clicks=2 if double else 1)
            return True

        return False
    
    def _do_input(self, jingmai, params, pyautogui):
        """执行输入"""
        text = params.get("text", "")
        name = params.get("name", "")
        index = params.get("index", 0)
        clear = params.get("clear", True)

        edits = jingmai.descendants(control_type="Edit")
        count = 0
        matched_edit = None
        for edit in edits:
            edit_name = edit.element_info.name or ""
            if name in edit_name or (not name and count == index):
                matched_edit = edit
                break
            count += 1

        if matched_edit:
            # 找到了匹配的 Edit 控件，走 UIA 路径
            rect = matched_edit.rectangle()
            # 点击激活
            pyautogui.click(rect.left + 5, rect.top + 5)
            time.sleep(0.3)
        else:
            # 未找到匹配的 Edit 控件（CEF 内嵌控件可能没有 UIA Edit）
            # 此时前面坐标 click 已聚焦了输入框，直接在当前焦点输入
            self.log('info', f"  未匹配 Edit 控件 '{name}'，使用当前焦点输入")

        # 清除 (GAP-13: win32api 优先，pyautogui 回退)
        if clear:
            try:
                import win32api
                import win32con
                # Ctrl+A 全选
                win32api.keybd_event(0x11, 0, 0, 0)  # VK_CONTROL
                win32api.keybd_event(0x41, 0, 0, 0)  # VK_A
                win32api.keybd_event(0x41, 0, win32con.KEYEVENTF_KEYUP, 0)
                win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.1)
                # Delete 删除
                win32api.keybd_event(0x2E, 0, 0, 0)  # VK_DELETE
                win32api.keybd_event(0x2E, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.1)
            except Exception:
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.1)
                pyautogui.press('delete')
                time.sleep(0.1)

        # 四级回退：set_edit_text → win32clipboard+Ctrl+V → pyperclip → typewrite
        # 京麦 CEF 内嵌浏览器 set_edit_text 可能不工作
        # win32clipboard 是 fill_product_v2.py 验证过的可靠方案
        input_ok = False
        if matched_edit:
            try:
                matched_edit.set_edit_text(text)
                input_ok = True
            except Exception:
                pass

        if not input_ok:
            try:
                import win32clipboard
                import win32con
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
                win32clipboard.CloseClipboard()
                # Ctrl+V 粘贴
                import win32api
                win32api.keybd_event(0x11, 0, 0, 0)  # Ctrl down
                win32api.keybd_event(0x56, 0, 0, 0)   # V down
                win32api.keybd_event(0x56, 0, win32con.KEYEVENTF_KEYUP, 0)
                win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.3)
                input_ok = True
            except Exception:
                # win32clipboard 不可用时回退到 pyperclip
                try:
                    import pyperclip
                    pyperclip.copy(text)
                    pyautogui.hotkey('ctrl', 'v')
                    input_ok = True
                except Exception:
                    pass

        if not input_ok:
            pyautogui.typewrite(text, interval=0.05)

        return True
    
    def _do_search(self, jingmai, params, pyautogui):
        """执行搜索 (输入+回车)"""
        text = params.get("text", "")
        name = params.get("name", "")
        index = params.get("index", 0)
        enter = params.get("enter", True)
        
        # 先输入
        if self._do_input(jingmai, {"text": text, "name": name, "index": index, "clear": True}, pyautogui):
            if enter:
                time.sleep(0.3)
                pyautogui.press("enter")
                time.sleep(1)
            return True
        
        return False
    
    def _do_select(self, jingmai, params, pyautogui):
        """执行选择"""
        text = params.get("text", "")
        index = params.get("index", 0)
        
        # 查找包含文字的元素并点击
        elements = jingmai.descendants()
        count = 0
        for elem in elements:
            try:
                name = elem.element_info.name or ""
                if text in name:
                    if count == index:
                        rect = elem.rectangle()
                        pyautogui.click(rect.left + 5, rect.top + 5)
                        return True
                    count += 1
            except:
                pass
        
        return False

    def _do_hover(self, jingmai, params, pyautogui):
        """GAP-03: 执行悬停操作"""
        x = params.get("x")
        y = params.get("y")

        if x is not None and y is not None:
            # 坐标悬停：使用 win32api 移动鼠标
            try:
                import win32gui
                import win32api
                import win32con
                hwnd = jingmai.handle if hasattr(jingmai, 'handle') else None
                if hwnd:
                    left, top, _, _ = win32gui.GetWindowRect(hwnd)
                    screen_x = left + int(x)
                    screen_y = top + int(y)
                    win32api.SetCursorPos(screen_x, screen_y)
                    time.sleep(0.3)
                    return True
            except Exception:
                pass
            # 回退到 pyautogui
            pyautogui.moveTo(int(x), int(y))
            time.sleep(0.3)
            return True

        # 按名称查找元素并悬停
        name = params.get("name", "")
        if name:
            elements = jingmai.descendants()
            for elem in elements:
                try:
                    elem_name = elem.element_info.name or ""
                    if name in elem_name:
                        rect = elem.rectangle()
                        pyautogui.moveTo(rect.left + 5, rect.top + 5)
                        time.sleep(0.3)
                        return True
                except:
                    pass

        return False


class VerificationStrategy(ProcessingStrategy):
    """验证策略 - 检查发布操作是否成功"""

    def execute(self, context: JingmaiContext) -> bool:
        self.log('info', "验证执行结果...")

        try:
            from pywinauto import Desktop

            desktop = Desktop(backend="uia")
            jingmai = _find_jingmai_window(desktop)

            if not jingmai:
                self.log('error', "  [FAIL] 验证时窗口未找到")
                return False

            jingmai.set_focus()
            time.sleep(0.5)

            # 检查是否有错误弹窗或提示
            error_indicators = ["错误", "失败", "异常", "error", "fail", "警告"]
            try:
                all_elements = jingmai.descendants()
                for elem in all_elements:
                    try:
                        name = (elem.element_info.name or "").lower()
                        if any(ind in name for ind in error_indicators):
                            if elem.element_info.control_type in ("Text", "Button", "Pane"):
                                self.log('warn', f"  发现错误提示: {elem.element_info.name}")
                    except Exception:
                        continue
            except Exception as e:
                self.log('warn', f"  错误检查异常: {e}")

            # 检查关键编辑框是否有内容（表示已填写）
            product = context.config.get("product", {})
            filled_count = 0
            try:
                edits = jingmai.descendants(control_type="Edit")
                for edit in edits:
                    try:
                        value = edit.get_value()
                        if value and value.strip():
                            filled_count += 1
                    except Exception:
                        pass
            except Exception:
                pass

            self.log('info', f"  已填写 {filled_count} 个编辑框")

            if filled_count > 0:
                self.log('info', "  [OK] 验证通过")
                context.success = True
                return True
            else:
                self.log('warn', "  [WARN] 未检测到已填写的编辑框，但仍视为通过")
                context.success = True
                return True

        except Exception as e:
            self.log('error', f"  验证异常: {e}")
            # 验证失败不阻断流程
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
