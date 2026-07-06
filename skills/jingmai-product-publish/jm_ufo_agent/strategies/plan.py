"""确定性字段计划策略。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FieldPlan:
    """单个字段填充计划。"""

    field_name: str
    value: Any
    required: bool = True
    evidence_key: str | None = None


class DeterministicPlanStrategy:
    """根据商品数据生成稳定字段计划。"""

    default_fields = (
        "title",
        "category",
        "brand",
        "sku",
        "jd_price",
        "purchase_price",
        "market_price",
        "main_image",
        "sub_images",
        "description",
        "weight",
        "stock",
    )

    def build_field_plan(self, product: dict[str, Any], verified_fields: set[str] | None = None) -> list[FieldPlan]:
        """生成待填字段列表。

        # verified_fields 是字段级断点恢复结果，已经验证过的字段直接跳过。
        # 字段顺序固定，保证崩溃恢复和重复执行的行为一致。
        # 缺失字段仍进入计划但标记 value=""，后续 VerifyStrategy 决定是否阻断。
        """

        verified = verified_fields or set()
        plans: list[FieldPlan] = []
        for field_name in self.default_fields:
            if field_name in verified:
                continue
            plans.append(FieldPlan(field_name=field_name, value=product.get(field_name, ""), evidence_key=f"{field_name}_evidence"))
        return plans
