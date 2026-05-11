"""
京麦商品发布自动化 - 双引擎元素定位器
UIA 元素查找 + 坐标 fallback
"""
import ctypes
import ctypes.wintypes
import math
import os
import random
import time
from typing import Optional, Tuple, Dict, Any, List
from dataclasses import dataclass

try:
    import win32gui
    import win32con
    import win32api
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

try:
    from pywinauto import Desktop
    PYWINAUTO_AVAILABLE = True
except ImportError:
    PYWINAUTO_AVAILABLE = False


@dataclass
class WindowInfo:
    """窗口信息"""
    hwnd: int
    title: str
    rect: Tuple[int, int, int, int]
    width: int
    height: int
    is_visible: bool


@dataclass
class ElementPosition:
    """元素位置"""
    x: int
    y: int
    width: int = 0
    height: int = 0
    confidence: float = 1.0
    method: str = "fallback"


# 京麦窗口标题关键词（精确匹配，避免匹配 IDE/编辑器窗口）
WINDOW_KEYWORDS = ["jd_", "京麦"]
# 排除关键词（标题含这些的不匹配，防止 IDE 项目名误命中）
WINDOW_EXCLUDE_KEYWORDS = [
    "code", "vscode", "visual studio", "pycharm", "idea",
    "terminal", "cmd", "powershell",
    "jingmai-product-publish", "jingmai-agent",  # IDE 项目标题
]
BROWSER_PROCESS_HINTS = {"chrome", "msedge", "360chrome", "360se", "iexplore", "jingmai", "jd"}
JINGMAI_PROCESS_HINTS = {"jmworkstation", "jdm_dd_workbench"}
WINDOW_EXCLUDE_PROCESS_HINTS = {"jdm_dd_workbench"}


