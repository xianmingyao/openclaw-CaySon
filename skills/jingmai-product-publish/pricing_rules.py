from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any, Optional


def _to_decimal(value: Any) -> Optional[Decimal]:
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, ValueError, TypeError):
        return None


def _quantize_money(value: Decimal) -> float:
    return float(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def derive_market_price(jd_price: Any) -> Optional[float]:
    price = _to_decimal(jd_price)
    if price is None:
        return None
    if price <= 0:
        return _quantize_money(price)
    return _quantize_money(price / Decimal("0.85"))


def derive_purchase_price(jd_price: Any) -> Optional[float]:
    price = _to_decimal(jd_price)
    if price is None:
        return None
    return _quantize_money(price * Decimal("0.95"))
