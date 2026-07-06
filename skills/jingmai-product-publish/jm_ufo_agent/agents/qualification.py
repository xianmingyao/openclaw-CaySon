"""资质 PDF 数据模型与占位 Agent。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from jm_ufo_agent.agents.base import AgentContext, AgentResult
from jm_ufo_agent.agents.worker import WorkerAgent


@dataclass(frozen=True)
class QualificationDoc:
    """单个资质文件记录。"""

    doc_type: str  # trademark, business_license, inspection_report, authorization, ccc_cert
    local_path: str = ""  # 本地 PDF 路径，空表示未提供
    status: str = "missing"  # missing, placeholder, ready
    remark: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "doc_type": self.doc_type,
            "local_path": self.local_path,
            "status": self.status,
            "remark": self.remark,
        }


# 京麦上架所需资质清单
REQUIRED_QUALIFICATIONS: tuple[QualificationDoc, ...] = (
    QualificationDoc(doc_type="trademark", remark="商标注册证"),
    QualificationDoc(doc_type="business_license", remark="营业执照"),
    QualificationDoc(doc_type="inspection_report", remark="检测报告"),
    QualificationDoc(doc_type="authorization", remark="授权书"),
    QualificationDoc(doc_type="ccc_cert", remark="3C认证"),
)


class QualificationAgent(WorkerAgent):
    """负责资质文件检查与占位管理。"""

    def __init__(self, handler=None):
        super().__init__(name="qualification", handler=handler)

    async def check(self, context: AgentContext) -> AgentResult:
        """检查资质文件就绪状态。"""

        # 从 product 中读取已有资质，未提供的标记为 missing。
        # 资质不阻塞保存草稿，但会阻塞正式提交审核。
        product_quals = context.product.get("qualifications") or {}
        results: list[dict[str, Any]] = []
        ready_count = 0
        for required in REQUIRED_QUALIFICATIONS:
            existing = product_quals.get(required.doc_type)
            if existing and existing.get("local_path"):
                doc = QualificationDoc(
                    doc_type=required.doc_type,
                    local_path=existing["local_path"],
                    status="ready",
                    remark=required.remark,
                )
                ready_count += 1
            else:
                doc = QualificationDoc(
                    doc_type=required.doc_type,
                    status="missing",
                    remark=required.remark,
                )
            results.append(doc.to_dict())

        all_ready = ready_count == len(REQUIRED_QUALIFICATIONS)
        return AgentResult(
            ok=all_ready,
            message=f"资质就绪 {ready_count}/{len(REQUIRED_QUALIFICATIONS)}",
            data={
                "qualifications": results,
                "ready_count": ready_count,
                "total_count": len(REQUIRED_QUALIFICATIONS),
                "blocks_publish": not all_ready,
                "blocks_draft": False,  # 资质不阻塞保存草稿
            },
        )
