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


# 京麦窗口标题关键词
WINDOW_KEYWORDS = ["jd_", "京麦", "jingmai", "JD"]
MIN_WINDOW_SIZE = (1024, 768)


class JingmaiLocator:
    """双引擎元素定位器"""

    def __init__(self, log=None):
        self.log = log
        self.hwnd: Optional[int] = None
        self.window_rect: Optional[Tuple[int, int, int, int]] = None
        self._desktop = None

    def _log(self, level: str, msg: str):
        if self.log:
            getattr(self.log, level.lower())(msg)

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
                    if not title:
                        continue
                    title_lower = title.lower()
                    if not any(kw in title_lower for kw in WINDOW_KEYWORDS):
                        continue
                    rect = w.rectangle()
                    width, height = rect.width(), rect.height()
                    if width < MIN_WINDOW_SIZE[0] or height < MIN_WINDOW_SIZE[1]:
                        continue
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
        result = []

        def enum_handler(hwnd, results):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    title_lower = title.lower()
                    if any(kw in title_lower for kw in WINDOW_KEYWORDS):
                        results.append(hwnd)

        win32gui.EnumWindows(enum_handler, result)

        if result:
            hwnd = result[0]
            title = win32gui.GetWindowText(hwnd)
            rect = win32gui.GetWindowRect(hwnd)
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
            win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
            time.sleep(0.2)
            win32gui.SetWindowPos(self.hwnd, 0, 100, 100, 1280, 800, 0)
            time.sleep(0.2)
            win32gui.SetForegroundWindow(self.hwnd)
            time.sleep(0.3)
            self.window_rect = win32gui.GetWindowRect(self.hwnd)
            self._log('ok', f"窗口已激活: {self.window_rect}")
            return True
        except Exception as e:
            self._log('error', f"窗口激活失败: {e}")
            return False

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
        """在窗口坐标处点击"""
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
        """右键点击"""
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
                save_path = str(Path("logs") / f"screenshot_{int(time.time())}.png")

            left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
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
