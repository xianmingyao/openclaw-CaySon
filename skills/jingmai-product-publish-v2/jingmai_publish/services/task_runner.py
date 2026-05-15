"""Minimal runtime kernel: Session + TaskRunner."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
import uuid

from jingmai_publish.services.jingmai_workflow import WorkflowStepResult


@dataclass(slots=True)
class RunnerSession:
    """Minimum session state for a runtime execution."""

    requested_step: str
    session_id: str = field(default_factory=lambda: f"runner-{uuid.uuid4().hex[:12]}")
    window_handle: str | None = None
    page_state: str | None = None
    completed_steps: list[str] = field(default_factory=list)
    trace: list[dict[str, object]] = field(default_factory=list)
    halted: bool = False
    last_message: str | None = None
    max_retry_count: int = 3


class TaskRunner:
    """Drive the minimum observe -> decide -> act -> verify loop."""

    VALID_STEPS = {
        "t1",
        "t2",
        "t3",
        "t4",
        "t4-extra",
        "t4-option-probe",
        "t5-probe",
        "t5-input-probe",
        "t5-row-probe",
        "t5-market-probe",
        "t5-first-row",
        "t5-dimension-probe",
        "t5-weight-probe",
        "t6-probe",
        "t6-dialog-probe",
        "t6-main-image",
        "t6-transparent-image",
        "t6-detail-editor",
        "t7",
        "t8-probe",
        "t8-save-draft",
        "t8-publish-product",
        "both",
    }

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

    def __init__(self, workflow_service) -> None:
        self.workflow_service = workflow_service

    def run(self, step: str = "both", debug: bool = False, **kwargs) -> dict[str, object]:
        if step not in self.VALID_STEPS:
            raise ValueError(f"unsupported verification step: {step}")

        session = RunnerSession(requested_step=step)
        results: dict[str, object] = {}
        for planned_step in self._build_plan(step):
            outcome = self._execute_with_retry(planned_step, session, kwargs)
            result_key = self._result_key(planned_step)

            if isinstance(outcome, WorkflowStepResult):
                payload = asdict(outcome)
                results[result_key] = payload
                self._apply_workflow_result(session, outcome)
                if not outcome.success:
                    session.halted = True
                    break
            else:
                results[result_key] = outcome

        if debug:
            results["debug"] = self._build_debug_output(session.window_handle, "发布商品")

        results["session"] = {
            "session_id": session.session_id,
            "requested_step": session.requested_step,
            "window_handle": session.window_handle,
            "page_state": session.page_state,
            "completed_steps": session.completed_steps,
            "trace": session.trace,
            "halted": session.halted,
            "last_message": session.last_message,
            "max_retry_count": session.max_retry_count,
        }
        return results

    def _build_plan(self, step: str) -> list[str]:
        if step == "both":
            return ["t1", "t2"]
        if step == "t2":
            return ["t1", "t2"]
        if step in {"t3", "t4", "t4-extra", "t4-option-probe"}:
            return ["t1", "t3", step]
        if step == "t1":
            return ["t1"]
        return ["t1", step]

    def _execute_step(self, planned_step: str, session: RunnerSession, params: dict[str, Any]):
        if planned_step == "t1":
            try:
                return self.workflow_service.run_t1_attach_window()
            except Exception as exc:
                return WorkflowStepResult(
                    step_id="T1",
                    success=False,
                    page_state="window_not_found",
                    window_handle=None,
                    screenshot_path=None,
                    message=str(exc),
                )
        if planned_step == "t2":
            return self.workflow_service.run_t2_enter_publish_entry(self._require_window_handle(session, "T2"))
        if planned_step == "t3":
            return self.workflow_service.run_t3_confirm_category(self._require_window_handle(session, "T3"))
        if planned_step == "t4":
            title = params.get("title")
            model = params.get("model")
            required_attribute = params.get("required_attribute")
            if not title or not model or not required_attribute:
                raise ValueError("T4 requires title, model and required_attribute")
            return self.workflow_service.run_t4_fill_base_info(
                self._require_window_handle(session, "T4"),
                title=title,
                model=model,
                required_attribute=required_attribute,
                brand=params.get("brand"),
            )
        if planned_step == "t4-extra":
            return self.workflow_service.run_t4_fill_additional_required_fields(
                self._require_window_handle(session, "T4-EXTRA"),
                brand=params.get("brand"),
                rated_voltage=params.get("rated_voltage"),
                cable_length=params.get("cable_length"),
                weight=params.get("weight"),
            )
        if planned_step == "t4-option-probe":
            adapter = self.workflow_service.window_manager.adapter
            handle = self._require_window_handle(session, "T4-OPTION-PROBE")
            return {
                "brand": adapter.probe_select_options_by_label(handle, "品牌"),
                "rated_voltage": adapter.probe_select_options_by_label(handle, "额定电压"),
                "cable_length": adapter.probe_select_options_by_label(handle, "电缆长度"),
            }
        if planned_step == "t5-probe":
            adapter = self.workflow_service.window_manager.adapter
            return adapter.build_sku_probe(self._require_window_handle(session, "T5-PROBE"))
        if planned_step == "t5-input-probe":
            sku_cell_id = params.get("sku_cell_id")
            sku_value = params.get("sku_value")
            if not sku_cell_id or sku_value is None:
                raise ValueError("T5 input probe requires sku_cell_id and sku_value")
            return self._run_t5_input_probe(
                self._require_window_handle(session, "T5-INPUT-PROBE"),
                sku_cell_id,
                sku_value,
                bool(params.get("sku_submit", False)),
            )
        if planned_step == "t5-row-probe":
            payload = {
                "sku_name": params.get("sku_name"),
                "short_title": params.get("short_title"),
                "market_price": params.get("market_price"),
                "purchase_price": params.get("purchase_price"),
                "jd_price": params.get("jd_price"),
            }
            if not any(value is not None for value in payload.values()):
                raise ValueError("T5 row probe requires at least one mapped field")
            return self._run_t5_row_probe(
                self._require_window_handle(session, "T5-ROW-PROBE"),
                payload,
                bool(params.get("sku_submit", False)),
            )
        if planned_step == "t5-market-probe":
            market_price = params.get("market_price")
            if market_price is None:
                raise ValueError("T5 market-price probe requires market_price")
            return self._run_t5_market_probe(
                self._require_window_handle(session, "T5-MARKET-PROBE"),
                market_price,
                bool(params.get("sku_submit", False)),
            )
        if planned_step == "t5-first-row":
            sku_name = params.get("sku_name")
            market_price = params.get("market_price")
            purchase_price = params.get("purchase_price")
            jd_price = params.get("jd_price")
            if not sku_name or market_price is None or purchase_price is None or jd_price is None:
                raise ValueError("T5 first-row probe requires sku_name, market_price, purchase_price and jd_price")
            payload = {
                "sku_name": sku_name,
                "short_title": params.get("short_title") or sku_name,
                "market_price": market_price,
                "purchase_price": purchase_price,
                "jd_price": jd_price,
            }
            return self._run_t5_first_row(
                self._require_window_handle(session, "T5-FIRST-ROW"),
                payload,
                bool(params.get("sku_submit", False)),
            )
        if planned_step == "t5-dimension-probe":
            payload = {
                "weight": params.get("weight"),
                "length_mm": params.get("length_mm"),
                "width_mm": params.get("width_mm"),
                "height_mm": params.get("height_mm"),
            }
            if not all(value is not None for value in payload.values()):
                raise ValueError("T5 dimension probe requires weight, length_mm, width_mm and height_mm")
            return self._run_t5_dimension_probe(
                self._require_window_handle(session, "T5-DIMENSION-PROBE"),
                payload,
                bool(params.get("sku_submit", False)),
            )
        if planned_step == "t5-weight-probe":
            weight = params.get("weight")
            if weight is None:
                raise ValueError("T5 weight probe requires weight")
            return self._run_t5_weight_probe(
                self._require_window_handle(session, "T5-WEIGHT-PROBE"),
                weight,
                bool(params.get("sku_submit", False)),
            )
        if planned_step == "t6-probe":
            return self.workflow_service.run_t6_probe(self._require_window_handle(session, "T6-PROBE"))
        if planned_step == "t6-dialog-probe":
            image_path = params.get("image_path")
            if not image_path:
                raise ValueError("T6 dialog probe requires image_path")
            return self.workflow_service.run_t6_upload_dialog_probe(
                self._require_window_handle(session, "T6-DIALOG-PROBE"),
                image_path,
            )
        if planned_step == "t6-main-image":
            image_path = params.get("image_path")
            if not image_path:
                raise ValueError("T6 main-image upload requires image_path")
            return self.workflow_service.run_t6_upload_main_image(
                self._require_window_handle(session, "T6-MAIN-IMAGE"),
                image_path,
            )
        if planned_step == "t6-transparent-image":
            transparent_image_path = params.get("transparent_image_path") or params.get("image_path")
            if not transparent_image_path:
                raise ValueError("T6 transparent-image upload requires transparent_image_path")
            return self.workflow_service.run_t6_upload_transparent_image(
                self._require_window_handle(session, "T6-TRANSPARENT-IMAGE"),
                transparent_image_path,
            )
        if planned_step == "t6-detail-editor":
            detail_content = params.get("detail_content")
            if not detail_content:
                raise ValueError("T6 detail editor requires detail_content")
            return self.workflow_service.run_t6_fill_detail_editor(
                self._require_window_handle(session, "T6-DETAIL-EDITOR"),
                detail_content=detail_content,
            )
        if planned_step == "t7":
            required = ["sale_unit", "package_type", "delivery_mark", "package_list", "warranty_period"]
            if not all(params.get(name) for name in required):
                raise ValueError("T7 requires sale_unit, package_type, delivery_mark, package_list and warranty_period")
            return self.workflow_service.run_t7_fill_logistics_fields(
                self._require_window_handle(session, "T7"),
                sale_unit=params["sale_unit"],
                package_type=params["package_type"],
                delivery_mark=params["delivery_mark"],
                package_list=params["package_list"],
                warranty_period=params["warranty_period"],
            )
        if planned_step == "t8-probe":
            return self.workflow_service.run_t8_probe(self._require_window_handle(session, "T8-PROBE"))
        if planned_step == "t8-save-draft":
            return self.workflow_service.run_t8_save_draft(self._require_window_handle(session, "T8-SAVE-DRAFT"))
        if planned_step == "t8-publish-product":
            return self.workflow_service.run_t8_publish_product(
                self._require_window_handle(session, "T8-PUBLISH-PRODUCT")
            )
        raise ValueError(f"unknown planned step: {planned_step}")

    @staticmethod
    def _result_key(planned_step: str) -> str:
        return planned_step.replace("-", "_")

    @staticmethod
    def _require_window_handle(session: RunnerSession, step_name: str) -> str:
        if not session.window_handle:
            raise RuntimeError(f"{step_name} missing window handle")
        return session.window_handle

    @staticmethod
    def _apply_workflow_result(session: RunnerSession, result: WorkflowStepResult) -> None:
        session.window_handle = result.window_handle or session.window_handle
        session.page_state = result.page_state
        session.completed_steps.append(result.step_id)
        session.last_message = result.message

    def _execute_with_retry(self, planned_step: str, session: RunnerSession, params: dict[str, Any]):
        last_outcome = None
        for attempt_no in range(1, session.max_retry_count + 1):
            before_state = {
                "window_handle": session.window_handle,
                "page_state": session.page_state,
                "completed_steps": list(session.completed_steps),
            }
            outcome = self._execute_step(planned_step, session, params)
            last_outcome = outcome
            verified = self._is_verified(outcome)
            failure_signature = None if verified else self._build_failure_signature(planned_step, attempt_no, outcome)
            after_state = self._extract_after_state(outcome, session)
            session.trace.append(
                {
                    "planned_step": planned_step,
                    "attempt_no": attempt_no,
                    "before_state": before_state,
                    "after_state": after_state,
                    "verified": verified,
                    "failure_signature": failure_signature,
                }
            )
            if verified:
                return outcome
        return last_outcome

    @staticmethod
    def _is_verified(outcome) -> bool:
        if isinstance(outcome, WorkflowStepResult):
            return bool(outcome.success)
        if isinstance(outcome, dict) and "success" in outcome:
            return bool(outcome["success"])
        return True

    @staticmethod
    def _build_failure_signature(planned_step: str, attempt_no: int, outcome) -> str:
        if isinstance(outcome, WorkflowStepResult):
            message = outcome.message or "no_message"
            return f"{planned_step}|attempt={attempt_no}|page={outcome.page_state}|message={message}"
        return f"{planned_step}|attempt={attempt_no}|result=unverified"

    @staticmethod
    def _extract_after_state(outcome, session: RunnerSession) -> dict[str, object]:
        if isinstance(outcome, WorkflowStepResult):
            return {
                "window_handle": outcome.window_handle or session.window_handle,
                "page_state": outcome.page_state,
                "screenshot_path": outcome.screenshot_path,
                "message": outcome.message,
            }
        return {
            "window_handle": session.window_handle,
            "page_state": session.page_state,
            "result_type": type(outcome).__name__,
        }

    def _build_debug_output(self, window_handle: str | None, target_text: str) -> dict[str, object]:
        adapter = self.workflow_service.window_manager.adapter
        output: dict[str, object] = {}
        if hasattr(adapter, "build_window_debug_snapshot"):
            output["window_snapshot"] = adapter.build_window_debug_snapshot()
        if window_handle and hasattr(adapter, "list_candidate_controls"):
            output["candidate_controls"] = adapter.list_candidate_controls(window_handle, target_text)
        if window_handle and hasattr(adapter, "build_click_diagnostics"):
            output["click_diagnostics"] = adapter.build_click_diagnostics(window_handle, target_text)
        return output

    def _run_t5_input_probe(
        self,
        window_handle: str,
        automation_id: str,
        value: str,
        submit: bool,
    ) -> dict[str, object]:
        adapter = self.workflow_service.window_manager.adapter
        before_snapshot = adapter.inspect_controls_by_automation_id(window_handle, automation_id)
        activation = adapter.activate_cell_by_automation_id(window_handle, automation_id)
        typing_result = None
        after_snapshot = before_snapshot
        if activation.get("success"):
            typing_result = adapter.type_into_focused_control(window_handle, value, submit=submit)
            after_snapshot = adapter.inspect_controls_by_automation_id(window_handle, automation_id)
        return {
            "before_snapshot": before_snapshot,
            "activation": activation,
            "typing": typing_result,
            "after_snapshot": after_snapshot,
        }

    def _run_t5_row_probe(
        self,
        window_handle: str,
        payload: dict[str, str | None],
        submit: bool,
    ) -> dict[str, object]:
        results: dict[str, object] = {}
        for field_name, automation_id in self.SKU_FIRST_ROW_MAPPING.items():
            value = payload.get(field_name)
            if value is None:
                continue
            results[field_name] = self._run_t5_input_probe(window_handle, automation_id, value, submit)
        return {"mapping": self.SKU_FIRST_ROW_MAPPING, "fields": results}

    def _run_t5_market_probe(
        self,
        window_handle: str,
        market_price: str,
        submit: bool,
    ) -> dict[str, object]:
        results: dict[str, object] = {}
        for automation_id in self.MARKET_PRICE_CANDIDATES:
            results[automation_id] = self._run_t5_input_probe(window_handle, automation_id, market_price, submit)
        return {"candidates": self.MARKET_PRICE_CANDIDATES, "value": market_price, "results": results}

    def _run_t5_first_row(
        self,
        window_handle: str,
        payload: dict[str, str],
        submit: bool,
    ) -> dict[str, object]:
        field_results = self._run_t5_row_probe(window_handle, payload, submit)["fields"]
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
        self,
        window_handle: str,
        payload: dict[str, str],
        submit: bool,
    ) -> dict[str, object]:
        field_results: dict[str, object] = {}
        for field_name, automation_id in self.SKU_DIMENSION_MAPPING.items():
            field_results[field_name] = self._run_t5_input_probe(window_handle, automation_id, payload[field_name], submit)
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
        self,
        window_handle: str,
        weight: str,
        submit: bool,
    ) -> dict[str, object]:
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
            probe_result = self._run_t5_input_probe(window_handle, self.SKU_DIMENSION_MAPPING["weight"], variant, submit)
            document_text = self.workflow_service.window_manager.adapter.read_document_text(window_handle)
            probe_result["document_contains"] = variant in document_text
            results[variant] = probe_result
        return {
            "automation_id": self.SKU_DIMENSION_MAPPING["weight"],
            "input_weight": weight,
            "variants": ordered_variants,
            "results": results,
        }
