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
        - 先按京麦已知窗口签名（类名/标题模式）匹配
        - 再按用户传入的关键词加权
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
        """为顶层窗口计算京麦匹配分数。

        两阶段评分：
        1. 先计算固有签名分（类名/标题模式）
        2. 若有固有签名，再加关键词加分和可见性加分
        否则返回 0，避免纯关键词误匹配（如 IDE 标题含 "jingmai"）。
        """

        title = (window.title or "").lower()
        class_name = (window.class_name or "").lower()

        # -- 阶段一：固有签名评分 --
        intrinsic = 0
        if class_name == "jmmainframebase":
            intrinsic += 200
        elif "jmmainframe" in class_name:
            intrinsic += 150

        if title.startswith("jd_"):
            intrinsic += 120
        if "咚咚融合工作台" in title:
            intrinsic += 80
        if "京东-京麦" in title or "京麦" in title:
            intrinsic += 100

        # -- 阶段二：关键词加分（仅当有固有签名时才生效） --
        keyword_bonus = 0
        if intrinsic > 0:
            for keyword in keywords:
                normalized = keyword.strip().lower()
                if not normalized:
                    continue
                if WindowManager._keyword_boundary_match(normalized, title, class_name):
                    keyword_bonus += 60
                    break

        # 可见性加分：仅当有固有签名或关键词命中时才生效
        visibility_bonus = 0
        if intrinsic > 0 or keyword_bonus > 0:
            visibility_bonus = 40 if window.visible else -40

        if intrinsic == 0 and keyword_bonus == 0:
            return 0

        return intrinsic + keyword_bonus + visibility_bonus

    @staticmethod
    def _keyword_boundary_match(keyword: str, title: str, class_name: str) -> bool:
        """检查关键词是否以独立词形式出现在标题或类名中。

        使用词边界匹配，防止 "jingmai" 误匹配 "jingmai-product-publish-v2"。
        """
        import re
        pattern = re.compile(rf"(?<![a-zA-Z0-9_-]){re.escape(keyword)}(?![a-zA-Z0-9_-])")
        return bool(pattern.search(title) or pattern.search(class_name))

    def attach_jingmai_window(self) -> WindowInfo:
        """接管京麦窗口并返回窗口信息。"""

        window = self.find_jingmai_window()
        if window is None:
            raise ValueError("未找到京麦桌面窗口")
        if not self.adapter.activate_window(window.handle):
            raise RuntimeError(f"京麦窗口激活失败: {window.handle}")
        return window
