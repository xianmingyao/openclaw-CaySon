"""京麦窗口管理器。"""

from __future__ import annotations

from jingmai_publish.desktop.adapter import DesktopAutomationAdapter, WindowInfo


class WindowManager:
    """负责定位和接管京麦桌面窗口。"""

    def __init__(self, adapter: DesktopAutomationAdapter) -> None:
        """注入桌面自动化适配器。"""

        self.adapter = adapter

    def find_jingmai_window(self) -> WindowInfo | None:
        """查找京麦窗口。

        识别策略：
        - 先按用户传入的窗口关键词匹配
        - 再按京麦已知窗口签名加分
        - 优先返回可见且分数最高的窗口
        """

        keywords = getattr(getattr(self.adapter, "tuning", None), "window_keywords", ["京麦", "Jingmai"])
        best_window: WindowInfo | None = None
        best_score = 0

        for window in self.adapter.list_windows():
            score = self._score_window(window, keywords)
            if score > best_score:
                best_score = score
                best_window = window

        return best_window

    @staticmethod
    def _score_window(window: WindowInfo, keywords: list[str]) -> int:
        """为顶层窗口计算“像不像京麦”的分数。"""

        title = (window.title or "").lower()
        class_name = (window.class_name or "").lower()
        haystack = f"{title} {class_name}"
        score = 0

        # 优先匹配用户显式给出的关键词。
        for keyword in keywords:
            normalized = keyword.strip().lower()
            if not normalized:
                continue
            if normalized in haystack:
                score += 60

        # 京麦桌面的真实窗口签名。
        if class_name == "jmmainframebase":
            score += 200
        elif "jmmainframe" in class_name:
            score += 150

        if title.startswith("jd_"):
            score += 120
        if "咚咚融合工作台" in title:
            score += 80
        if "京东-京麦" in title or "京麦" in title:
            score += 100

        # 可见窗口优先，避免误选隐藏 IPC/辅助窗口。
        if window.visible:
            score += 40
        else:
            score -= 40

        return score

    def attach_jingmai_window(self) -> WindowInfo:
        """接管京麦窗口并返回窗口信息。"""

        window = self.find_jingmai_window()
        if window is None:
            raise ValueError("未找到京麦桌面窗口")
        if not self.adapter.activate_window(window.handle):
            raise RuntimeError(f"京麦窗口激活失败: {window.handle}")
        return window
