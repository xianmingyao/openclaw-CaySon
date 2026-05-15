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
    width: int | None = None
    height: int | None = None
    is_valid: bool | None = None


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
    jd_item_id: str | None = None
    jd_item_url: str | None = None
    category_path: str | None = None
    detail_html: str | None = None
    qualification_pdf_path: str | None = None
    remark: str | None = None
    item_type: str | None = None
    length_mm: Decimal | None = None
    width_mm: Decimal | None = None
    height_mm: Decimal | None = None
    weight_kg: Decimal | None = None
    images: list[PreparedImageData] = field(default_factory=list)
