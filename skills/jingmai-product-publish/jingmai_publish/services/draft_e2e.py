"""Excel 到京麦草稿箱的端到端编排服务。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from sqlalchemy.orm import Session

from jingmai_publish.desktop import UIATuningConfig
from jingmai_publish.services.desktop_verify import DesktopVerificationService
from jingmai_publish.services.import_pipeline import ImportPipelineService


@dataclass(slots=True)
class DraftE2EOptions:
    """草稿 E2E 运行参数。"""

    excel_path: str | Path
    item_index: int = 0
    store_id: str | None = None
    required_attr: str | None = None
    current: str | None = None
    factory_inventory: str | None = None
    main_image_path: str | None = None
    transparent_image_path: str | None = None
    detail_content: str | None = None
    detail_content_file: str | None = None
    rated_voltage: str | None = None
    cable_length: str | None = None
    sale_unit: str | None = None
    package_type: str = "普通商品"
    delivery_mark: str = "普通品"
    package_list: str | None = None
    warranty_period: str = "365"
    debug: bool = False


class DraftE2EOrchestrator:
    """把导入、数据准备和桌面草稿保存串成一个可复现入口。"""

    def __init__(
            self,
            session: Session,
            *,
            screenshot_dir: str,
            tuning: UIATuningConfig | None = None,
            desktop_service_factory: Callable[[str, UIATuningConfig | None], Any] | None = None,
    ) -> None:
        self.import_pipeline = ImportPipelineService(session)
        self.desktop_service = (
                desktop_service_factory
                or (lambda target_dir, target_tuning: DesktopVerificationService(target_dir, tuning=target_tuning))
        )(screenshot_dir, tuning)

    def run(self, options: DraftE2EOptions) -> dict[str, object]:
        """执行草稿 E2E。

        该入口故意不支持正式发布，只把页面推进到保存草稿成功。
        """

        pipeline_result = self.import_pipeline.run_from_local_excel_path(
            options.excel_path,
            mode="draft",
            store_id=options.store_id,
        )
        prepared_products = pipeline_result.get("prepared_products", [])
        if not isinstance(prepared_products, list) or not prepared_products:
            raise ValueError("导入链路没有产出可上架商品数据")
        if options.item_index < 0 or options.item_index >= len(prepared_products):
            raise ValueError(f"item_index 越界: {options.item_index}, 商品数={len(prepared_products)}")

        prepared = prepared_products[options.item_index]
        if not isinstance(prepared, dict):
            raise ValueError("prepared product payload must be a dict")

        runtime_payload = self._build_runtime_payload(prepared, options)
        desktop_steps = self._run_desktop_draft_steps(runtime_payload, debug=options.debug)
        success = bool(
            desktop_steps and desktop_steps[-1].get("success") and desktop_steps[-1].get("step") == "t8-save-draft")

        return {
            "success": success,
            "mode": "draft",
            "job_id": pipeline_result.get("job_id"),
            "session_id": pipeline_result.get("session_id"),
            "task_ids": pipeline_result.get("task_ids", []),
            "selected_item_index": options.item_index,
            "selected_prepared_product": prepared,
            "runtime_payload": runtime_payload,
            "desktop_steps": desktop_steps,
        }

    def _build_runtime_payload(self, prepared: dict[str, object], options: DraftE2EOptions) -> dict[str, object]:
        title = self._required_text(prepared, "product_name")
        model = str(prepared.get("model") or "")
        brand = self._required_text(prepared, "brand")
        weight = self._optional_decimal_text(prepared.get("weight_kg"))
        package_list = options.package_list or f"{title}*1"
        detail_content = self._resolve_detail_content(prepared, options)

        return {
            "title": title,
            "model": model,
            "brand": brand,
            "required_attribute": options.required_attr or model or title,
            "rated_voltage": options.rated_voltage,
            "cable_length": options.cable_length,
            "current": options.current,
            "weight": weight,
            "factory_inventory": options.factory_inventory,
            "sku_name": title,
            "short_title": title[:45],
            "market_price": self._required_decimal_text(prepared, "market_price"),
            "purchase_price": self._required_decimal_text(prepared, "purchase_price"),
            "jd_price": self._required_decimal_text(prepared, "jd_sale_price"),
            "length_mm": self._optional_decimal_text(prepared.get("length_mm")),
            "width_mm": self._optional_decimal_text(prepared.get("width_mm")),
            "height_mm": self._optional_decimal_text(prepared.get("height_mm")),
            "main_image_path": self._resolve_image_path(prepared, "main", options.main_image_path),
            "transparent_image_path": self._resolve_image_path(prepared, "transparent", options.transparent_image_path),
            "detail_content": detail_content,
            "sale_unit": options.sale_unit or str(prepared.get("unit_name") or "件"),
            "package_type": options.package_type,
            "delivery_mark": options.delivery_mark,
            "package_list": package_list,
            "warranty_period": options.warranty_period,
        }

    def _run_desktop_draft_steps(self, payload: dict[str, object], *, debug: bool) -> list[dict[str, object]]:
        steps: list[tuple[str, dict[str, object], bool]] = [
            (
                "t4",
                {
                    "title": payload["title"],
                    "model": payload["model"],
                    "required_attribute": payload["required_attribute"],
                    "brand": payload["brand"],
                },
                False,
            ),
            (
                "t5-required-fields",
                {
                    "market_price": payload["market_price"],
                    "purchase_price": payload["purchase_price"],
                    "jd_price": payload["jd_price"],
                    "current": payload["current"],
                    "weight": payload["weight"],
                    "length_mm": payload["length_mm"],
                    "width_mm": payload["width_mm"],
                    "height_mm": payload["height_mm"],
                    "factory_inventory": payload["factory_inventory"],
                },
                False,
            ),
        ]

        steps.extend(
            [
                ("t6-main-image", {"image_path": payload["main_image_path"]}, True),
                ("t6-transparent-image", {"transparent_image_path": payload["transparent_image_path"]}, False),
                ("t6-detail-editor", {"detail_content": payload["detail_content"]}, True),
                (
                    "t7",
                    {
                        "sale_unit": payload["sale_unit"],
                        "package_type": payload["package_type"],
                        "delivery_mark": payload["delivery_mark"],
                        "package_list": payload["package_list"],
                        "warranty_period": payload["warranty_period"],
                    },
                    True,
                ),
                ("t8-save-draft", {}, True),
            ]
        )

        results: list[dict[str, object]] = []
        for step_name, step_kwargs, required in steps:
            cleaned_kwargs = {key: value for key, value in step_kwargs.items() if value is not None}
            step_result = self.desktop_service.run(step=step_name, debug=debug, **cleaned_kwargs)
            success = self._extract_step_success(step_name, step_result)
            results.append(
                {
                    "step": step_name,
                    "success": success,
                    "required": required,
                    "result": step_result,
                }
            )
            if required and not success:
                break
        return results

    @staticmethod
    def _extract_step_success(step_name: str, result: dict[str, object]) -> bool:
        result_key = step_name.replace("-", "_")
        payload = result.get(result_key)
        if isinstance(payload, dict) and "success" in payload:
            return bool(payload["success"])
        session = result.get("session")
        if isinstance(session, dict) and session.get("halted"):
            return False
        return payload is not None

    @staticmethod
    def _required_text(prepared: dict[str, object], key: str) -> str:
        value = prepared.get(key)
        if value is None or str(value).strip() == "":
            raise ValueError(f"prepared product missing required field: {key}")
        return str(value).strip()

    @staticmethod
    def _required_decimal_text(prepared: dict[str, object], key: str) -> str:
        value = prepared.get(key)
        if value is None or str(value).strip() == "":
            raise ValueError(f"prepared product missing required price field: {key}")
        return str(value).strip()

    @staticmethod
    def _optional_decimal_text(value: object) -> str | None:
        if value is None or str(value).strip() == "":
            return None
        return str(value).strip()

    @staticmethod
    def _resolve_detail_content(prepared: dict[str, object], options: DraftE2EOptions) -> str:
        if options.detail_content:
            return options.detail_content
        if options.detail_content_file:
            return Path(options.detail_content_file).read_text(encoding="utf-8-sig").strip()
        for key in ("detail_html", "product_summary"):
            value = prepared.get(key)
            if value is not None and str(value).strip():
                return str(value).strip()
        return f"<p>{DraftE2EOrchestrator._required_text(prepared, 'product_name')}</p>"

    @staticmethod
    def _resolve_image_path(prepared: dict[str, object], image_role: str, override_path: str | None) -> str:
        if override_path:
            DraftE2EOrchestrator._assert_existing_file(override_path, f"{image_role}_image_path")
            return override_path

        images = prepared.get("images", [])
        if isinstance(images, list):
            for image in images:
                if not isinstance(image, dict):
                    continue
                if image.get("role") != image_role:
                    continue
                local_path = image.get("local_path")
                if local_path:
                    DraftE2EOrchestrator._assert_existing_file(str(local_path), f"{image_role}_image_path")
                    return str(local_path)

        raise ValueError(f"缺少本地 {image_role} 图片路径，请通过 CLI 参数传入")

    @staticmethod
    def _assert_existing_file(file_path: str, field_name: str) -> None:
        if not Path(file_path).exists():
            raise ValueError(f"{field_name} 不存在: {file_path}")
