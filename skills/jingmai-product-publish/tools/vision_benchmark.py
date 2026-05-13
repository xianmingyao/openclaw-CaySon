"""
视觉基准评分脚本。

用途：
1. 固定页面分类 / 阻断判断 / 锚点命中的评分口径。
2. 后续把真实失败截图整理成 case JSON 后，直接跑出总分与失分项。

运行：
    python tools/vision_benchmark.py --cases benchmarks/vision_cases.sample.json
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PAGE_STATE_WEIGHT = 40
BLOCK_DECISION_WEIGHT = 30
ANCHOR_WEIGHT = 30


@dataclass
class CaseScore:
    case_id: str
    score: int
    page_state_score: int
    block_score: int
    anchor_score: int
    failures: list[str]


def _normalize_anchor_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def score_case(case: dict[str, Any]) -> CaseScore:
    case_id = str(case.get("id", "") or "unknown-case")
    expected = case.get("expected") or {}
    actual = case.get("actual") or {}
    failures: list[str] = []

    expected_page_state = str(expected.get("page_state", "") or "").strip()
    actual_page_state = str(actual.get("page_state", "") or "").strip()
    page_state_score = PAGE_STATE_WEIGHT if expected_page_state and expected_page_state == actual_page_state else 0
    if page_state_score == 0:
        failures.append(f"page_state expected={expected_page_state or '<empty>'} actual={actual_page_state or '<empty>'}")

    expected_block = bool(expected.get("should_block_fill_product_info", False))
    actual_block = bool(actual.get("should_block_fill_product_info", False))
    block_score = BLOCK_DECISION_WEIGHT if expected_block == actual_block else 0
    if block_score == 0:
        failures.append(f"block_decision expected={expected_block} actual={actual_block}")

    expected_anchors = set(_normalize_anchor_list(expected.get("anchors")))
    actual_anchors = set(_normalize_anchor_list(actual.get("anchors")))
    if expected_anchors:
        matched = len(expected_anchors & actual_anchors)
        anchor_score = round(ANCHOR_WEIGHT * matched / len(expected_anchors))
        missing = sorted(expected_anchors - actual_anchors)
        if missing:
            failures.append(f"missing_anchors={missing}")
    else:
        anchor_score = ANCHOR_WEIGHT

    score = int(page_state_score + block_score + anchor_score)
    return CaseScore(
        case_id=case_id,
        score=score,
        page_state_score=int(page_state_score),
        block_score=int(block_score),
        anchor_score=int(anchor_score),
        failures=failures,
    )


def load_cases(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        payload = payload.get("cases", [])
    if not isinstance(payload, list):
        raise ValueError("cases JSON must be a list or an object with a 'cases' list")
    return [case for case in payload if isinstance(case, dict)]


def build_report(cases: list[dict[str, Any]]) -> dict[str, Any]:
    results = [score_case(case) for case in cases]
    total_score = sum(item.score for item in results)
    max_score = len(results) * 100
    average = round(total_score / len(results), 2) if results else 0.0
    return {
        "summary": {
            "case_count": len(results),
            "total_score": total_score,
            "max_score": max_score,
            "average_score": average,
        },
        "results": [
            {
                "id": item.case_id,
                "score": item.score,
                "page_state_score": item.page_state_score,
                "block_score": item.block_score,
                "anchor_score": item.anchor_score,
                "failures": item.failures,
            }
            for item in results
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="jingmai 视觉基准评分")
    parser.add_argument("--cases", required=True, help="case JSON 路径")
    args = parser.parse_args()

    cases_path = Path(args.cases).resolve()
    report = build_report(load_cases(cases_path))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
