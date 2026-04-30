"""
京麦商品发布自动化 - 双引擎元素定位器
UIA 元素查找 + 坐标 fallback
"""
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
# 排除关键词（标题含这些的不匹配）
WINDOW_EXCLUDE_KEYWORDS = ["code", "vscode", "visual studio", "pycharm", "idea", "terminal", "cmd", "powershell"]
MIN_WINDOW_SIZE = (1024, 768)


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

    def llm_to_screen(self, llm_x: int, llm_y: int) -> Tuple[int, int]:
        """
        LLM 识别图坐标 → 实际屏幕坐标。

        LLM 返回的坐标基于识别图（1120x560），
        需要先映射到参考分辨率（2560x1392），
        再通过 adapt_coords 映射到实际窗口。

        scale_to_ref_x = ref_width / plan_width  = 2560/1120 = 2.286
        scale_to_ref_y = ref_height / plan_height = 1392/560  = 2.486
        """
        self._ensure_scale_config()
        # 识别图 → 参考分辨率
        ref_x = int(llm_x * self._ref_width / self._plan_width)
        ref_y = int(llm_y * self._ref_height / self._plan_height)
        # 参考分辨率 → 实际窗口
        return self.adapt_coords(ref_x, ref_y)

    # ==================== 窗口操作 ====================

    def find_window(self) -> Optional[WindowInfo]:
        """查找京麦窗口（优先 UIA，fallback win32gui）"""
        self._log('info', "查找京麦窗口...")

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

    def _find_window_uia(self) -> Optional[WindowInfo]:
        """UIA 方式查找窗口"""
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
                return WindowInfo(
                    hwnd=self.hwnd,
                    title=best.window_text(),
                    rect=self.window_rect,
                    width=rect.width(),
                    height=rect.height(),
                    is_visible=True,
                )
        except Exception as e:
            self._log('debug', f"UIA 查找失败: {e}")
        return None

    def _find_window_win32(self) -> Optional[WindowInfo]:
        """win32gui 方式查找窗口"""
        candidates = []

        def enum_handler(hwnd, results):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if not self._is_matching_title(title):
                    return
                rect = win32gui.GetWindowRect(hwnd)
                if not self._is_usable_rect(rect):
                    return
                left, top, right, bottom = rect
                results.append((hwnd, rect, (right - left) * (bottom - top)))

        win32gui.EnumWindows(enum_handler, candidates)

        if candidates:
            hwnd, rect, _ = max(candidates, key=lambda item: item[2])
            title = win32gui.GetWindowText(hwnd)
            left, top, right, bottom = rect
            self.hwnd = hwnd
            self.window_rect = rect
            return WindowInfo(
                hwnd=hwnd, title=title, rect=rect,
                width=right - left, height=bottom - top,
                is_visible=True,
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
            win32gui.SetForegroundWindow(self.hwnd)
            time.sleep(0.3)
            self.window_rect = win32gui.GetWindowRect(self.hwnd)
            if not self._is_usable_rect(self.window_rect):
                self._log('error', f"窗口位置异常，疑似无效目标: {self.window_rect}")
                return False
            self._log('ok', f"窗口已激活: {self.window_rect}")
            return True
        except Exception as e:
            self._log('error', f"窗口激活失败: {e}")
            return False

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
    def _is_usable_rect(rect: Tuple[int, int, int, int]) -> bool:
        """过滤最小化/离屏/尺寸异常窗口，避免命中 Session 幽灵窗口。"""
        left, top, right, bottom = rect
        width = right - left
        height = bottom - top
        if width < MIN_WINDOW_SIZE[0] or height < MIN_WINDOW_SIZE[1]:
            return False
        if right <= left or bottom <= top:
            return False
        if left <= -30000 or top <= -30000:
            return False
        if right <= 0 or bottom <= 0:
            return False
        return True

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

    def click(self, x: int, y: int, delay: float = 0.5) -> bool:
        """在窗口坐标处点击（自动缩放坐标）"""
        # 坐标自适应缩放
        x, y = self.adapt_coords(x, y)
        if not WIN32_AVAILABLE:
            self._log('debug', f"[模拟] 点击 ({x}, {y})")
            time.sleep(delay)
            return True
        if not self.hwnd:
            self._log('error', "窗口未找到")
            return False
        try:
            win32gui.SetForegroundWindow(self.hwnd)
            time.sleep(0.1)
            screen_x, screen_y = self.window_to_screen(x, y)
            win32api.SetCursorPos((screen_x, screen_y))
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            time.sleep(delay)
            return True
        except Exception as e:
            self._log('error', f"点击失败: {e}")
            return False

    def double_click(self, x: int, y: int, delay: float = 0.5) -> bool:
        """双击"""
        self.click(x, y, delay=0.05)
        time.sleep(0.1)
        self.click(x, y, delay=delay)
        return True

    def right_click(self, x: int, y: int, delay: float = 0.5) -> bool:
        """右键点击（自动缩放坐标）"""
        x, y = self.adapt_coords(x, y)
        if not WIN32_AVAILABLE or not self.hwnd:
            return False
        try:
            win32gui.SetForegroundWindow(self.hwnd)
            screen_x, screen_y = self.window_to_screen(x, y)
            win32api.SetCursorPos((screen_x, screen_y))
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
            time.sleep(delay)
            return True
        except Exception as e:
            self._log('error', f"右键点击失败: {e}")
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
            # 重新查找窗口
            if control_type:
                elements = desktop.windows()
            else:
                elements = []

            results = []
            for w in desktop.windows():
                try:
                    title = w.window_text()
                    if not any(kw in (title or "").lower() for kw in WINDOW_KEYWORDS):
                        continue
                    if control_type:
                        descendants = w.descendants(control_type=control_type)
                    else:
                        descendants = w.descendants()

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

    def take_screenshot(self, save_path: str = None) -> Optional[str]:
        """截图"""
        if not WIN32_AVAILABLE or not self.hwnd:
            return None
        try:
            import win32ui
            if not save_path:
                from pathlib import Path
                from settings import get_settings
                screenshot_dir = get_settings().SCREENSHOT_DIR
                Path(screenshot_dir).mkdir(parents=True, exist_ok=True)
                save_path = str(Path(screenshot_dir) / f"screenshot_{int(time.time())}.png")

            left, top, right, bottom = self.refresh_window_rect() or win32gui.GetWindowRect(self.hwnd)
            width, height = right - left, bottom - top

            hwindc = win32gui.GetWindowDC(self.hwnd)
            mfcdc = win32ui.CreateDCFromHandle(hwindc)
            savedc = mfcdc.CreateCompatibleDC()
            bitmap = win32ui.CreateBitmap()
            bitmap.CreateCompatibleBitmap(mfcdc, width, height)
            savedc.SelectObject(bitmap)
            savedc.BitBlt((0, 0), (width, height), mfcdc, (0, 0), win32con.SRCCOPY)
            bitmap.SaveBitmapFile(savedc, save_path)

            win32gui.DeleteObject(bitmap.GetHandle())
            savedc.DeleteDC()
            mfcdc.DeleteDC()
            win32gui.ReleaseDC(self.hwnd, hwindc)

            return save_path
        except Exception as e:
            self._log('error', f"截图失败: {e}")
            return None
