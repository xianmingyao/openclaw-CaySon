"""价格计算工具。"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP


def quantize_money(value: Decimal | int | float | str) -> Decimal:
    """把输入金额规整为两位小数。

    # 京麦价格字段最终都需要稳定的两位小数。
    # 用 Decimal(str(value)) 避免 float 二进制精度污染。
    # ROUND_HALF_UP 符合常见财务四舍五入习惯。
    """

    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_sale_price(purchase_price: Decimal | int | float | str, market_price: Decimal | int | float | str) -> Decimal:
    """计算保守销售价。

    # 默认取采购价的 1.2 倍作为候选价。
    # 如果候选价超过市场价的 1.1 倍，就收敛到允许上限。
    # 返回值始终是两位小数，便于后续 SafetyPolicy 再做硬校验。
    """

    purchase = quantize_money(purchase_price)
    market = quantize_money(market_price)
    candidate = purchase * Decimal("1.2")
    upper = market * Decimal("1.1")
    return quantize_money(min(candidate, upper))
