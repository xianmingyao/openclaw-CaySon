"""UFO/UIA/Win32 桌面能力适配边界。"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import sys
from typing import Any, Protocol

from jm_ufo_agent.agents.base import AgentResult
from jm_ufo_agent.commands.base import Command


@dataclass(frozen=True)
class WindowInfo:
    """窗口树中的一个窗口摘要。"""

    handle: int | None
    title: str
    class_name: str
    control_type: str = ""
    children_count: int = 0


@dataclass(frozen=True)
class JingmaiWindowFacts:
    """京麦窗口技术事实。"""

    found: bool
    main_title: str = ""
    main_class_name: str = ""
    qt_child_count: int = 0
    webview_pane_count: int = 0
    html_edit_count: int = 0
    html_combobox_count: int = 0
    html_button_count: int = 0
    panes: list[WindowInfo] = field(default_factory=list)

    def is_expected_qt_shell(self) -> bool:
        """判断是否命中文档要求的 Qt5 主壳。"""

        # 设计文档要求识别 Qt51511QWindowIcon，而不是误判为普通 CEF。
        # class_name 可能由不同底层库返回大小写差异，所以统一小写比较。
        # found 为 False 时直接失败，避免空窗口被误判。
        return self.found and self.main_class_name.lower() == "qt51511qwindowicon".lower()

    def webview_summary(self) -> dict[str, Any]:
        """返回 WebView 和 HTML 控件可达性摘要。"""

        # 该摘要直接服务 F14 验收。
        # html_*_count 为 0 时表示 HTML 控件没有暴露给 UIA。
        # panes 只保留轻量窗口信息，避免把完整窗口树塞进状态。
        return {
            "webview_pane_count": self.webview_pane_count,
            "html_edit_count": self.html_edit_count,
            "html_combobox_count": self.html_combobox_count,
            "html_button_count": self.html_button_count,
            "panes": [pane.__dict__ for pane in self.panes],
        }


class WindowInspectorBackend(Protocol):
    """窗口检测 backend 协议。"""

    async def inspect_jingmai(self) -> JingmaiWindowFacts:
        """返回京麦窗口技术事实。"""

    async def focus_window(self, title_keyword: str) -> bool:
        """按标题关键字聚焦窗口。"""

    async def screenshot(self, output_path: Path) -> Path:
        """截取当前目标窗口截图。"""


class Win32ApiAdapter:
    """最小 Win32 窗口枚举适配器。"""

    def enum_windows(self) -> list[int]:
        """枚举当前桌面顶层窗口句柄。"""

        # 该方法只读取窗口句柄，不执行点击或输入。
        # ctypes 延迟导入，非 Windows 环境不会在 import 包时失败。
        # 返回 int 句柄列表，后续由 get_title/get_class_name 读取摘要。
        if sys.platform != "win32":
            return []
        import ctypes

        user32 = ctypes.windll.user32
        handles: list[int] = []
        enum_proc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

        def callback(hwnd, _lparam):
            if user32.IsWindowVisible(hwnd):
                handles.append(int(hwnd))
            return True

        user32.EnumWindows(enum_proc(callback), 0)
        return handles

    def enum_child_windows(self, handle: int) -> list[int]:
        """枚举指定窗口的子窗口句柄。"""

        # 子窗口树用于统计 Qt 子窗口数量和 WebView Pane 摘要。
        # 这里仍然只读窗口结构，不触发任何前台操作。
        # 如果平台不是 Windows，直接返回空列表。
        if sys.platform != "win32":
            return []
        import ctypes

        user32 = ctypes.windll.user32
        handles: list[int] = []
        enum_proc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

        def callback(hwnd, _lparam):
            handles.append(int(hwnd))
            return True

        user32.EnumChildWindows(handle, enum_proc(callback), 0)
        return handles

    def get_title(self, handle: int) -> str:
        """读取窗口标题。"""

        # 标题用于识别“京麦”和“新增商品”等页面状态。
        # 读取失败时返回空字符串，调用方据此 halt 或提示人工处理。
        # 不抛出底层 Win32 错误，避免单个异常窗口中断整次枚举。
        if sys.platform != "win32":
            return ""
        import ctypes

        user32 = ctypes.windll.user32
        length = user32.GetWindowTextLengthW(handle)
        buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(handle, buffer, length + 1)
        return buffer.value

    def get_class_name(self, handle: int) -> str:
        """读取窗口类名。"""

        # 类名是 F14 的核心证据，必须能识别 Qt51511QWindowIcon。
        # 缓冲区 256 对普通 Win32 类名足够，过长时 Win32 会截断。
        # 读取失败返回空字符串，避免影响其他窗口枚举。
        if sys.platform != "win32":
            return ""
        import ctypes

        user32 = ctypes.windll.user32
        buffer = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(handle, buffer, 256)
        return buffer.value

    def focus_window(self, handle: int) -> bool:
        """把窗口置到前台。"""

        # 聚焦属于真实桌面动作，只有上层显式调用 focus_window 时才会执行。
        # 这里不点击窗口内部控件，也不发送键盘输入。
        # SetForegroundWindow 返回非零表示请求成功。
        if sys.platform != "win32":
            return False
        import ctypes

        return bool(ctypes.windll.user32.SetForegroundWindow(handle))

    def get_window_rect(self, handle: int) -> tuple[int, int, int, int] | None:
        """读取窗口屏幕矩形。"""

        # F17 截图证据需要知道窗口边界，不能只记录一个预期路径。
        # 非 Windows 环境直接返回 None，保持跨平台测试安全。
        # Win32 失败时也返回 None，由 screenshot_window 给出明确错误。
        if sys.platform != "win32":
            return None
        import ctypes
        from ctypes import wintypes

        rect = wintypes.RECT()
        ok = ctypes.windll.user32.GetWindowRect(handle, ctypes.byref(rect))
        if not ok:
            return None
        return (int(rect.left), int(rect.top), int(rect.right), int(rect.bottom))

    def screenshot_window(self, handle: int, output_path: Path) -> str:
        """截取指定窗口区域并保存为图片。"""

        # 这是 F17 真实截图证据的底层实现，只在上层显式调用 screenshot() 时触发。
        # 使用 Pillow ImageGrab 按窗口矩形截图，不发送点击、键盘或其它写操作。
        # 如果缺少 Pillow 或窗口矩形不可用，直接抛错，让 halt evidence 记录失败原因。
        rect = self.get_window_rect(handle)
        if rect is None:
            raise RuntimeError("无法读取窗口矩形，不能采集截图")
        try:
            from PIL import ImageGrab
        except ImportError as exc:
            raise RuntimeError("缺少 Pillow，不能采集窗口截图") from exc
        output_path.parent.mkdir(parents=True, exist_ok=True)
        image = ImageGrab.grab(bbox=rect)
        image.save(output_path)
        return str(output_path)


class Win32WindowInspectorBackend:
    """基于 Win32 的京麦窗口事实枚举 backend。"""

    def __init__(self, api: Any | None = None, title_keywords: tuple[str, ...] = ("京麦", "Jingmai"), target_class: str = "Qt51511QWindowIcon"):
        """初始化 Win32 窗口检测 backend。"""

        # api 可注入 fake，单元测试不依赖真实桌面。
        # title_keywords 允许中文京麦和英文兼容命名。
        # target_class 来自设计文档，是判断 Qt5 主壳的关键事实。
        self.api = api or Win32ApiAdapter()
        self.title_keywords = title_keywords
        self.target_class = target_class
        self._last_handle: int | None = None

    async def inspect_jingmai(self) -> JingmaiWindowFacts:
        """枚举桌面并返回京麦窗口技术事实。"""

        # 先枚举顶层窗口，再优先选择类名命中 Qt51511QWindowIcon 的窗口。
        # 如果类名未命中，则退回到标题关键字命中，便于未登录或标题变化时保留证据。
        # 子窗口摘要只保留计数和 Pane 列表，不保存完整窗口树。
        top_windows = [self._window_info(handle) for handle in self.api.enum_windows()]
        candidates = [window for window in top_windows if self._is_jingmai_candidate(window)]
        if not candidates:
            self._last_handle = None
            return JingmaiWindowFacts(found=False)
        main = self._select_main_window(candidates)
        self._last_handle = main.handle
        child_infos = [self._window_info(handle) for handle in self.api.enum_child_windows(main.handle or 0)]
        panes = [child for child in child_infos if self._is_webview_pane(child)]
        return JingmaiWindowFacts(
            found=True,
            main_title=main.title,
            main_class_name=main.class_name,
            qt_child_count=sum(1 for child in child_infos if child.class_name.lower().startswith("qt")),
            webview_pane_count=len(panes),
            html_edit_count=sum(1 for child in child_infos if self._is_html_control(child, "edit")),
            html_combobox_count=sum(1 for child in child_infos if self._is_html_control(child, "combobox")),
            html_button_count=sum(1 for child in child_infos if self._is_html_control(child, "button")),
            panes=panes[:10],
        )

    async def focus_window(self, title_keyword: str) -> bool:
        """按标题关键字或最近枚举结果聚焦京麦窗口。"""

        # 优先复用最近一次 inspect_jingmai 得到的句柄。
        # 如果没有最近句柄，则重新枚举并按 title_keyword 搜索。
        # 该方法只做前台聚焦，不执行菜单点击或表单输入。
        handle = self._last_handle
        if handle is None:
            for candidate in (self._window_info(item) for item in self.api.enum_windows()):
                if title_keyword in candidate.title or self._is_jingmai_candidate(candidate):
                    handle = candidate.handle
                    break
        if handle is None:
            return False
        return bool(self.api.focus_window(handle))

    async def screenshot(self, output_path: Path) -> Path:
        """返回窗口截图路径占位。"""

        # 当前 Win32 backend 只实现窗口事实枚举，不内置截图保存。
        # 如果注入 api 提供 screenshot_window，就委托它写真实图片。
        # 否则返回目标路径，让上层 halt 证据仍能记录预期路径。
        if self._last_handle is not None and hasattr(self.api, "screenshot_window"):
            return Path(self.api.screenshot_window(self._last_handle, output_path))
        return output_path

    def _window_info(self, handle: int) -> WindowInfo:
        """把 Win32 句柄转换为窗口摘要。"""

        # 所有底层 API 读取都集中在这里，便于 fake api 测试。
        # children_count 只用于轻量摘要，不递归展开完整窗口树。
        # handle 保留 int，方便后续聚焦或截图。
        return WindowInfo(
            handle=handle,
            title=str(self.api.get_title(handle) or ""),
            class_name=str(self.api.get_class_name(handle) or ""),
            children_count=len(self.api.enum_child_windows(handle)),
        )

    def _is_jingmai_candidate(self, window: WindowInfo) -> bool:
        """判断窗口是否可能是京麦主窗口。"""

        # 类名命中 Qt51511QWindowIcon 是最高可信证据。
        # 标题命中京麦/Jingmai 是兼容兜底。
        # 二者都不满足时不纳入候选。
        return window.class_name.lower() == self.target_class.lower() or any(keyword in window.title for keyword in self.title_keywords)

    def _select_main_window(self, candidates: list[WindowInfo]) -> WindowInfo:
        """从候选窗口中选择主窗口。"""

        # 优先选择类名精确命中的 Qt 主壳。
        # 没有精确命中时选择第一个标题候选，保留现场证据给人工判断。
        # 返回 WindowInfo 而不是 handle，避免重复读取标题/类名。
        for candidate in candidates:
            if candidate.class_name.lower() == self.target_class.lower():
                return candidate
        return candidates[0]

    def _is_webview_pane(self, window: WindowInfo) -> bool:
        """判断子窗口是否属于 WebView/Chromium 区域。"""

        # 京麦 QtWebEngine 会出现 Chrome/Cef/RenderWidget 类名。
        # 这些类名证明是 WebView 区域，但不代表 DOM 可控。
        # 只把摘要写入证据，不直接生成可点击 locator。
        class_name = window.class_name.lower()
        return "chrome" in class_name or "cef" in class_name or "renderwidget" in class_name

    def _is_html_control(self, window: WindowInfo, control_type: str) -> bool:
        """统计疑似 HTML 控件暴露数量。"""

        # F14 要确认 Edit/ComboBox/Button 对 UIA 不可达。
        # Win32 类名里直接出现这些词时计数；真实 UIA backend 后续可覆盖得更准。
        # 当前实现偏保守，只作为窗口事实摘要。
        text = f"{window.class_name} {window.control_type}".lower()
        return control_type.lower() in text


class Win32DesktopBackend:
    """基于 Win32/UFO API 的桌面命令执行 backend。"""

    def __init__(self, api: Any, allow_write: bool = False):
        """初始化桌面执行 backend。"""

        # api 由外部注入，可以是真实 UFO/Win32 包装，也可以是测试 fake。
        # allow_write 默认 False，避免构造 backend 后误执行真实点击或输入。
        # 所有命令到达这里前仍必须先通过 DesktopAgent 的 SafetyPolicy。
        self.api = api
        self.allow_write = allow_write
        self.executed: list[Command] = []

    async def execute(self, command: Command) -> AgentResult:
        """执行已经通过安全策略的桌面命令。"""

        # read/navigate 这类只读或焦点类命令可以在 observe-only 下执行。
        # click/fill/submit 属于真实写操作，必须 allow_write=True。
        # 返回 AgentResult，保持和 RecordingDesktopBackend 协议一致。
        self.executed.append(command)
        if command.action in {"click", "fill", "submit", "upload"} and not self.allow_write:
            return AgentResult(ok=False, message="真实桌面写操作未启用 allow_write", data={"action": command.action, "blocked": True})
        if command.action == "click":
            return self._click(command)
        if command.action == "fill":
            return self._fill(command)
        if command.action == "submit":
            return self._click(command)
        if command.action == "upload":
            return self._upload(command)
        if command.action in {"read", "navigate"}:
            return AgentResult(ok=True, message="desktop command observed", data={"action": command.action})
        return AgentResult(ok=False, message=f"不支持的桌面命令: {command.action}", data={"action": command.action})

    def _click(self, command: Command) -> AgentResult:
        """执行点击命令。"""

        # 优先使用 metadata.point；没有 point 时尝试使用 metadata.rect 的中心点。
        # api 必须显式提供 click(x, y)，否则返回失败，避免假装成功。
        # submit 保存草稿最终也会走这个点击路径。
        point = self._point_from_metadata(command.metadata)
        if point is None:
            return AgentResult(ok=False, message="缺少点击坐标证据", data={"target": command.target})
        if not hasattr(self.api, "click"):
            return AgentResult(ok=False, message="底层 API 不支持 click", data={"target": command.target, "point": point})
        self.api.click(*point)
        return AgentResult(ok=True, message="真实点击已执行", data={"target": command.target, "point": point})

    def _fill(self, command: Command) -> AgentResult:
        """执行填充命令。"""

        # WebView 填写应先点击坐标，再通过剪贴板/键盘写入。
        # api 需要提供 set_clipboard_text 和 hotkey 或 paste_text。
        # 缺少能力时直接失败，不把部分操作当成功。
        click_result = self._click(command)
        if not click_result.ok:
            return click_result
        if hasattr(self.api, "paste_text"):
            self.api.paste_text(str(command.value))
        elif hasattr(self.api, "set_clipboard_text") and hasattr(self.api, "hotkey"):
            self.api.set_clipboard_text(str(command.value))
            self.api.hotkey("ctrl", "a")
            self.api.hotkey("ctrl", "v")
        else:
            return AgentResult(ok=False, message="底层 API 不支持剪贴板填充", data={"target": command.target})
        return AgentResult(ok=True, message="真实填充已执行", data={"target": command.target, "value_length": len(str(command.value))})

    def _upload(self, command: Command) -> AgentResult:
        """执行文件上传命令。"""

        # 原生文件对话框由 UFO/Win32 api 负责。
        # api 必须提供 choose_file(path)，否则返回失败。
        # 上传路径保存在 command.value 中，不在日志里展开敏感目录之外的内容。
        if not hasattr(self.api, "choose_file"):
            return AgentResult(ok=False, message="底层 API 不支持 choose_file", data={"target": command.target})
        self.api.choose_file(str(command.value))
        return AgentResult(ok=True, message="真实文件选择已执行", data={"target": command.target})

    def _point_from_metadata(self, metadata: dict[str, Any]) -> tuple[int, int] | None:
        """从命令元数据中解析点击坐标。"""

        # point 支持 [x, y] 或 (x, y)。
        # rect 支持 {x,y,width,height}，自动取中心点。
        # 坐标不存在时返回 None，让调用方 halt 并记录缺失证据。
        point = metadata.get("point")
        if isinstance(point, (list, tuple)) and len(point) == 2:
            return (int(point[0]), int(point[1]))
        rect = metadata.get("rect")
        if isinstance(rect, dict):
            return (int(rect["x"]) + int(rect["width"]) // 2, int(rect["y"]) + int(rect["height"]) // 2)
        return None


class StaticWindowInspectorBackend:
    """用于测试和 dry-run 的静态窗口 backend。"""

    def __init__(self, facts: JingmaiWindowFacts | None = None):
        """保存静态窗口事实。"""

        # 默认事实刻意表示未找到真实窗口，避免 dry-run 假装已连接京麦。
        # 测试可注入 Qt51511QWindowIcon 等事实来验证 F14 判断。
        # 该 backend 不调用任何系统 API。
        self.facts = facts or JingmaiWindowFacts(found=False)
        self.focused_keywords: list[str] = []

    async def inspect_jingmai(self) -> JingmaiWindowFacts:
        """返回静态京麦窗口事实。"""

        # 返回构造时传入的事实，保证测试确定性。
        # 不枚举桌面窗口，不依赖当前用户是否打开京麦。
        # 上层必须根据 found/is_expected_qt_shell 决定是否继续。
        return self.facts

    async def focus_window(self, title_keyword: str) -> bool:
        """记录聚焦请求并返回是否可聚焦。"""

        # 只记录关键字，方便测试验证 OPEN_PAGE 前置动作。
        # found 为 False 时返回 False，模拟窗口不存在。
        # 真实 backend 后续会调用 UFO/Win32 聚焦能力。
        self.focused_keywords.append(title_keyword)
        return self.facts.found

    async def screenshot(self, output_path: Path) -> Path:
        """返回 dry-run 截图路径。"""

        # dry-run 不创建真实截图文件。
        # 返回调用方给定路径，作为证据结构占位。
        # 真实 backend 应覆盖该方法并写入实际图片。
        return output_path


class UfoImportBackend(StaticWindowInspectorBackend):
    """从本机 UFO v1 包加载底层能力的占位适配器。"""

    def __init__(self, ufo_root: Path = Path("E:/PY/UFO/ufo")):
        """记录 UFO v1 源码路径。"""

        # 这里不继承 v1 ReAct agent，只检查底层包是否存在。
        # 真正的窗口枚举/截图方法后续在该类中逐步接入。
        # 路径不存在时保持 found=False，调用方会 halt 等待人工处理。
        self.ufo_root = ufo_root
        super().__init__(facts=JingmaiWindowFacts(found=ufo_root.exists()))

    def source_files(self) -> dict[str, str]:
        """返回 v2 计划适配的 UFO v1 底层文件。"""

        # 这些路径来自设计文档，不包含 v1 自主决策 agent。
        # 只暴露文件映射，便于审计当前适配范围。
        # 后续复制/适配时应保留原许可和来源注释。
        return {
            "action_execution": str(self.ufo_root / "automator" / "action_execution.py"),
            "controller": str(self.ufo_root / "automator" / "ui_control" / "controller.py"),
            "inspector": str(self.ufo_root / "automator" / "ui_control" / "inspector.py"),
            "screenshot": str(self.ufo_root / "automator" / "ui_control" / "screenshot.py"),
            "ui_tree": str(self.ufo_root / "automator" / "ui_control" / "ui_tree.py"),
        }
