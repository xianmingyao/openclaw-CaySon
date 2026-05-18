"""AgentExecutor: getattr-based dispatch replacing hardcoded if/elif chain.

BL-091: Executes ActionSteps by reflecting on workflow_service methods
or private executor methods. Handles param filtering, window_handle
injection, and special step logic (T6 content resolution, probe steps).
"""

from __future__ import annotations

from typing import Any

from .types import ActionStep, RetryLane, StepValidationError


class AgentExecutor:
    """Executes ActionSteps via workflow_service reflection or private methods.

    Public method dispatch:
    - name on self → private executor method (e.g. _run_t5_input_probe)
    - name on workflow_service → reflection call with filtered kwargs + window_handle
    """

    # ── 配置常量（从原有 TaskRunner 迁移） ──
    SKU_FIRST_ROW_MAPPING = {
        "sku_name": "jd-id-8403-311",
        "short_title": "jd-id-8403-312",
        "market_price": "jd-id-8403-313",
        "purchase_price": "jd-id-8403-314",
        "jd_price": "jd-id-8403-315",
    }
    MARKET_PRICE_CANDIDATES = ["jd-id-8403-312", "jd-id-8403-313"]
    SKU_DIMENSION_MAPPING = {
        "weight": "jd-id-8403-319",
        "length_mm": "jd-id-8403-320",
        "width_mm": "jd-id-8403-321",
        "height_mm": "jd-id-8403-322",
    }
    SKU_REQUIRED_MAPPING = {
        "current": "jd-id-8403-328",
        "weight": "jd-id-8403-319",
        "factory_inventory": "jd-id-8403-345",
    }
    DETAIL_PROBE_MARKERS = ("BL-088-3 command", "BL-088-3")
    MAX_DETAIL_CONTENT_CHARS = 90000

    def __init__(self, workflow_service, *, event_loop=None) -> None:
        self.workflow_service = workflow_service
        self.event_loop = event_loop

    # ── 主执行入口 ───────────────────────────────────────────────

    def execute(
            self, step: ActionStep, session: Any, params: dict[str, Any],
            lane: RetryLane | None = None,
    ) -> Any:
        """Execute a single ActionStep, optionally via a RetryLane.

        When lane is provided:
        - lane.method_name replaces step.method_name
        - lane.param_overrides are merged into params (lane wins)

        Returns:
            WorkflowStepResult, dict (for probe steps), or raises.
        """
        # BL-103: lane 覆盖 step 的方法名和参数
        method_name = lane.method_name if lane else step.method_name
        merged_params = dict(params)
        if lane and lane.param_overrides:
            merged_params.update(lane.param_overrides)

        if hasattr(self, method_name):
            # 私有执行器方法
            window_handle = session.window_handle
            if step.step_name != "t1" and not window_handle:
                raise RuntimeError(f"{step.step_name} missing window handle")
            return getattr(self, method_name)(window_handle, merged_params)
        else:
            # workflow_service 反射调度
            method = getattr(self.workflow_service, method_name)
            if step.step_name == "t1":
                return method()

            window_handle = session.window_handle
            if not window_handle:
                raise RuntimeError(f"{step.step_name} missing window handle")
            kwargs = self._build_kwargs(step, merged_params)
            if lane and lane.param_overrides:
                kwargs.update(lane.param_overrides)
            return method(window_handle, **kwargs)

    # ── 参数构建 ─────────────────────────────────────────────────

    def _build_kwargs(
            self, step: ActionStep, params: dict[str, Any]
    ) -> dict[str, Any]:
        """Build method kwargs from params dict using required_params + param_map."""
        kwargs: dict[str, Any] = {}
        for param_key in step.required_params:
            value = params.get(param_key)
            if value is None:
                raise StepValidationError(f"{step.step_name} requires {param_key}")
            mapped_key = step.param_map.get(param_key, param_key)
            kwargs[mapped_key] = value
        # 非必需的映射参数（转发所有映射条目，不在 params 中则默认为 None）
        for param_key, mapped_key in step.param_map.items():
            if param_key not in step.required_params:
                kwargs[mapped_key] = params.get(param_key)
        return kwargs

    # ── T4 探测方法 ───────────────────────────────────────────────

    def _run_t4_option_probe(
            self, window_handle: str, params: dict[str, Any]
    ) -> dict[str, object]:
        adapter = self.workflow_service.window_manager.adapter
        return {
            "brand": adapter.probe_select_options_by_label(window_handle, "品牌"),
            "rated_voltage": adapter.probe_select_options_by_label(window_handle, "额定电压"),
            "cable_length": adapter.probe_select_options_by_label(window_handle, "电缆长度"),
        }

    # ── T5 探测方法 ───────────────────────────────────────────────

    def _run_t5_probe(
            self, window_handle: str, params: dict[str, Any]
    ) -> dict[str, object]:
        adapter = self.workflow_service.window_manager.adapter
        return adapter.build_sku_probe(window_handle)

    def _run_t5_input_probe(
            self, window_handle: str, params: dict[str, Any]
    ) -> dict[str, object]:
        sku_cell_id = params["sku_cell_id"]
        sku_value = params["sku_value"]
        submit = bool(params.get("sku_submit", False))
        adapter = self.workflow_service.window_manager.adapter
        resolved_automation_id = self._resolve_sku_automation_id(window_handle, sku_cell_id)
        before_snapshot = adapter.inspect_controls_by_automation_id(window_handle, resolved_automation_id)
        activation = adapter.activate_cell_by_automation_id(window_handle, resolved_automation_id)
        typing_result = None
        after_snapshot = before_snapshot
        if activation.get("success"):
            typing_result = adapter.type_into_focused_control(window_handle, sku_value, submit=submit)
            after_snapshot = adapter.inspect_controls_by_automation_id(window_handle, resolved_automation_id)
        after_value_visible = self._snapshot_contains_value(after_snapshot, sku_value)
        typed = bool(typing_result and typing_result.get("success"))
        success = bool(activation.get("success") and typed and after_value_visible)
        return {
            "success": success,
            "requested_automation_id": sku_cell_id,
            "resolved_automation_id": resolved_automation_id,
            "before_snapshot": before_snapshot,
            "activation": activation,
            "typing": typing_result,
            "after_snapshot": after_snapshot,
        }

    def _run_t5_row_probe(
            self, window_handle: str, params: dict[str, Any]
    ) -> dict[str, object]:
        payload = {
            "sku_name": params.get("sku_name"),
            "short_title": params.get("short_title"),
            "market_price": params.get("market_price"),
            "purchase_price": params.get("purchase_price"),
            "jd_price": params.get("jd_price"),
        }
        if not any(value is not None for value in payload.values()):
            raise StepValidationError("T5 row probe requires at least one mapped field")
        submit = bool(params.get("sku_submit", False))
        results: dict[str, object] = {}
        for field_name, automation_id in self.SKU_FIRST_ROW_MAPPING.items():
            value = payload.get(field_name)
            if value is None:
                continue
            sub_params = dict(params, sku_cell_id=automation_id, sku_value=value, sku_submit=submit)
            results[field_name] = self._run_t5_input_probe(window_handle, sub_params)
        return {"mapping": self.SKU_FIRST_ROW_MAPPING, "fields": results}

    def _run_t5_market_probe(
            self, window_handle: str, params: dict[str, Any]
    ) -> dict[str, object]:
        market_price = params["market_price"]
        submit = bool(params.get("sku_submit", False))
        results: dict[str, object] = {}
        for automation_id in self.MARKET_PRICE_CANDIDATES:
            sub_params = dict(params, sku_cell_id=automation_id, sku_value=market_price, sku_submit=submit)
            results[automation_id] = self._run_t5_input_probe(window_handle, sub_params)
        return {"candidates": self.MARKET_PRICE_CANDIDATES, "value": market_price, "results": results}

    def _run_t5_first_row(
            self, window_handle: str, params: dict[str, Any]
    ) -> dict[str, object]:
        sku_name = params["sku_name"]
        market_price = params["market_price"]
        purchase_price = params["purchase_price"]
        jd_price = params["jd_price"]
        payload = {
            "sku_name": sku_name,
            "short_title": params.get("short_title") or sku_name,
            "market_price": market_price,
            "purchase_price": purchase_price,
            "jd_price": jd_price,
        }
        submit = bool(params.get("sku_submit", False))
        row_params = dict(params)
        for k, v in payload.items():
            if v is not None:
                row_params[k] = v
        field_results = self._run_t5_row_probe(window_handle, row_params)["fields"]
        document_text = self.workflow_service.window_manager.adapter.read_document_text(window_handle)
        validation = {field_name: value in document_text for field_name, value in payload.items()}
        return {
            "mapping": self.SKU_FIRST_ROW_MAPPING,
            "payload": payload,
            "fields": field_results,
            "validation": validation,
            "success": all(validation.values()),
        }

    def _run_t5_dimension_probe(
            self, window_handle: str, params: dict[str, Any]
    ) -> dict[str, object]:
        payload = {
            "weight": params["weight"],
            "length_mm": params["length_mm"],
            "width_mm": params["width_mm"],
            "height_mm": params["height_mm"],
        }
        submit = bool(params.get("sku_submit", False))
        field_results: dict[str, object] = {}
        for field_name, automation_id in self.SKU_DIMENSION_MAPPING.items():
            sub_params = dict(params, sku_cell_id=automation_id, sku_value=payload[field_name], sku_submit=submit)
            field_results[field_name] = self._run_t5_input_probe(window_handle, sub_params)
        document_text = self.workflow_service.window_manager.adapter.read_document_text(window_handle)
        validation = {field_name: value in document_text for field_name, value in payload.items()}
        return {
            "mapping": self.SKU_DIMENSION_MAPPING,
            "payload": payload,
            "fields": field_results,
            "validation": validation,
            "success": all(validation.values()),
        }

    def _run_t5_weight_probe(
            self, window_handle: str, params: dict[str, Any]
    ) -> dict[str, object]:
        weight = params["weight"]
        submit = bool(params.get("sku_submit", False))
        variants = [weight, weight.replace(".", ""), weight.replace(".", ","), weight.replace(".", "．")]
        ordered_variants: list[str] = []
        seen: set[str] = set()
        for item in variants:
            if not item or item in seen:
                continue
            seen.add(item)
            ordered_variants.append(item)
        results: dict[str, object] = {}
        for variant in ordered_variants:
            sub_params = dict(params, sku_cell_id=self.SKU_DIMENSION_MAPPING["weight"], sku_value=variant,
                              sku_submit=submit)
            probe_result = self._run_t5_input_probe(window_handle, sub_params)
            document_text = self.workflow_service.window_manager.adapter.read_document_text(window_handle)
            probe_result["document_contains"] = variant in document_text
            results[variant] = probe_result
        return {
            "automation_id": self.SKU_DIMENSION_MAPPING["weight"],
            "input_weight": weight,
            "variants": ordered_variants,
            "results": results,
        }

    # ── T6 特殊处理 ──────────────────────────────────────────────

    def _run_t6_transparent_image(
            self, window_handle: str, params: dict[str, Any]
    ) -> Any:
        """T6 透明图上传：支持 transparent_image_path / image_path 回退。"""
        transparent_image_path = params.get("transparent_image_path") or params.get("image_path")
        if not transparent_image_path:
            raise StepValidationError("T6 transparent-image upload requires transparent_image_path")
        return self.workflow_service.run_t6_upload_transparent_image(
            window_handle, transparent_image_path
        )

    def _run_t6_detail_editor(
            self, window_handle: str, params: dict[str, Any]
    ) -> Any:
        """T6 详情编辑器写入：支持多种内容来源解析。"""
        detail_content = self._resolve_detail_content(params)
        return self.workflow_service.run_t6_fill_detail_editor(
            window_handle, detail_content=detail_content
        )

    def _resolve_detail_content(self, params: dict[str, Any]) -> str:
        detail_content = self._normalize_detail_content(params.get("detail_content"))
        if detail_content:
            self._reject_probe_detail_content(detail_content)
            return self._limit_detail_content(detail_content)
        detail_html = self._normalize_detail_content(params.get("detail_html"))
        if detail_html:
            self._reject_probe_detail_content(detail_html)
            return self._limit_detail_content(detail_html)
        detail_content_file = params.get("detail_content_file")
        if detail_content_file:
            file_content = self._read_detail_content_file(str(detail_content_file))
            self._reject_probe_detail_content(file_content)
            return self._limit_detail_content(file_content)
        jd_item_url = self._normalize_detail_content(params.get("jd_item_url"))
        if jd_item_url:
            from jingmai_publish.services.jd_fetch import JDProductFetchService  # 延迟导入，避免循环依赖
            fetcher = JDProductFetchService(None, None, None)
            payload = fetcher.fetch_product_payload(jd_item_url)
            fetched_content = JDProductFetchService.build_detail_editor_content(payload)
            detail_content = self._normalize_detail_content(fetched_content)
            if detail_content:
                self._reject_probe_detail_content(detail_content)
                return self._limit_detail_content(detail_content)
            raise StepValidationError(f"T6 detail editor could not build JD detail content from {jd_item_url}")
        fallback_text = self._normalize_detail_content(params.get("detail_text") or params.get("product_summary"))
        if fallback_text:
            self._reject_probe_detail_content(fallback_text)
            return self._limit_detail_content(f"<p>{fallback_text}</p>")
        raise StepValidationError(
            "T6 detail editor requires detail_content, detail_html, detail_content_file or jd_item_url")

    @classmethod
    def _reject_probe_detail_content(cls, value: str) -> None:
        if any(marker in value for marker in cls.DETAIL_PROBE_MARKERS):
            raise StepValidationError("T6 detail editor refuses BL-088-3 probe text as publishable detail content")

    @classmethod
    def _limit_detail_content(cls, value: str) -> str:
        return value[: cls.MAX_DETAIL_CONTENT_CHARS]

    @staticmethod
    def _normalize_detail_content(value: object) -> str | None:
        if value is None:
            return None
        normalized = str(value).strip()
        return normalized or None

    @staticmethod
    def _read_detail_content_file(file_path: str) -> str:
        from pathlib import Path
        path = Path(file_path)
        if not path.exists():
            raise StepValidationError(f"T6 detail content file does not exist: {file_path}")
        return path.read_text(encoding="utf-8-sig").strip()

    # ── SKU automation_id 解析 ───────────────────────────────────

    def _resolve_sku_automation_id(self, window_handle: str, automation_id: str) -> str:
        adapter = self.workflow_service.window_manager.adapter
        suffix = automation_id.rsplit("-", 1)[-1]
        if not suffix:
            return automation_id
        try:
            probe = adapter.build_sku_probe(window_handle)
        except Exception:
            return automation_id
        candidates = []
        for item in probe.get("dynamic_controls", []):
            candidate_id = str(item.get("automation_id") or "")
            if not candidate_id.endswith(f"-{suffix}"):
                continue
            candidates.append(item)
        if not candidates:
            return automation_id

        def score(item: dict[str, object]) -> tuple[int, int]:
            rects = item.get("rects") or []
            visible_rect_count = 0
            for rect in rects:
                if not isinstance(rect, (list, tuple)) or len(rect) != 4:
                    continue
                left, top, right, bottom = [int(value) for value in rect]
                if right > left and bottom > top:
                    visible_rect_count += 1
            return (visible_rect_count, int(item.get("seen_count") or 0))

        best = sorted(candidates, key=score, reverse=True)[0]
        return str(best.get("automation_id") or automation_id)

    @staticmethod
    def _snapshot_contains_value(snapshot: list[dict[str, object]], value: str) -> bool:
        for item in snapshot:
            text = str(item.get("text") or "")
            if value and value in text:
                return True
        return False
