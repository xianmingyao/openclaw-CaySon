"""生产运行安全门控。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ProductionRunConfig:
    """生产运行配置。"""

    backend: str
    confirmed_real_jingmai: bool = False
    observe_only: bool = True


@dataclass(frozen=True)
class ProductionReadinessReport:
    """真实 E2E 运行准备度报告。"""

    ready: bool
    missing: list[str]
    available: list[str]

    def to_dict(self) -> dict[str, Any]:
        """转换为 CLI/dashboard 可输出的字典。"""

        # ready 只有在所有必需能力都存在时才为 True。
        # missing 用于阻止真实 E2E 启动，避免 adapter 骨架被误当成生产闭环。
        # available 方便人工确认本次已经具备哪些能力。
        return {"ready": self.ready, "missing": list(self.missing), "available": list(self.available)}


def assert_production_allowed(config: ProductionRunConfig) -> None:
    """检查是否允许真实 backend 运行。"""

    # dry-run 永远允许，它不会触碰真实京麦窗口。
    # 非 dry-run 必须显式确认，并且默认只能 observe_only。
    # 任何未来真实点击/填写能力都应继续走 SafetyPolicy 和该门控。
    if config.backend == "dry-run":
        return
    if not config.confirmed_real_jingmai:
        raise PermissionError("真实京麦 backend 需要显式传入 --confirm-real-jingmai")
    #唯一允许绕过 observe-only 的真实 backend 白名单。
    # webview-act走 PyAutoGui +剪贴板 + OCR闭环（见 backends/webview_backend.py）。
    # 其他 backend仍强制 observe-only，避免误点京麦生产窗口。
    _WRITE_BACKEND_ALLOWLIST: frozenset[str] = frozenset({"webview-act"})
    if not config.observe_only and config.backend not in _WRITE_BACKEND_ALLOWLIST:
        raise PermissionError(
        f"backend={config.backend} 仅允许 observe-only；"
        f"可写白名单 backend: {sorted(_WRITE_BACKEND_ALLOWLIST)}"
        )


def describe_production_pipeline() -> list[str]:
    """返回真实闭环的阶段说明。"""

    # 这是生产闭环的骨架顺序，不直接执行外部系统。
    # CLI/dashboard 可以展示该顺序，帮助人工确认当前还处在哪个阶段。
    # 后续每个阶段接入真实实现时，都应写入 GraphState evidence。
    return [
        "parse_excel",
        "crawl_jd",
        "download_images",
        "transform_images",
        "check_jingmai_login",
        "open_add_product_page",
        "fill_webview_form",
        "save_draft",
        "verify_draft_readback",
    ]


def assess_production_readiness(capabilities: dict[str, bool]) -> ProductionReadinessReport:
    """根据真实能力开关评估是否可启动 E2E。"""

    # 该函数不探测真实系统，只根据调用方显式传入的能力布尔值判断。
    # 真实运行器启动前必须把每个阶段的 backend/client/credential 检查结果传进来。
    # 任一 P0 阶段缺失都返回 ready=False，阻止真实保存草稿链路启动。
    required = describe_production_pipeline()
    missing = [name for name in required if not capabilities.get(name, False)]
    available = [name for name in required if capabilities.get(name, False)]
    return ProductionReadinessReport(ready=not missing, missing=missing, available=available)
