"""生产 halt 现场证据采集器。"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jm_ufo_agent.runtime.evidence import normalize_halt_evidence


@dataclass(frozen=True)
class HaltEvidenceCollector:
    """采集截图、OCR、窗口摘要和日志路径的统一入口。"""

    artifact_dir: Path
    window_backend: Any | None = None
    ocr_service: Any | None = None

    async def collect(self, task_id: str, row_index: int, node: str, reason: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
        """采集一次 halt 现场证据。"""

        # 该方法只在上游明确 halt 时调用，不参与正常成功路径。
        # window_backend/ocr_service 都是可选注入，缺失时仍生成结构化证据。
        # 所有外部能力失败都会被记录到 details，不再覆盖原始 halt reason。
        evidence: dict[str, Any] = dict(details or {})
        evidence["screenshot_path"] = await self._capture_screenshot(task_id, row_index, node, evidence)
        evidence["window_summary"] = await self._inspect_window(evidence)
        evidence["ocr_summary"] = await self._capture_ocr(evidence)
        evidence["page_signature"] = evidence.get("page_signature") or evidence["ocr_summary"].get("page_signature")
        normalized = normalize_halt_evidence(node, reason, evidence)
        log_path = self._log_path(task_id, row_index, node)
        normalized["log_path"] = str(log_path)
        self._write_log(log_path, normalized)
        return normalized

    async def _capture_screenshot(self, task_id: str, row_index: int, node: str, evidence: dict[str, Any]) -> str | None:
        """通过 window backend 采集截图。"""

        # 没有 window_backend 时返回已有截图路径或 None，保持 dry-run 安全。
        # 截图文件名包含 task/row/node，方便排查同一批次中的失败位置。
        # backend 异常只记录，不阻断 halt 证据生成。
        if self.window_backend is None:
            return evidence.get("screenshot_path")
        screenshot_path = self.artifact_dir / task_id / f"row{row_index}_{node}_halt.png"
        try:
            captured = await self.window_backend.screenshot(screenshot_path)
            return str(captured)
        except Exception as exc:
            evidence.setdefault("capture_errors", []).append({"target": "screenshot", "error_type": exc.__class__.__name__, "error": str(exc)})
            return evidence.get("screenshot_path")

    async def _inspect_window(self, evidence: dict[str, Any]) -> dict[str, Any]:
        """采集京麦窗口事实摘要。"""

        # F17 的 halt 证据需要能回答“当时窗口是什么状态”。
        # 如果 backend 没有 inspect_jingmai，就沿用上游已有 window_summary。
        # 返回值只保留轻量字段，避免把完整窗口树塞进状态。
        if self.window_backend is None or not hasattr(self.window_backend, "inspect_jingmai"):
            return dict(evidence.get("window_summary") or {})
        try:
            facts = await self.window_backend.inspect_jingmai()
            summary = {
                "found": facts.found,
                "main_title": facts.main_title,
                "main_class_name": facts.main_class_name,
                "qt_child_count": facts.qt_child_count,
            }
            if hasattr(facts, "webview_summary"):
                summary.update(facts.webview_summary())
            return summary
        except Exception as exc:
            evidence.setdefault("capture_errors", []).append({"target": "window", "error_type": exc.__class__.__name__, "error": str(exc)})
            return dict(evidence.get("window_summary") or {})

    async def _capture_ocr(self, evidence: dict[str, Any]) -> dict[str, Any]:
        """采集 OCR 摘要。"""

        # OCR 摘要只保存前 20 个文本块，避免状态和日志过大。
        # 如果 ocr_service 不存在，沿用上游已有 ocr_summary。
        # OCR 失败也只记录错误，halt 证据仍会返回。
        if self.ocr_service is None or not hasattr(self.ocr_service, "capture_and_ocr"):
            return dict(evidence.get("ocr_summary") or {})
        try:
            result = await self.ocr_service.capture_and_ocr()
            return {
                "page_signature": getattr(result, "page_signature", ""),
                "screenshot_path": str(getattr(result, "screenshot_path", "") or ""),
                "blocks": [
                    {"text": block.text, "confidence": block.confidence}
                    for block in list(getattr(result, "blocks", []))[:20]
                ],
            }
        except Exception as exc:
            evidence.setdefault("capture_errors", []).append({"target": "ocr", "error_type": exc.__class__.__name__, "error": str(exc)})
            return dict(evidence.get("ocr_summary") or {})

    def _log_path(self, task_id: str, row_index: int, node: str) -> Path:
        """生成 halt 证据日志路径。"""

        # 日志目录按 task_id 分区，便于整批任务归档。
        # 文件名带 UTC 时间，避免同一节点多次 halt 时互相覆盖。
        log_dir = self.artifact_dir / task_id
        log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        return log_dir / f"row{row_index}_{node}_halt_{timestamp}.json"

    def _write_log(self, log_path: Path, payload: dict[str, Any]) -> None:
        """把 halt 证据写入本地 JSON 日志。"""

        # 这里只负责写文件，不重新计算路径，避免 payload 内外路径不一致。
        # ensure_ascii=False 保留中文错误信息，人工排查更直接。
        # sort_keys=True 和 indent=2 让日志可 diff、可人工查看。
        log_path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2), encoding="utf-8")


async def collect_and_halt(state: Any, reason: str, collector: HaltEvidenceCollector, details: dict[str, Any] | None = None) -> dict[str, Any]:
    """采集 halt 证据并写入 GraphState。"""

    # 该 helper 让 workflow 节点不需要手写截图/OCR/window/log 四套采集逻辑。
    # state 只要求具备 task_id、row_index、current_node 和 halt()，避免 runtime 反向强依赖 workflow 类型。
    # 返回 collected evidence，方便节点测试或额外 repository 落库。
    evidence = await collector.collect(
        task_id=state.task_id,
        row_index=state.row_index,
        node=state.current_node,
        reason=reason,
        details=details,
    )
    state.halt(reason, evidence)
    return evidence