class JingmaiLocator:
    """双引擎元素定位器"""

    def __init__(self, log=None):
        self.log = log
        self.hwnd: Optional[int] = None
        self.window_rect: Optional[Tuple[int, int, int, int]] = None
        self._desktop = None
        # 坐标自适应缩放配置（延迟加载）
        self._ref_width: Optional[int] = None
        self._ref_height: Optional[int] = None
        self._plan_width: Optional[int] = None
        self._plan_height: Optional[int] = None

    def _log(self, level: str, msg: str):
        if self.log:
            getattr(self.log, level.lower())(msg)

    # ==================== 坐标自适应缩放 ====================

    def _ensure_scale_config(self):
        """延迟加载缩放配置"""
        if self._ref_width is not None:
            return
        try:
            from settings import get_settings
            s = get_settings()
            self._ref_width = s.COORDS_SCREEN_WIDTH       # 2560（坐标参考分辨率）
            self._ref_height = s.COORDS_SCREEN_HEIGHT      # 1392
            self._plan_width = s.SCREENSHOT_PLAN_MAX_WIDTH  # 1120（LLM 识别图宽度）
            self._plan_height = s.SCREENSHOT_PLAN_MAX_HEIGHT  # 560（LLM 识别图高度）
        except Exception:
            self._ref_width, self._ref_height = 2560, 1392
            self._plan_width, self._plan_height = 1120, 560

    def adapt_coords(self, x: int, y: int) -> Tuple[int, int]:
        """
        坐标自适应缩放：从参考分辨率映射到实际窗口尺寸。

        坐标文件中的坐标基于 2560x1392，
        实际窗口可能是任意尺寸（如 1280x800），
        此方法按比例缩放坐标到当前窗口。

        scale_x = actual_width / ref_width
        scale_y = actual_height / ref_height
        """
        self._ensure_scale_config()
        self.refresh_window_rect()
        if not self.window_rect:
            return x, y

        actual_width = self.window_rect[2] - self.window_rect[0]
        actual_height = self.window_rect[3] - self.window_rect[1]

        # 窗口尺寸与参考分辨率一致，无需缩放
        if actual_width == self._ref_width and actual_height == self._ref_height:
            return x, y

        scale_x = actual_width / self._ref_width
        scale_y = actual_height / self._ref_height
        scaled_x = int(x * scale_x)
        scaled_y = int(y * scale_y)
        self._log('debug', f"坐标缩放 ({x},{y}) → ({scaled_x},{scaled_y}), "
                           f"scale=({scale_x:.3f},{scale_y:.3f}), "
                           f"窗口={actual_width}x{actual_height}")
        return scaled_x, scaled_y

    def refresh_window_rect(self) -> Optional[Tuple[int, int, int, int]]:
        """刷新窗口矩形缓存，避免使用过期尺寸做坐标缩放。"""
        if not self.hwnd or not WIN32_AVAILABLE:
            return self.window_rect
        try:
            rect = win32gui.GetWindowRect(self.hwnd)
            if self._is_usable_rect(rect):
                self.window_rect = rect
            return self.window_rect
        except Exception as e:
            self._log('debug', f"刷新窗口位置失败: {e}")
            return self.window_rect

    def llm_to_screen(
        self,
        llm_x: int,
        llm_y: int,
        image_path: Optional[str] = None,
        image_size: Optional[Tuple[int, int]] = None,
    ) -> Tuple[int, int]:
        """
        LLM 识别图坐标 → 实际屏幕坐标。

        `SCREENSHOT_PLAN_MAX_WIDTH/HEIGHT` 是缩略图上限，不是实际识别图尺寸。
        `take_screenshot(..., for_vision=True)` 使用 thumbnail 保持宽高比，
        所以换算时必须优先使用真实识别图尺寸。
        """
        self._ensure_scale_config()
        actual_plan_width = self._plan_width
        actual_plan_height = self._plan_height

        if image_size:
            actual_plan_width, actual_plan_height = image_size
        elif image_path:
            try:
                from PIL import Image

                with Image.open(image_path) as img:
                    actual_plan_width, actual_plan_height = img.size
            except Exception as exc:
                self._log('debug', f"llm_to_screen failed to read image size from {image_path}: {exc}")

        actual_plan_width = max(int(actual_plan_width or 1), 1)
        actual_plan_height = max(int(actual_plan_height or 1), 1)
        ref_x = int(llm_x * self._ref_width / actual_plan_width)
        ref_y = int(llm_y * self._ref_height / actual_plan_height)
        self._log(
            'debug',
            f"LLM coords ({llm_x},{llm_y}) -> ref ({ref_x},{ref_y}) using plan={actual_plan_width}x{actual_plan_height}",
        )
        return self.adapt_coords(ref_x, ref_y)

    # ==================== 窗口操作 ====================

    def find_window(self) -> Optional[WindowInfo]:
        """查找京麦窗口（优先 UIA，fallback win32gui）"""
        self._log('info', "查找京麦窗口...")

        # 优先复用已命中的句柄
        if WIN32_AVAILABLE and self.hwnd:
            try:
                rect = win32gui.GetWindowRect(self.hwnd)
                if self._is_usable_rect(rect) and not self._window_surface_is_blank(self.hwnd):
                    title = win32gui.GetWindowText(self.hwnd)
                    left, top, right, bottom = rect
                    self.window_rect = rect
                    return WindowInfo(
                        hwnd=self.hwnd,
                        title=title,
                        rect=rect,
                        width=right - left,
                        height=bottom - top,
                        is_visible=bool(win32gui.IsWindowVisible(self.hwnd)),
                    )
            except Exception:
                pass

        # 引擎0: 前台窗口优先（借鉴 UFOAgent 的前台窗口上下文逻辑）
        if WIN32_AVAILABLE:
            result = self._find_window_foreground()
            if result:
                return result

        # 引擎1: pywinauto UIA
        if PYWINAUTO_AVAILABLE:
            result = self._find_window_uia()
            if result:
                return result

        # 引擎2: win32gui
        if WIN32_AVAILABLE:
            result = self._find_window_win32()
            if result:
                return result

        self._log('error', "未找到京麦窗口")
        return None

    def _find_window_foreground(self) -> Optional[WindowInfo]:
        """优先使用当前前台大窗口，解决 jd_ 幽灵句柄误命中的问题。"""
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            if not hwnd:
                return None

            rect_obj = ctypes.wintypes.RECT()
            ctypes.windll.user32.GetWindowRect(hwnd, ctypes.pointer(rect_obj))
            rect = (rect_obj.left, rect_obj.top, rect_obj.right, rect_obj.bottom)
            if not self._is_usable_rect(rect):
                return None

            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
            title = buf.value or ""
            if self._is_excluded_title(title):
                return None

            process_name = self._get_process_name(hwnd)
            if self._is_excluded_process(process_name):
                self._log('debug', f"skip excluded foreground process: title='{title}', process='{process_name}'")
                return None
            has_jingmai_hint = self._has_any_jingmai_window()
            if not self._is_matching_title(title):
                if not (has_jingmai_hint and process_name in BROWSER_PROCESS_HINTS):
                    return None
            if self._window_surface_is_blank(hwnd):
                self._log('debug', f"skip blank foreground window: title='{title}', process='{process_name}'")
                return None

            left, top, right, bottom = rect
            self.hwnd = hwnd
            self.window_rect = rect
            self._log('info', f"命中前台窗口: title='{title}', process='{process_name}', rect={rect}")
            return WindowInfo(
                hwnd=hwnd,
                title=title,
                rect=rect,
                width=right - left,
                height=bottom - top,
                is_visible=True,
            )
        except Exception as e:
            self._log('debug', f"前台窗口查找失败: {e}")
            return None

    def _find_window_uia(self, timeout: float = 10.0) -> Optional[WindowInfo]:
        """
        UIA 方式查找窗口（带超时）。

        Desktop(backend="uia").windows() 在京麦窗口不存在时会遍历所有窗口，
        耗时 1-2 分钟。加超时保护，避免无意义等待。
        """
        import threading
        result_holder = {"result": None}

        def _uia_search():
            try:
                desktop = Desktop(backend="uia")
                best = None
                best_area = 0
                for w in desktop.windows():
                    try:
                        title = w.window_text()
                        if not self._is_matching_title(title):
                            continue
                        rect = w.rectangle()
                        if not self._is_usable_rect((rect.left, rect.top, rect.right, rect.bottom)):
                            continue
                        width, height = rect.width(), rect.height()
                        area = width * height
                        if area > best_area:
                            best_area = area
                            best = w
                    except Exception:
                        continue

                if best:
                    rect = best.rectangle()
                    self.hwnd = best.handle if hasattr(best, 'handle') else 0
                    self.window_rect = (rect.left, rect.top, rect.right, rect.bottom)
                    result_holder["result"] = WindowInfo(
                        hwnd=self.hwnd,
                        title=best.window_text(),
                        rect=self.window_rect,
                        width=rect.width(),
                        height=rect.height(),
                        is_visible=True,
                    )
            except Exception as e:
                self._log('debug', f"UIA 查找失败: {e}")

        t = threading.Thread(target=_uia_search, daemon=True)
        t.start()
        t.join(timeout=timeout)
        if t.is_alive():
            self._log('warning', f"UIA 查找超时 ({timeout}s)，跳过")
            return None
        return result_holder["result"]

    def _find_window_win32(self) -> Optional[WindowInfo]:
        """win32gui 方式查找窗口"""
        candidates = []

        def enum_handler(hwnd, results):
            title = win32gui.GetWindowText(hwnd)
            if self._is_excluded_title(title):
                return

            rect = win32gui.GetWindowRect(hwnd)
            if not self._is_usable_rect(rect):
                return

            process_name = self._get_process_name(hwnd)
            if self._is_excluded_process(process_name):
                return
            title_match = self._is_matching_title(title)
            process_match = process_name in JINGMAI_PROCESS_HINTS
            if not (title_match or process_match):
                return

            left, top, right, bottom = rect
            visible = bool(win32gui.IsWindowVisible(hwnd))
            area = (right - left) * (bottom - top)
            blank = self._window_surface_is_blank(hwnd)
            score = (
                4 if title_match and visible else
                3 if title_match else
                2 if process_match and visible else
                1
            )
            results.append((0 if blank else 1, score, area, hwnd, rect, title, visible, process_name))

        win32gui.EnumWindows(enum_handler, candidates)

        if candidates:
            _, _, _, hwnd, rect, title, visible, process_name = max(
                candidates,
                key=lambda item: (item[0], item[1], item[2]),
            )
            left, top, right, bottom = rect
            self.hwnd = hwnd
            self.window_rect = rect
            self._log(
                "info",
                f"win32 命中窗口: title='{title}', process='{process_name}', visible={visible}, rect={rect}",
            )
            return WindowInfo(
                hwnd=hwnd, title=title, rect=rect,
                width=right - left, height=bottom - top,
                is_visible=visible,
            )
        return None

    def activate_window(self) -> bool:
        """激活并调整窗口"""
        if not self.hwnd or not WIN32_AVAILABLE:
            return True
        try:
            from settings import get_settings

            settings = get_settings()
            win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
            time.sleep(0.2)
            current_rect = win32gui.GetWindowRect(self.hwnd)
            if self._is_usable_rect(current_rect):
                current_width = current_rect[2] - current_rect[0]
                current_height = current_rect[3] - current_rect[1]
                if current_width < settings.WINDOW_WIDTH or current_height < settings.WINDOW_HEIGHT:
                    win32gui.SetWindowPos(
                        self.hwnd, 0, 100, 100, settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT, 0
                    )
                    time.sleep(0.2)
            # 使用多种方式激活窗口
            try:
                win32gui.SetForegroundWindow(self.hwnd)
            except Exception as fg_err:
                self._log('warning', f"SetForegroundWindow 失败: {fg_err}, 尝试其他方式")
                try:
                    # 尝试使用 SwitchToThisWindow (更强制的方式)
                    win32api.SwitchToThisWindow(self.hwnd, True)
                except Exception as sw_err:
                    self._log('warning', f"SwitchToThisWindow 也失败: {sw_err}")
                    # 最后尝试使用 ShowWindow + BringWindowToTop
                    win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)
                    win32gui.BringWindowToTop(self.hwnd)
            time.sleep(0.3)
            self.window_rect = win32gui.GetWindowRect(self.hwnd)
            if not self._is_usable_rect(self.window_rect):
                self._log('error', f"窗口位置异常，疑似无效目标: {self.window_rect}")
                return False
            if self._window_surface_is_blank(self.hwnd):
                self._log('warning', "window activated but surface is blank, trying recovery")
                if not self._recover_blank_window():
                    return False
                self.window_rect = win32gui.GetWindowRect(self.hwnd)
            self._log('ok', f"窗口已激活: {self.window_rect}")
            return True
        except Exception as e:
            self._log('error', f"窗口激活失败: {e}")
            return False

    def _window_surface_is_blank(self, hwnd: Optional[int] = None) -> bool:
        hwnd = hwnd or self.hwnd
        if not hwnd:
            return False
        try:
            image = self._print_window_capture(hwnd)
            if image is None:
                return False
            gray = image.convert("L").resize((64, 64))
            pixels = list(gray.getdata())
            if not pixels:
                return False
            min_px = min(pixels)
            max_px = max(pixels)
            avg_px = sum(pixels) / len(pixels)
            return avg_px >= 245 and (max_px - min_px) <= 4
        except Exception:
            return False

    def _recover_blank_window(self) -> bool:
        if not self.hwnd or not WIN32_AVAILABLE:
            return False
        try:
            win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
            time.sleep(0.2)
            win32gui.ShowWindow(self.hwnd, win32con.SW_MAXIMIZE)
            time.sleep(0.2)
            win32gui.BringWindowToTop(self.hwnd)
            time.sleep(0.3)
            if not self._window_surface_is_blank(self.hwnd):
                return True
        except Exception as exc:
            self._log('debug', f"blank window restore attempt failed: {exc}")

        alt = self._find_window_win32()
        if not alt:
            return False
        self.hwnd = alt.hwnd
        self.window_rect = alt.rect
        try:
            win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
            time.sleep(0.2)
            win32gui.BringWindowToTop(self.hwnd)
            time.sleep(0.3)
        except Exception:
            pass
        return not self._window_surface_is_blank(self.hwnd)

    @staticmethod
    def _is_matching_title(title: str) -> bool:
        """标题过滤，避免误命中 IDE、终端和无关小窗。"""
        if not title:
            return False
        title_lower = title.lower()
        return any(kw in title_lower for kw in WINDOW_KEYWORDS) and not any(
            ex in title_lower for ex in WINDOW_EXCLUDE_KEYWORDS
        )

    @staticmethod
    def _is_excluded_title(title: str) -> bool:
        if not title:
            return False
        title_lower = title.lower()
        if any(ex in title_lower for ex in ("咚咚", "融合工作台")):
            return True
        return any(ex in title_lower for ex in WINDOW_EXCLUDE_KEYWORDS)

    @staticmethod
    def _is_excluded_process(process_name: str) -> bool:
        if not process_name:
            return False
        return process_name.lower() in WINDOW_EXCLUDE_PROCESS_HINTS

    @staticmethod
    def _is_usable_rect(rect: Tuple[int, int, int, int]) -> bool:
        """
        过滤最小化/离屏/尺寸异常窗口，避免命中 Session 幽灵窗口。

        参考 UFOAgent 的 _update_window_context 逻辑：
        - 最小尺寸放宽到 100x100（京麦窗口不一定最大化，可能 800x600 等）
        - 屏幕范围检查用动态分辨率（允许多显示器和 DPI 缩放）
        - 允许 -10px 偏移（窗口阴影/边框的常见行为）
        """
        left, top, right, bottom = rect
        width = right - left
        height = bottom - top
        # 尺寸过小 → 最小化或幽灵窗口
        if width < 100 or height < 100:
            return False
        # 坐标明显异常
        if right <= left or bottom <= top:
            return False
        # Session 幽灵窗口（坐标 -32000 附近）
        if left <= -30000 or top <= -30000:
            return False
        # 窗口完全在屏幕外（允许负偏移 -10，窗口边框/阴影的常见行为）
        if right <= -10 or bottom <= -10:
            return False
        # 窗口尺寸上限检查：超过 2 倍屏幕分辨率 → 异常
        try:
            screen_w = ctypes.windll.user32.GetSystemMetrics(0)
            screen_h = ctypes.windll.user32.GetSystemMetrics(1)
            if width > screen_w * 2 or height > screen_h * 2:
                return False
        except Exception:
            pass
        return True

    def _has_any_jingmai_window(self) -> bool:
        """检测系统里是否存在京麦相关句柄，包括最小化/离屏窗口。"""
        if not WIN32_AVAILABLE:
            return False

        found = {"value": False}

        def enum_handler(hwnd, _):
            title = win32gui.GetWindowText(hwnd)
            if self._is_matching_title(title):
                found["value"] = True

        try:
            win32gui.EnumWindows(enum_handler, None)
        except Exception:
            return False
        return found["value"]

    @staticmethod
    def _get_process_name(hwnd: int) -> str:
        """获取窗口所属进程名（不含 .exe）。"""
        try:
            pid = ctypes.wintypes.DWORD()
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if not pid.value:
                return ""

            PROCESS_QUERY_INFORMATION = 0x0400
            PROCESS_VM_READ = 0x0010
            handle = ctypes.windll.kernel32.OpenProcess(
                PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
                False,
                pid.value,
            )
            if not handle:
                return ""

            try:
                buf = ctypes.create_unicode_buffer(260)
                ctypes.windll.psapi.GetModuleFileNameExW(handle, None, buf, 260)
                exe_path = buf.value
                return os.path.splitext(os.path.basename(exe_path))[0].lower()
            finally:
                ctypes.windll.kernel32.CloseHandle(handle)
        except Exception:
            return ""

    def window_to_screen(self, x: int, y: int) -> Tuple[int, int]:
        """窗口坐标转屏幕坐标"""
        if not self.window_rect:
            return x, y
        return self.window_rect[0] + x, self.window_rect[1] + y

    def screen_to_window(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        """屏幕坐标转窗口坐标"""
        if not self.window_rect:
            return screen_x, screen_y
        return screen_x - self.window_rect[0], screen_y - self.window_rect[1]

    # ==================== 点击操作 ====================

    def _release_mouse_buttons(self):
        """移动前强制释放鼠标键，防止残留按下态导致 move 变拖拽。"""
        if not WIN32_AVAILABLE:
            return
        try:
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
        except Exception:
            pass

    def _human_move_to(self, screen_x: int, screen_y: int):
        """仿人鼠标移动：三次贝塞尔曲线 + Ease Out 缓动 + 随机抖动
        参考 sightflow-desktop-agent 的 humanLikeMove()
        """
        import pyautogui
        self._release_mouse_buttons()
        start_x, start_y = pyautogui.position()
        dx = screen_x - start_x
        dy = screen_y - start_y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance < 3:
            pyautogui.moveTo(screen_x, screen_y)
            return

        # 步数根据距离自适应（5-15步）
        steps = min(15, max(5, int(distance / 40) + random.randint(0, 2)))

        # 随机控制点（Cubic Bezier）
        ctrl1_x = start_x + dx * random.random() * 0.5 + (random.random() - 0.5) * distance * 0.2
        ctrl1_y = start_y + dy * random.random() * 0.5 + (random.random() - 0.5) * distance * 0.2
        ctrl2_x = start_x + dx * (0.5 + random.random() * 0.5) + (random.random() - 0.5) * distance * 0.2
        ctrl2_y = start_y + dy * (0.5 + random.random() * 0.5) + (random.random() - 0.5) * distance * 0.2

        for i in range(1, steps + 1):
            t = i / steps
            # Ease Out 非线性缓动
            ease_t = t * (2 - t)
            mt = 1 - ease_t

            # 贝塞尔曲线公式: B(t) = (1-t)^3*P0 + 3*(1-t)^2*t*P1 + 3*(1-t)*t^2*P2 + t^3*P3
            bx = (mt**3 * start_x + 3 * mt**2 * ease_t * ctrl1_x
                  + 3 * mt * ease_t**2 * ctrl2_x + ease_t**3 * screen_x)
            by = (mt**3 * start_y + 3 * mt**2 * ease_t * ctrl1_y
                  + 3 * mt * ease_t**2 * ctrl2_y + ease_t**3 * screen_y)

            # 随机抖动（最后一步不加，确保精准落点）
            if i < steps:
                bx += (random.random() - 0.5) * 2
                by += (random.random() - 0.5) * 2

            pyautogui.moveTo(int(bx), int(by))

            # 变频延迟：尾部 20% 减速
            step_delay = 0.002 + random.random() * 0.003
            if i > steps * 0.8:
                step_delay += 0.003
            time.sleep(step_delay)

    def _human_click(self, button: str = 'left'):
        """仿人点击：短暂停顿后执行原子 click，避免残留按下态。"""
        import pyautogui
        time.sleep(0.03 + random.random() * 0.04)
        pyautogui.click(button=button)
        time.sleep(0.05 + random.random() * 0.1)   # 50-150ms 后停顿

    def click(self, x: int, y: int, delay: float = 0.5) -> bool:
        """在窗口坐标处点击（自动缩放坐标）- 仿人移动+点击"""
        x, y = self.adapt_coords(x, y)
        if not WIN32_AVAILABLE:
            self._log('debug', f"[模拟] 点击 ({x}, {y})")
            time.sleep(delay)
            return True
        if not self.hwnd:
            self._log('error', "窗口未找到")
            return False
        screen_x, screen_y = self.window_to_screen(x, y)
        try:
            import pyautogui
            win32gui.SetForegroundWindow(self.hwnd)
            time.sleep(0.1)
            # 仿人移动 + 仿人点击
            self._human_move_to(screen_x, screen_y)
            time.sleep(0.05 + random.random() * 0.1)
            self._human_click(button='left')
            time.sleep(delay)
            return True
        except Exception:
            # 降级：pyautogui 原子点击
            try:
                pyautogui.click(screen_x, screen_y)
                time.sleep(delay)
                return True
            except Exception as e:
                self._log('error', f"点击失败: {e}")
                return False

    def double_click(self, x: int, y: int, delay: float = 0.5) -> bool:
        """双击 - 单次前置激活 + 原子 doubleClick，避免按下态遗留。"""
        x, y = self.adapt_coords(x, y)
        if not WIN32_AVAILABLE or not self.hwnd:
            return False
        try:
            import pyautogui
            win32gui.SetForegroundWindow(self.hwnd)
            time.sleep(0.1)
            screen_x, screen_y = self.window_to_screen(x, y)
            self._human_move_to(screen_x, screen_y)
            time.sleep(0.05 + random.random() * 0.1)
            pyautogui.doubleClick(screen_x, screen_y, interval=0.04 + random.random() * 0.06)
            time.sleep(delay)
            return True
        except Exception as e:
            self._log('error', f"双击失败: {e}")
            return False

    def right_click(self, x: int, y: int, delay: float = 0.5) -> bool:
        """右键点击（自动缩放坐标）- 仿人移动+点击"""
        x, y = self.adapt_coords(x, y)
        if not WIN32_AVAILABLE or not self.hwnd:
            return False
        screen_x, screen_y = self.window_to_screen(x, y)
        try:
            import pyautogui
            win32gui.SetForegroundWindow(self.hwnd)
            time.sleep(0.1)
            self._human_move_to(screen_x, screen_y)
            time.sleep(0.05 + random.random() * 0.1)
            self._human_click(button='right')
            time.sleep(delay)
            return True
        except Exception:
            # 降级
            try:
                pyautogui.click(screen_x, screen_y, button='right')
                time.sleep(delay)
                return True
            except Exception as e:
                self._log('error', f"右键点击失败: {e}")
                return False

    # ==================== UIA 窗口缓存 ====================

    def get_uia_window(self, timeout: float = 10.0):
        """获取京麦 UIA 窗口对象（带 5s TTL 缓存，避免重复遍历）
        参考 sightflow window-utils.ts 的窗口信息缓存
        """
        if not PYWINAUTO_AVAILABLE:
            return None

        # 检查缓存是否有效（5秒 TTL）
        cache_key = '_uia_window_cache'
        cache_time_key = '_uia_window_cache_time'
        if hasattr(self, cache_key) and hasattr(self, cache_time_key):
            if time.time() - getattr(self, cache_time_key) < 5.0:
                try:
                    cached = getattr(self, cache_key)
                    cached.window_text()  # 验证窗口仍然有效
                    return cached
                except Exception:
                    pass  # 缓存失效，重新查找

        # 带超时的窗口查找（UIA 枚举可能很慢）
        result = {"window": None}

        def _search():
            try:
                desktop = Desktop(backend="uia")
                for w in desktop.windows():
                    try:
                        title = w.window_text()
                        if not any(kw in (title or "").lower() for kw in WINDOW_KEYWORDS):
                            continue
                        result["window"] = w
                        return
                    except Exception:
                        continue
            except Exception:
                pass

        import threading
        t = threading.Thread(target=_search, daemon=True)
        t.start()
        t.join(timeout=timeout)

        window = result["window"]
        if window:
            setattr(self, cache_key, window)
            setattr(self, cache_time_key, time.time())
        return window

    # ==================== 页面等待 ====================

    def wait_for_ready(self, timeout: float = 5.0, check_interval: float = 0.3) -> bool:
        """等待页面稳定（通过连续截图像素 hash 变化检测）
        参考 sightflow image-compare.ts 的 pixelmatch diff 检测
        连续 2 次截图 hash 相同 → 页面加载完毕
        """
        if not self.hwnd or not WIN32_AVAILABLE:
            time.sleep(timeout)
            return True
        import hashlib
        start = time.time()
        last_hash = None
        stable_count = 0
        while time.time() - start < timeout:
            try:
                left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
                width, height = right - left, bottom - top
                # 只采样中心 50% 区域（避免边缘动画干扰）
                sample_w = width // 2
                sample_h = height // 2
                hwindc = win32gui.GetWindowDC(self.hwnd)
                mfcdc = win32ui.CreateDCFromHandle(hwindc)
                savedc = mfcdc.CreateCompatibleDC()
                bitmap = win32ui.CreateBitmap()
                bitmap.CreateCompatibleBitmap(mfcdc, sample_w, sample_h)
                savedc.SelectObject(bitmap)
                savedc.BitBlt((0, 0), (sample_w, sample_h), mfcdc,
                              (width // 4, height // 4), win32con.SRCCOPY)
                bits = bitmap.GetBitmapBits(True)
                current_hash = hashlib.md5(bits).hexdigest()
                win32gui.DeleteObject(bitmap.GetHandle())
                savedc.DeleteDC()
                mfcdc.DeleteDC()
                win32gui.ReleaseDC(self.hwnd, hwindc)
                if current_hash == last_hash:
                    stable_count += 1
                    if stable_count >= 2:
                        self._log('debug', f"页面稳定 (耗时 {time.time()-start:.1f}s)")
                        return True
                else:
                    stable_count = 0
                    last_hash = current_hash
                time.sleep(check_interval)
            except Exception:
                time.sleep(check_interval)
        self._log('debug', f"页面等待超时 ({timeout}s)")
        return False

    # ==================== 键盘操作 ====================

    def type_text(self, text: str, delay: float = 0.1) -> bool:
        """输入文本"""
        if not WIN32_AVAILABLE or not self.hwnd:
            return False
        try:
            win32gui.SetForegroundWindow(self.hwnd)
            time.sleep(0.2)
            for char in text:
                win32api.SendMessage(self.hwnd, win32con.WM_CHAR, ord(char), 0)
                time.sleep(delay)
            return True
        except Exception as e:
            self._log('error', f"输入失败: {e}")
            return False

    def press_key(self, vk_code: int, delay: float = 0.1) -> bool:
        """按键"""
        if not WIN32_AVAILABLE or not self.hwnd:
            return False
        try:
            win32gui.SetForegroundWindow(self.hwnd)
            win32api.keybd_event(vk_code, 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(delay)
            return True
        except Exception as e:
            self._log('error', f"按键失败: {e}")
            return False

    def press_enter(self, delay: float = 0.3) -> bool:
        return self.press_key(0x0D, delay)

    def press_tab(self, delay: float = 0.3) -> bool:
        return self.press_key(0x09, delay)

    def press_escape(self, delay: float = 0.3) -> bool:
        return self.press_key(0x1B, delay)

    # ==================== UIA 元素操作 ====================

    def inspect_elements(self, control_type: str = None) -> List[Dict[str, Any]]:
        """扫描窗口内 UIA 元素"""
        if not PYWINAUTO_AVAILABLE:
            self._log('warn', "pywinauto 不可用")
            return []

        try:
            desktop = Desktop(backend="uia")
            results = []
            for w in desktop.windows():
                try:
                    title = w.window_text()
                    if not any(kw in (title or "").lower() for kw in WINDOW_KEYWORDS):
                        continue
                    descendants = (w.descendants(control_type=control_type)
                                   if control_type else w.descendants())

                    for elem in descendants:
                        try:
                            name = elem.element_info.name or ""
                            ctrl_type = elem.element_info.control_type or ""
                            rect = elem.rectangle()
                            results.append({
                                "name": name,
                                "type": ctrl_type,
                                "x": rect.left,
                                "y": rect.top,
                                "width": rect.width(),
                                "height": rect.height(),
                            })
                        except Exception:
                            continue
                    break  # 只处理第一个匹配的窗口
                except Exception:
                    continue

            return results
        except Exception as e:
            self._log('error', f"元素扫描失败: {e}")
            return []

    @staticmethod
    def _print_window_capture(hwnd: int):
        try:
            from PIL import Image
            import win32ui

            rect = win32gui.GetWindowRect(hwnd)
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]
            if width <= 0 or height <= 0:
                return None

            hwnd_dc = win32gui.GetWindowDC(hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()
            bmp = win32ui.CreateBitmap()
            bmp.CreateCompatibleBitmap(mfc_dc, width, height)
            save_dc.SelectObject(bmp)

            pw_render_full_content = 2
            result = ctypes.windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), pw_render_full_content)
            if not result:
                result = ctypes.windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 1)
            if not result:
                save_dc.DeleteDC()
                mfc_dc.DeleteDC()
                win32gui.ReleaseDC(hwnd, hwnd_dc)
                win32gui.DeleteObject(bmp.GetHandle())
                return None

            bmpinfo = bmp.GetInfo()
            bmpbytes = bmp.GetBitmapBits(True)
            image = Image.frombuffer(
                "RGB",
                (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
                bmpbytes,
                "raw",
                "BGRX",
                0,
                1,
            )

            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwnd_dc)
            win32gui.DeleteObject(bmp.GetHandle())
            return image
        except Exception:
            return None

    def take_screenshot(self, save_path: str = None, for_vision: bool = False) -> Optional[str]:
        """截图"""
        if not WIN32_AVAILABLE or not self.hwnd:
            return None
        hwindc = None
        mfcdc = None
        savedc = None
        bitmap = None
        try:
            from pathlib import Path

            from PIL import Image
            import win32ui
            from infrastructure.path_validator import validate_save_path
            from settings import get_settings

            settings = get_settings()
            if not save_path:
                screenshot_dir = settings.SCREENSHOT_DIR
                Path(screenshot_dir).mkdir(parents=True, exist_ok=True)
                save_path = str(Path(screenshot_dir) / f"screenshot_{int(time.time())}.png")
            else:
                save_dir = validate_save_path(str(Path(save_path).parent), document_dir=settings.SCREENSHOT_DIR)
                save_path = str(Path(save_dir) / Path(save_path).name)

            left, top, right, bottom = self.refresh_window_rect() or win32gui.GetWindowRect(self.hwnd)
            width, height = right - left, bottom - top

            hwindc = win32gui.GetWindowDC(self.hwnd)
            mfcdc = win32ui.CreateDCFromHandle(hwindc)
            savedc = mfcdc.CreateCompatibleDC()
            bitmap = win32ui.CreateBitmap()
            bitmap.CreateCompatibleBitmap(mfcdc, width, height)
            savedc.SelectObject(bitmap)
            savedc.BitBlt((0, 0), (width, height), mfcdc, (0, 0), win32con.SRCCOPY)
            bmpinfo = bitmap.GetInfo()
            bmpbytes = bitmap.GetBitmapBits(True)
            image = Image.frombuffer(
                "RGB",
                (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
                bmpbytes,
                "raw",
                "BGRX",
                0,
                1,
            )
            if image.getbbox() is None:
                self._log('warning', "BitBlt screenshot empty, trying PrintWindow fallback")
                fallback_image = self._print_window_capture(self.hwnd)
                if fallback_image is not None:
                    image = fallback_image

            output = image
            if for_vision:
                output = image.copy()
                output.thumbnail(
                    (settings.SCREENSHOT_PLAN_MAX_WIDTH, settings.SCREENSHOT_PLAN_MAX_HEIGHT),
                    Image.Resampling.LANCZOS,
                )

            save_path = str(Path(save_path))
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            output.save(save_path, format="PNG", optimize=True)

            debug_enabled = os.environ.get("JINGMAI_DEBUG_SCREENSHOTS", "").strip().lower() in {"1", "true", "yes"}
            if for_vision and debug_enabled:
                debug_path = str(Path(save_path).with_name(f"{Path(save_path).stem}_full.png"))
                image.save(debug_path, format="PNG", optimize=True)

            win32gui.DeleteObject(bitmap.GetHandle())
            savedc.DeleteDC()
            mfcdc.DeleteDC()
            win32gui.ReleaseDC(self.hwnd, hwindc)

            return save_path
        except Exception as e:
            self._log('error', f"截图失败: {e}")
            return None
