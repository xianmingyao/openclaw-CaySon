"""商品上架前的数据准备服务。"""

from __future__ import annotations

import json
from decimal import Decimal

from jingmai_publish.domain.prepared_product import PreparedImageData, PreparedProductData
from jingmai_publish.services.excel_ingest import ExcelIngestService


class ProductDataPrepareService:
    """融合 Excel、京东快照与图片本地化记录，生成标准化上架对象。"""

    def __init__(self, upload_job_repo, snapshot_repo, runtime_log_repo, image_repo=None) -> None:
        self.upload_job_repo = upload_job_repo
        self.snapshot_repo = snapshot_repo
        self.runtime_log_repo = runtime_log_repo
        self.image_repo = image_repo

    @staticmethod
    def _pick_value(*values):
        for value in values:
            if value is not None and value != "":
                return value
        return None

    def prepare_for_job_item(self, job_item_id: int) -> PreparedProductData:
        """生成单条商品行的上架标准数据。"""

        item = self.upload_job_repo.get_job_item(job_item_id)
        if item is None:
            raise ValueError(f"未找到导入商品行: {job_item_id}")

        snapshot = self.snapshot_repo.get_latest_by_job_item_id(job_item_id)
        snapshot_attributes = self._load_snapshot_attributes(snapshot)
        source_payload = self._load_source_payload(snapshot)

        product_name = self._pick_value(getattr(item, "product_name", None), getattr(snapshot, "title", None))
        brand = self._pick_value(
            getattr(item, "brand", None),
            getattr(snapshot, "brand", None),
            snapshot_attributes.get("brand_name"),
        )
        model = self._pick_value(
            getattr(item, "model", None),
            getattr(snapshot, "model", None),
            source_payload.get("model"),
            "",
        )
        product_summary = self._pick_value(
            getattr(item, "product_summary", None),
            getattr(snapshot, "detail_text", None),
            product_name,
        )

        jd_sale_price = self._pick_value(getattr(item, "jd_sale_price", None), getattr(snapshot, "price", None))
        if jd_sale_price is None:
            raise ValueError(f"商品行 {job_item_id} 缺少京东价，无法准备上架数据")
        jd_sale_price = self._to_decimal(jd_sale_price)
        purchase_price = self._to_decimal(
            self._pick_value(
                getattr(item, "purchase_price", None),
                ExcelIngestService.calculate_purchase_price(jd_sale_price),
            )
        )
        market_price = self._to_decimal(
            self._pick_value(
                getattr(item, "market_price", None),
                ExcelIngestService.calculate_market_price(jd_sale_price),
            )
        )

        if not brand:
            raise ValueError(f"商品行 {job_item_id} 缺少品牌，无法准备上架数据")
        if not product_name:
            raise ValueError(f"商品行 {job_item_id} 缺少商品标题，无法准备上架数据")

        images = self._build_images(job_item_id, source_payload)
        prepared = PreparedProductData(
            product_name=str(product_name),
            brand=str(brand),
            model=str(model or ""),
            jd_sale_price=jd_sale_price,
            purchase_price=purchase_price,
            market_price=market_price,
            unit_name=str(
                self._pick_value(
                    getattr(item, "unit_name", None),
                    snapshot_attributes.get("unit_name"),
                    "个",
                )
            ),
            product_summary=str(product_summary) if product_summary else None,
            jd_item_id=getattr(snapshot, "jd_item_id", None),
            jd_item_url=getattr(item, "jd_item_url", None),
            category_path=self._pick_value(
                snapshot_attributes.get("category_path"),
                source_payload.get("category_path"),
            ),
            detail_html=getattr(snapshot, "detail_html", None),
            qualification_pdf_path=getattr(item, "qualification_pdf_path", None),
            remark=getattr(item, "remark", None),
            item_type=getattr(item, "item_type", None),
            length_mm=self._resolve_decimal_field(item, "length_mm", snapshot_attributes),
            width_mm=self._resolve_decimal_field(item, "width_mm", snapshot_attributes),
            height_mm=self._resolve_decimal_field(item, "height_mm", snapshot_attributes),
            weight_kg=self._resolve_decimal_field(item, "weight_kg", snapshot_attributes),
            images=images,
        )
        self.runtime_log_repo.append_log(
            session_id=f"prepare-{job_item_id}",
            log_type="process",
            job_id=getattr(item, "job_id", None),
            job_item_id=item.id,
            message=f"已生成商品行 {job_item_id} 的标准化上架数据，图片数={len(images)}",
        )
        return prepared

    @staticmethod
    def _load_snapshot_attributes(snapshot) -> dict[str, object]:
        if snapshot is None or getattr(snapshot, "attributes_json", None) is None:
            return {}
        if isinstance(snapshot.attributes_json, dict):
            return snapshot.attributes_json
        return {}

    @staticmethod
    def _load_source_payload(snapshot) -> dict[str, object]:
        if snapshot is None:
            return {}
        raw_payload = getattr(snapshot, "source_payload_json", None)
        if not raw_payload:
            return {}
        if isinstance(raw_payload, dict):
            return raw_payload
        try:
            payload = json.loads(raw_payload)
        except (TypeError, json.JSONDecodeError):
            return {}
        return payload if isinstance(payload, dict) else {}

    def _build_images(self, job_item_id: int, source_payload: dict[str, object]) -> list[PreparedImageData]:
        prepared_images: list[PreparedImageData] = []

        if self.image_repo is not None:
            for record in self.image_repo.list_images_by_job_item(job_item_id):
                prepared_images.append(
                    PreparedImageData(
                        role=str(getattr(record, "image_role", "detail")),
                        source_url=str(getattr(record, "image_source_url", "")),
                        local_path=getattr(record, "image_local_path", None),
                        image_format=getattr(record, "image_format", None),
                        width=getattr(record, "image_width", None),
                        height=getattr(record, "image_height", None),
                        is_valid=bool(getattr(record, "is_valid", False)),
                    )
                )

        if prepared_images:
            return prepared_images

        payload_images = source_payload.get("images", [])
        if not isinstance(payload_images, list):
            return prepared_images

        for index, image_url in enumerate(payload_images):
            if not image_url:
                continue
            prepared_images.append(
                PreparedImageData(
                    role="main" if index == 0 else "detail",
                    source_url=str(image_url),
                )
            )
        return prepared_images

    def _resolve_decimal_field(self, item, field_name: str, snapshot_attributes: dict[str, object]) -> Decimal | None:
        preferred = getattr(item, field_name, None)
        if preferred is not None:
            return self._to_decimal(preferred)
        fallback = snapshot_attributes.get(field_name)
        if fallback in (None, ""):
            return None
        return self._to_decimal(fallback)

    @staticmethod
    def _to_decimal(value) -> Decimal:
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))
