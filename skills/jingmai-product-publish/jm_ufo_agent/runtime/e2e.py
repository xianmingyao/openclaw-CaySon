"""真实端到端上架流程的安全编排骨架。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from jm_ufo_agent.runtime.production import ProductionReadinessReport, assess_production_readiness, describe_production_pipeline


@dataclass(frozen=True)
class E2EStageResult:
    """端到端阶段结果。"""

    stage: str
    ok: bool
    evidence: dict[str, Any] = field(default_factory=dict)
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        """转换为可输出的阶段证据。"""

        # 每个阶段都必须有 ok 和 evidence，方便 dashboard 展示。
        # message 用于人类快速定位失败原因。
        # stage 使用 production pipeline 固定名称，避免自由文本漂移。
        return {"stage": self.stage, "ok": self.ok, "evidence": dict(self.evidence), "message": self.message}


@dataclass(frozen=True)
class E2ERunReport:
    """端到端运行报告。"""

    readiness: ProductionReadinessReport
    stages: list[E2EStageResult] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """转换为 CLI/dashboard 可输出的字典。"""

        # readiness 失败时 stages 可以为空，表示尚未启动真实流程。
        # stages 按执行顺序记录，失败后由调用方决定是否 halt。
        # 该报告不包含凭证或敏感 headers。
        return {"readiness": self.readiness.to_dict(), "stages": [stage.to_dict() for stage in self.stages]}


class ProductionE2EOrchestrator:
    """安全门控下的真实 E2E 编排器。"""

    def __init__(self, capabilities: dict[str, bool], handlers: dict[str, Any]):
        """保存阶段能力和 handler。"""

        # capabilities 必须显式声明每个阶段是否真实可用。
        # handlers 按阶段名提供 async callable，测试和生产可以注入不同实现。
        # 构造函数不执行任何外部动作。
        self.capabilities = capabilities
        self.handlers = handlers

    async def run(self, initial_payload: dict[str, Any]) -> E2ERunReport:
        """按生产阶段顺序执行 E2E。"""

        # readiness 未通过时立即返回，不触发任何 handler。
        # 每个 handler 接收上一阶段 payload，返回 dict evidence。
        # 阶段失败时停止后续执行，避免真实京麦处于不确定状态还继续操作。
        readiness = assess_production_readiness(self.capabilities)
        if not readiness.ready:
            return E2ERunReport(readiness=readiness)
        payload = dict(initial_payload)
        stages: list[E2EStageResult] = []
        for stage in describe_production_pipeline():
            handler = self.handlers.get(stage)
            if handler is None:
                result = E2EStageResult(stage=stage, ok=False, message="缺少阶段 handler")
            else:
                try:
                    evidence = await handler(payload)
                    payload[stage] = evidence
                    result = E2EStageResult(stage=stage, ok=bool(evidence.get("ok", True)), evidence=dict(evidence))
                except Exception as exc:
                    result = E2EStageResult(stage=stage, ok=False, message=str(exc), evidence={"error_type": exc.__class__.__name__})
            stages.append(result)
            if not result.ok:
                break
        return E2ERunReport(readiness=readiness, stages=stages)
