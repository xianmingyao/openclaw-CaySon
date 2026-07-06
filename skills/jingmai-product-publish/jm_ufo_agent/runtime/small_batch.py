"""row5-row7 小批量生产验收门禁。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SmallBatchRowEvidence:
    """单行生产验收证据。"""

    row_index: int
    jd: dict[str, Any] = field(default_factory=dict)
    assets: dict[str, Any] = field(default_factory=dict)
    draft: dict[str, Any] = field(default_factory=dict)
    readback: dict[str, Any] = field(default_factory=dict)
    minimax: dict[str, Any] = field(default_factory=dict)
    artifacts: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "SmallBatchRowEvidence":
        """从 JSON 字典构造单行证据。"""

        # CLI 和测试都会传入普通 dict，这里集中做类型兜底。
        # row_index 是唯一必需字段，缺失时让 int 转换直接暴露错误。
        # 其他证据缺失时用空 dict，让 validator 给出明确缺口。
        return cls(
            row_index=int(payload["row_index"]),
            jd=dict(payload.get("jd") or {}),
            assets=dict(payload.get("assets") or {}),
            draft=dict(payload.get("draft") or {}),
            readback=dict(payload.get("readback") or {}),
            minimax=dict(payload.get("minimax") or {}),
            artifacts=dict(payload.get("artifacts") or {}),
        )

    def to_dict(self) -> dict[str, Any]:
        """转换为可输出的证据字典。"""

        # 保留原始证据摘要，方便 dashboard 或人工复核查看缺口。
        # 不在这里计算通过状态，避免数据对象夹带业务规则。
        # 业务判断统一放在 ProductionSmallBatchValidator。
        return {
            "row_index": self.row_index,
            "jd": dict(self.jd),
            "assets": dict(self.assets),
            "draft": dict(self.draft),
            "readback": dict(self.readback),
            "minimax": dict(self.minimax),
            "artifacts": dict(self.artifacts),
        }


@dataclass(frozen=True)
class SmallBatchRowResult:
    """单行小批量验收结果。"""

    row_index: int
    ok: bool
    missing: list[str] = field(default_factory=list)
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """转换为 JSON 输出字典。"""

        # missing 直接列出阻断点，方便按行修复。
        # evidence 只保留调用方传入的摘要，不生成额外成功假象。
        # ok 是当前行是否满足进入 row82 规则的唯一布尔值。
        return {
            "row_index": self.row_index,
            "ok": self.ok,
            "missing": list(self.missing),
            "evidence": dict(self.evidence),
        }


@dataclass(frozen=True)
class SmallBatchValidationReport:
    """row5-row7 小批量验收报告。"""

    task_id: str
    seed_rows: tuple[int, ...]
    target_row: int
    allow_target_row: bool
    next_row: int | None
    rows: list[SmallBatchRowResult]

    def to_dict(self) -> dict[str, Any]:
        """转换为 CLI/dashboard 可输出字典。"""

        # allow_target_row 为 True 时，调度器才可以自动跳到 target_row。
        # next_row 为 None 表示仍需停机补证据，不应该继续真实生产。
        # rows 保留每一行明细，避免只给总失败导致排查困难。
        return {
            "task_id": self.task_id,
            "seed_rows": list(self.seed_rows),
            "target_row": self.target_row,
            "allow_target_row": self.allow_target_row,
            "next_row": self.next_row,
            "rows": [row.to_dict() for row in self.rows],
        }


class ProductionSmallBatchValidator:
    """根据 row5-row7 真实证据决定是否允许进入 row82。"""

    def __init__(self, seed_rows: tuple[int, ...] = (5, 6, 7), target_row: int = 82, min_completion_score: float = 0.90):
        """保存小批量验收规则。"""

        # seed_rows 来自当前任务的恢复种子规则，不是通用跳行算法。
        # target_row 默认为文档明确要求的 row82。
        # min_completion_score 对齐 F18：表单完成度至少 90% 才允许保存草稿。
        self.seed_rows = seed_rows
        self.target_row = target_row
        self.min_completion_score = min_completion_score

    def validate(self, task_id: str, rows: list[SmallBatchRowEvidence]) -> SmallBatchValidationReport:
        """校验小批量证据并返回是否允许 row82。"""

        # 先按 row_index 建索引，保证 row5-row7 都被逐行检查。
        # 缺失 seed row 会生成失败结果，不会悄悄跳过。
        # 只有全部 seed row 通过时，next_row 才设置为 row82。
        by_row = {row.row_index: row for row in rows}
        row_results: list[SmallBatchRowResult] = []
        for row_index in self.seed_rows:
            evidence = by_row.get(row_index)
            if evidence is None:
                row_results.append(SmallBatchRowResult(row_index=row_index, ok=False, missing=["row_evidence_missing"]))
                continue
            row_results.append(self._validate_row(evidence))
        allow = all(row.ok for row in row_results)
        return SmallBatchValidationReport(
            task_id=task_id,
            seed_rows=self.seed_rows,
            target_row=self.target_row,
            allow_target_row=allow,
            next_row=self.target_row if allow else None,
            rows=row_results,
        )

    def _validate_row(self, evidence: SmallBatchRowEvidence) -> SmallBatchRowResult:
        """校验单行是否具备真实草稿闭环证据。"""

        # 每个检查项都对应设计文档中的 P0 验收面。
        # 这里不调用京东、京麦、MiniMax 或 VLM，只消费它们已经产生的证据。
        # 缺失任何一项都返回明确 missing，调度器据此 halt 当前任务。
        missing: list[str] = []
        if not self._jd_ok(evidence.jd):
            missing.append("jd_title_price_images")
        if not self._assets_ok(evidence.assets):
            missing.append("assets_download_transform")
        if not self._draft_ok(evidence.draft):
            missing.append("draft_save_evidence")
        if not self._readback_ok(evidence.readback):
            missing.append("draft_readback_passed")
        if not self._minimax_ok(evidence.minimax):
            missing.append("minimax_save_draft_decision")
        if not self._artifacts_ok(evidence.artifacts):
            missing.append("screenshot_or_log_artifact")
        return SmallBatchRowResult(row_index=evidence.row_index, ok=not missing, missing=missing, evidence=evidence.to_dict())

    def _jd_ok(self, payload: dict[str, Any]) -> bool:
        """检查京东标题、价格、图片列表证据。"""

        # F02 要求标题、价格、图片列表都抓取成功。
        # 支持 JdCrawlerAgent 的原始 data，也支持批量报告里包装过的 ok 字段。
        # image_urls 必须非空，防止后续 F03 没有图片输入。
        if payload.get("ok") is False:
            return False
        return bool(payload.get("title")) and bool(payload.get("price")) and bool(payload.get("image_urls"))

    def _assets_ok(self, payload: dict[str, Any]) -> bool:
        """检查图片下载和 VLM 转换证据。"""

        # F03 要求主图和副图下载并转换成功；当前证据至少要有下载数和转换数。
        # failed=True 明确阻断，即使 count 字段存在也不能通过。
        # 转换数不能小于 1，避免只有下载没有 VLM 审计。
        if payload.get("failed") is True:
            return False
        return int(payload.get("downloaded_count") or 0) >= 1 and int(payload.get("transformed_count") or 0) >= 1

    def _draft_ok(self, payload: dict[str, Any]) -> bool:
        """检查保存草稿成功证据。"""

        # F07 要求保存草稿成功，并能留下草稿 ID、URL 或 toast/list 证据。
        # ok=False 明确阻断；没有任何可识别草稿证据也阻断。
        # 这里不接受“点击过按钮”作为成功，必须有保存后的结果证据。
        if payload.get("ok") is False:
            return False
        return bool(payload.get("draft_id") or payload.get("draft_url") or payload.get("toast_text") or payload.get("list_page_signature"))

    def _readback_ok(self, payload: dict[str, Any]) -> bool:
        """检查保存后的读回验证证据。"""

        # F07/F17 要求草稿保存后能验证列表页或草稿内容。
        # verification_result=failed 明确阻断。
        # ok=True 或 verification_result=passed 都视为读回通过。
        if payload.get("verification_result") == "failed":
            return False
        return payload.get("ok") is True or payload.get("verification_result") == "passed"

    def _minimax_ok(self, payload: dict[str, Any]) -> bool:
        """检查 MiniMax 评审终结决策证据。"""

        # F19 要求 MiniMax-M3 的终结判断为 save_draft。
        # completion_score 仍然由确定性评分控制，这里只检查评审决策和基础分数。
        # overall_score 如果缺失不硬阻断，但存在时不能低于表单完成度阈值折算。
        if payload.get("decision") != "save_draft":
            return False
        score = payload.get("overall_score", payload.get("score"))
        if score is None:
            return True
        return float(score) >= self.min_completion_score * 100

    def _artifacts_ok(self, payload: dict[str, Any]) -> bool:
        """检查截图、日志或页面 signature 证据。"""

        # F17 要求异常和草稿验证都留下截图/日志/page signature 等证据。
        # 小批量通过时至少要有其中一类可审计证据。
        # 只检查路径或签名是否存在，不在这里读取磁盘，避免 CLI 误触外部路径。
        return bool(payload.get("screenshot_path") or payload.get("log_path") or payload.get("page_signature"))


def validate_small_batch_payload(payload: dict[str, Any]) -> SmallBatchValidationReport:
    """从 CLI JSON payload 执行小批量验收。"""

    # 该函数是命令行入口的薄封装，方便测试直接复用。
    # seed_rows/target_row 可由 payload 覆盖，但默认严格采用当前任务规则。
    # rows 必须是列表，否则让调用方尽早看到输入错误。
    rows = [SmallBatchRowEvidence.from_dict(item) for item in list(payload.get("rows") or [])]
    seed_rows = tuple(int(item) for item in payload.get("seed_rows", (5, 6, 7)))
    target_row = int(payload.get("target_row", 82))
    validator = ProductionSmallBatchValidator(seed_rows=seed_rows, target_row=target_row)
    return validator.validate(str(payload.get("task_id") or ""), rows)

