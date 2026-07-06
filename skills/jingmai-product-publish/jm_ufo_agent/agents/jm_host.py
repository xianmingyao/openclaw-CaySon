"""京麦主窗口 Agent。"""

from __future__ import annotations

from dataclasses import dataclass

from jm_ufo_agent.agents.base import AgentResult
from jm_ufo_agent.agents.desktop import DesktopAgent
from jm_ufo_agent.backends.ufo_adapter import JingmaiWindowFacts, StaticWindowInspectorBackend, WindowInspectorBackend


@dataclass(frozen=True)
class LoginCheckResult:
    """京麦登录态检测结果。"""

    logged_in: bool
    needs_human_login: bool
    reason: str


class JmHostAgent(DesktopAgent):
    """负责京麦主窗口状态检查。"""

    def __init__(self, *args, window_backend: WindowInspectorBackend | None = None, expected_window_title: str = "新增商品", **kwargs):
        """初始化京麦主窗口 Agent。"""

        # 默认名称固定，方便日志和测试识别。
        # window_backend 默认是静态 dry-run，不枚举真实桌面窗口。
        # expected_window_title 来自设计文档 F05，可由测试或不同页面配置覆盖。
        kwargs.setdefault("name", "jm_host")
        super().__init__(*args, **kwargs)
        self.window_backend = window_backend or StaticWindowInspectorBackend()
        self.expected_window_title = expected_window_title

    async def inspect_window_facts(self) -> AgentResult:
        """返回京麦窗口技术事实摘要。"""

        # F14 要求记录 Qt51511QWindowIcon、Qt 子窗口数量、WebView Pane 摘要。
        # 真实 backend 后续负责枚举窗口树；这里统一转换为 AgentResult。
        # 如果主壳不符合 Qt5 事实，ok=False，阻止后续误把京麦当普通浏览器。
        facts = await self.window_backend.inspect_jingmai()
        return AgentResult(
            ok=facts.is_expected_qt_shell(),
            message="京麦窗口事实已检测" if facts.found else "未找到京麦窗口",
            data={
                "found": facts.found,
                "main_title": facts.main_title,
                "main_class_name": facts.main_class_name,
                "qt_child_count": facts.qt_child_count,
                **facts.webview_summary(),
            },
        )

    async def check_login(self) -> AgentResult:
        """检测京麦是否已经登录。"""

        # 当前登录态先基于窗口事实和标题关键字判断。
        # 未找到窗口或标题含登录提示时，返回 needs_human_login=True。
        # 后续真实实现可加入 OCR/页面签名检测，但接口保持不变。
        facts = await self.window_backend.inspect_jingmai()
        result = self._login_from_facts(facts)
        return AgentResult(ok=result.logged_in, message=result.reason, data=result.__dict__)

    async def open_add_product_page(self) -> AgentResult:
        """准备打开新增商品页并验证目标窗口标题。"""

        # 真实点击导航前必须先聚焦京麦窗口。
        # 当前方法只调用 backend 的 focus_window，不直接点击真实菜单。
        # 标题命中 expected_window_title 才认为 F05 通过。
        focused = await self.window_backend.focus_window("京麦")
        facts = await self.window_backend.inspect_jingmai()
        title_hit = self.expected_window_title in facts.main_title
        return AgentResult(
            ok=focused and title_hit,
            message="新增商品页标题已命中" if title_hit else "新增商品页标题未命中",
            data={
                "focused": focused,
                "expected_window_title": self.expected_window_title,
                "actual_window_title": facts.main_title,
                "title_hit": title_hit,
            },
        )

    def _login_from_facts(self, facts: JingmaiWindowFacts) -> LoginCheckResult:
        """根据窗口事实推断登录态。"""

        # 没找到京麦窗口时，不能继续自动化，需要人工打开或登录。
        # 标题里出现登录、扫码等词时，视为需要人工登录。
        # 其它情况只表示窗口层面看起来已进入主界面，后续还应由页面签名再校验。
        if not facts.found:
            return LoginCheckResult(logged_in=False, needs_human_login=True, reason="未找到京麦窗口，请人工打开并登录")
        title = facts.main_title.lower()
        if any(keyword in title for keyword in ("登录", "扫码", "login")):
            return LoginCheckResult(logged_in=False, needs_human_login=True, reason="京麦显示登录相关标题，需要人工登录")
        return LoginCheckResult(logged_in=True, needs_human_login=False, reason="京麦窗口已存在，登录态需页面签名继续确认")
