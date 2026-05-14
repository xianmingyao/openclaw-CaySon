"""京麦桌面工作流服务。"""

from __future__ import annotations

from dataclasses import dataclass
import re

from jingmai_publish.desktop.window_manager import WindowManager
from jingmai_publish.repositories.runtime_log import RuntimeLogRepository


@dataclass(slots=True)
class WorkflowStepResult:
    """工作流步骤执行结果。"""

    step_id: str
    success: bool
    page_state: str
    window_handle: str | None = None
    screenshot_path: str | None = None
    message: str | None = None


class JingmaiWorkflowService:
    """负责京麦桌面 T1/T2 骨架流程。"""

    TITLE_AUTOMATION_ID = "jd-id-8403-277"
    BRAND_AUTOMATION_ID = "jd-id-8403-278"
    MODEL_AUTOMATION_ID = "jd-id-8403-279"
    REQUIRED_ATTR_AUTOMATION_ID = "jd-id-8403-284"

    def __init__(
        self,
        window_manager: WindowManager,
        runtime_log_repo: RuntimeLogRepository | None = None,
    ) -> None:
        """注入窗口管理器和日志仓库。"""

        self.window_manager = window_manager
        self.runtime_log_repo = runtime_log_repo

    def run_t1_attach_window(self) -> WorkflowStepResult:
        """执行 T1：接管京麦窗口。"""

        window = self.window_manager.attach_jingmai_window()
        screenshot_path = self.window_manager.adapter.capture_window(window.handle)

        if self.runtime_log_repo is not None:
            self.runtime_log_repo.append_log(
                session_id=f"window-{window.handle}",
                log_type="process",
                message=f"T1 已接管京麦窗口: {window.title}",
                detail_path=screenshot_path,
            )

        return WorkflowStepResult(
            step_id="T1",
            success=True,
            page_state="jingmai_home",
            window_handle=window.handle,
            screenshot_path=screenshot_path,
            message=f"已接管京麦窗口: {window.title}",
        )

    def run_t2_enter_publish_entry(self, window_handle: str) -> WorkflowStepResult:
        """执行 T2：进入商品发布入口。"""

        clicked = self.window_manager.adapter.click_text(window_handle, "发布商品")
        screenshot_path = self.window_manager.adapter.capture_window(window_handle)

        if self.runtime_log_repo is not None:
            self.runtime_log_repo.append_log(
                session_id=f"window-{window_handle}",
                log_type="process",
                message="T2 已尝试进入发布商品入口",
                detail_path=screenshot_path,
            )

        return WorkflowStepResult(
            step_id="T2",
            success=clicked,
            page_state="publish_entry" if clicked else "jingmai_home",
            window_handle=window_handle,
            screenshot_path=screenshot_path,
            message="已进入发布商品入口" if clicked else "未找到发布商品入口",
        )

    def run_t3_confirm_category(self, window_handle: str) -> WorkflowStepResult:
        """执行 T3：确认当前发布页类目上下文。"""

        category_path = self._extract_category_path(window_handle)
        screenshot_path = self.window_manager.adapter.capture_window(window_handle)
        success = bool(category_path)

        if self.runtime_log_repo is not None:
            self.runtime_log_repo.append_log(
                session_id=f"window-{window_handle}",
                log_type="process",
                message=f"T3 类目确认结果: {category_path or '未识别'}",
                detail_path=screenshot_path,
            )

        return WorkflowStepResult(
            step_id="T3",
            success=success,
            page_state="category_confirmed" if success else "publish_entry",
            window_handle=window_handle,
            screenshot_path=screenshot_path,
            message=f"已确认商品类目: {category_path}" if success else "未识别到商品类目",
        )

    def run_t4_fill_base_info(
        self,
        window_handle: str,
        *,
        title: str,
        model: str,
        required_attribute: str,
        brand: str | None = None,
    ) -> WorkflowStepResult:
        """执行 T4：填写基础信息最小闭环。"""

        adapter = self.window_manager.adapter
        title_filled = adapter.fill_edit_by_automation_id(window_handle, self.TITLE_AUTOMATION_ID, title)
        model_filled = adapter.fill_edit_by_automation_id(window_handle, self.MODEL_AUTOMATION_ID, model)
        attr_filled = adapter.fill_edit_by_automation_id(
            window_handle,
            self.REQUIRED_ATTR_AUTOMATION_ID,
            required_attribute,
        )
        brand_filled = True
        brand_message = "未要求品牌自动选择"

        if brand:
            brand_filled = adapter.select_combobox_by_automation_id(window_handle, self.BRAND_AUTOMATION_ID, brand)
            brand_message = "品牌已填写" if brand_filled else "品牌填写失败"

        document_text = adapter.read_document_text(window_handle)
        title_ok = title in document_text
        model_ok = model in document_text
        attr_ok = required_attribute in document_text
        brand_ok = True if not brand else brand in document_text
        success = title_ok and model_ok and attr_ok and brand_ok

        screenshot_path = adapter.capture_window(window_handle)
        message_parts = [
            f"标题填充={'成功' if title_filled else '失败'}",
            f"标题校验={'成功' if title_ok else '失败'}",
            f"型号填充={'成功' if model_filled else '失败'}",
            f"型号校验={'成功' if model_ok else '失败'}",
            f"必填属性填充={'成功' if attr_filled else '失败'}",
            f"必填属性校验={'成功' if attr_ok else '失败'}",
            f"品牌填充={'成功' if brand_filled else '失败' if brand else '未要求'}",
            f"品牌校验={'成功' if brand_ok else '失败' if brand else '未要求'}",
        ]

        if self.runtime_log_repo is not None:
            self.runtime_log_repo.append_log(
                session_id=f"window-{window_handle}",
                log_type="process",
                message="T4 基础信息填写: " + "，".join(message_parts),
                detail_path=screenshot_path,
            )

        return WorkflowStepResult(
            step_id="T4",
            success=success,
            page_state="base_info_completed" if success else "publish_entry",
            window_handle=window_handle,
            screenshot_path=screenshot_path,
            message="；".join(message_parts),
        )

    def _extract_category_path(self, window_handle: str) -> str | None:
        """从发布页文档文本中提取商品类目路径。"""

        document_text = self.window_manager.adapter.read_document_text(window_handle)
        matched = re.search(r"商品类目\s*([^\n]+?)\s*修改", document_text)
        if matched:
            category_path = " ".join(matched.group(1).split())
            return category_path.strip()
        return None
