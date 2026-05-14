"""上架前标准化商品领域模型。"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(slots=True)
class PreparedImageData:
    """标准化图片数据。"""

    role: str
    source_url: str
    local_path: str | None = None
    image_format: str | None = None


@dataclass(slots=True)
class PreparedProductData:
    """标准化商品上架数据。"""

    product_name: str
    brand: str
    model: str
    jd_sale_price: Decimal
    purchase_price: Decimal
    market_price: Decimal
    unit_name: str | None = None
    product_summary: str | None = None
    images: list[PreparedImageData] = field(default_factory=list)
