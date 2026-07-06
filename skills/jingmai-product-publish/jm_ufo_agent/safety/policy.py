"""硬安全策略。

SafetyPolicy 是 v2 的最后一道本地屏障。任何 DesktopAgent 在 click/fill/submit
之前都必须调用 `assert_allowed`，不能把“模型觉得安全”作为执行依据。
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from jm_ufo_agent.commands.base import Command


class SafetyViolation(RuntimeError):
    """安全策略拒绝执行时抛出的异常。"""


@dataclass(frozen=True)
class PriceBounds:
    """京麦价格允许区间。"""

    min_price: Decimal
    max_price: Decimal


class SafetyPolicy:
    """京麦自动化硬阻断策略。"""

    blocked_keywords = frozenset(
        {
            "发布",
            "发布商品",
            "立即发布",
            "删除",
            "删除商品",
            "下架",
            "remove",
            "delete",
            "publish",
            "submit_publish",
        }
    )
    draft_keywords = frozenset({"保存草稿", "存草稿", "save draft", "save_draft"})

    def assert_allowed(self, command: Command) -> None:
        """校验命令是否允许执行。

        # 第一步先阻断所有危险动作，不依赖页面位置或按钮样式。
        # 第二步允许“保存草稿”白名单继续向下走，符合设计文档红线。
        # 第三步检查价格元数据，防止模型或调用方绕过价格上下限。
        """

        text = command.normalized_text()
        if self._contains_blocked_keyword(text):
            raise SafetyViolation(f"禁止执行高风险动作: {command.label or command.action}")
        if command.action.lower() in {"price", "fill_price", "set_price"}:
            self.assert_price_allowed(command)

    def assert_price_allowed(self, command: Command) -> None:
        """校验价格写入是否在允许范围内。

        # purchase_price 和 market_price 来自商品数据或抓取结果。
        # 要写入的 price 可能在 value，也可能放在 metadata["price"]。
        # 任何一个必要值缺失都拒绝执行，避免在证据不足时继续推进。
        """

        price = self._decimal(command.value if command.value is not None else command.metadata.get("price"))
        purchase_price = self._decimal(command.metadata.get("purchase_price"))
        market_price = self._decimal(command.metadata.get("market_price"))
        if price is None or purchase_price is None or market_price is None:
            raise SafetyViolation("价格校验缺少必要证据")

        bounds = self.price_bounds(purchase_price=purchase_price, market_price=market_price)
        if price < bounds.min_price or price > bounds.max_price:
            raise SafetyViolation(f"价格 {price} 超出允许范围 {bounds.min_price} ~ {bounds.max_price}")

    def price_bounds(self, purchase_price: Decimal, market_price: Decimal) -> PriceBounds:
        """计算价格允许区间。"""

        # 下限来自采购价的 90%，防止低价误填。
        # 上限来自市场价的 110%，防止高价误填。
        # quantize 固定两位小数，便于错误信息和测试稳定。
        min_price = (purchase_price * Decimal("0.9")).quantize(Decimal("0.01"))
        max_price = (market_price * Decimal("1.1")).quantize(Decimal("0.01"))
        return PriceBounds(min_price=min_price, max_price=max_price)

    def _contains_blocked_keyword(self, text: str) -> bool:
        """判断命令文本是否包含硬阻断关键字。"""

        # 这里用包含匹配而不是完全匹配，因为按钮文本常带空格或后缀。
        # 关键字集合同时覆盖中文 UI 和英文内部 action。
        # 一旦命中任意关键词，就交给 assert_allowed 抛出统一异常。
        return any(keyword in text for keyword in self.blocked_keywords)

    def _decimal(self, value: object) -> Decimal | None:
        """把价格输入转换为 Decimal。"""

        # None 和空字符串都代表缺少证据。
        # 使用 str(value) 构造 Decimal，避免 float 精度直接进入价格判断。
        # 非法金额让 Decimal 抛错，调用方应把它当作失败证据处理。
        if value in (None, ""):
            return None
        return Decimal(str(value))
