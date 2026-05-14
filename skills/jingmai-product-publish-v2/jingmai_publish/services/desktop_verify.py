"""真实京麦桌面验证入口服务。"""

from __future__ import annotations

from dataclasses import asdict

from jingmai_publish.desktop import RealWindowsUIAAdapter, UIATuningConfig, WindowManager
from jingmai_publish.services.jingmai_workflow import JingmaiWorkflowService


class DesktopVerificationService:
    """负责触发真实京麦窗口的 T1~T4 实机验证。"""

    def __init__(
        self,
        screenshot_dir: str,
        tuning: UIATuningConfig | None = None,
    ) -> None:
        """按截图目录初始化真实适配器与工作流。"""

        adapter = RealWindowsUIAAdapter(screenshot_dir=screenshot_dir, tuning=tuning)
        window_manager = WindowManager(adapter)
        self.workflow_service = JingmaiWorkflowService(window_manager)

    def run(
        self,
        step: str = "both",
        debug: bool = False,
        *,
        title: str | None = None,
        model: str | None = None,
        required_attribute: str | None = None,
        brand: str | None = None,
        sku_cell_id: str | None = None,
        sku_value: str | None = None,
        sku_submit: bool = False,
    ) -> dict[str, object]:
        """执行桌面验证流程。"""

        if step not in {"t1", "t2", "t3", "t4", "t5-probe", "t5-input-probe", "both"}:
            raise ValueError(f"不支持的验证步骤: {step}")

        results: dict[str, object] = {}
        t1_result = None

        if step in {"t1", "both", "t3", "t4", "t5-probe", "t5-input-probe"}:
            try:
                t1_result = self.workflow_service.run_t1_attach_window()
                results["t1"] = asdict(t1_result)
                if debug:
                    results["debug"] = self._build_debug_output(
                        window_handle=t1_result.window_handle,
                        target_text="发布商品",
                    )
            except Exception as exc:
                results["t1"] = {
                    "step_id": "T1",
                    "success": False,
                    "page_state": "window_not_found",
                    "window_handle": None,
                    "screenshot_path": None,
                    "message": str(exc),
                }
                if debug:
                    results["debug"] = self._build_debug_output(
                        window_handle=None,
                        target_text="发布商品",
                    )
                return results

        if step in {"t2", "both"}:
            if t1_result is None:
                try:
                    t1_result = self.workflow_service.run_t1_attach_window()
                    results["t1"] = asdict(t1_result)
                except Exception as exc:
                    results["t1"] = {
                        "step_id": "T1",
                        "success": False,
                        "page_state": "window_not_found",
                        "window_handle": None,
                        "screenshot_path": None,
                        "message": str(exc),
                    }
                    if debug:
                        results["debug"] = self._build_debug_output(
                            window_handle=None,
                            target_text="发布商品",
                        )
                    return results
            if not t1_result.window_handle:
                raise RuntimeError("T1 未返回窗口句柄，无法继续 T2")
            t2_result = self.workflow_service.run_t2_enter_publish_entry(t1_result.window_handle)
            results["t2"] = asdict(t2_result)
            if debug:
                results["debug"] = self._build_debug_output(
                    window_handle=t1_result.window_handle,
                    target_text="发布商品",
                )

        if step in {"t3", "t4", "t5-probe", "t5-input-probe"}:
            if t1_result is None:
                raise RuntimeError("T1 未执行成功，无法继续 T3/T4/T5")
            if step in {"t3", "t4"}:
                t3_result = self.workflow_service.run_t3_confirm_category(t1_result.window_handle)
                results["t3"] = asdict(t3_result)
            if step == "t4":
                if not title or not model or not required_attribute:
                    raise ValueError("执行 T4 需要提供 title、model、required_attribute")
                t4_result = self.workflow_service.run_t4_fill_base_info(
                    t1_result.window_handle,
                    title=title,
                    model=model,
                    required_attribute=required_attribute,
                    brand=brand,
                )
                results["t4"] = asdict(t4_result)
            if step == "t5-probe":
                adapter = self.workflow_service.window_manager.adapter
                results["t5_probe"] = adapter.build_sku_probe(t1_result.window_handle)
            if step == "t5-input-probe":
                if not sku_cell_id or sku_value is None:
                    raise ValueError("执行 T5 输入实验需要提供 sku_cell_id 和 sku_value")
                adapter = self.workflow_service.window_manager.adapter
                activation = adapter.activate_cell_by_automation_id(t1_result.window_handle, sku_cell_id)
                typing_result = None
                if activation.get("success"):
                    typing_result = adapter.type_into_focused_control(
                        t1_result.window_handle,
                        sku_value,
                        submit=sku_submit,
                    )
                results["t5_input_probe"] = {
                    "activation": activation,
                    "typing": typing_result,
                }
            if debug:
                results["debug"] = self._build_debug_output(
                    window_handle=t1_result.window_handle,
                    target_text="发布商品",
                )

        return results

    def _build_debug_output(self, window_handle: str | None, target_text: str) -> dict[str, object]:
        """构建真实桌面调试增强输出。"""

        adapter = self.workflow_service.window_manager.adapter
        output: dict[str, object] = {}

        if hasattr(adapter, "build_window_debug_snapshot"):
            output["window_snapshot"] = adapter.build_window_debug_snapshot()

        if window_handle and hasattr(adapter, "list_candidate_controls"):
            output["candidate_controls"] = adapter.list_candidate_controls(window_handle, target_text)

        if window_handle and hasattr(adapter, "build_click_diagnostics"):
            output["click_diagnostics"] = adapter.build_click_diagnostics(window_handle, target_text)

        return output
