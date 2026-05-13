"""
京麦商品发布自动化 - CLI 入口
"""
import inspect
import json
import re
import sys
import uuid
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Tuple

import click

from pricing_rules import derive_market_price


def _build_runtime_settings(settings_overrides: Dict[str, Any] | None = None):
    from settings import Settings, get_settings

    if settings_overrides:
        settings = Settings(**settings_overrides)
        settings.ensure_dirs()
        return settings
    return get_settings()


def _prepare_runtime_services(settings_overrides: Dict[str, Any] | None = None) -> Dict[str, Any]:
    from llm.service_manager import ensure_vllm_ready

    settings = _build_runtime_settings(settings_overrides)
    report = ensure_vllm_ready(settings)
    if report.get("started"):
        click.echo(
            f"LLM preflight: vLLM start requested pid={report.get('pid')} "
            f"log={report.get('log_file')}"
        )
    elif report.get("ready"):
        click.echo("LLM preflight: vLLM ready")
    elif report.get("reason") not in {"autostart_disabled", "non_local_base_url"}:
        click.echo(f"LLM preflight: vLLM unavailable ({report.get('reason', 'unknown')})")
        if report.get("runtime_error"):
            click.echo(f"LLM preflight runtime error: {report['runtime_error']}")
        if report.get("log_tail"):
            click.echo("LLM preflight log tail:")
            click.echo(report["log_tail"])
    return report


def _read_json_file(path: Path) -> Any:
    """兼容普通 UTF-8 和 UTF-8 BOM。"""
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _load_product_data(file_path: str = "", data_str: str = "") -> Dict[str, Any]:
    if file_path:
        return _read_json_file(Path(file_path))
    if data_str:
        return json.loads(data_str)
    click.echo("错误: 需要 --config 或 --data 提供商品数据", err=True)
    sys.exit(1)


def _load_batch_items(path: Path) -> List[Dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".json":
        data = _read_json_file(path)
        items = data if isinstance(data, list) else [data]
        return _annotate_publish_mode(
            [_enrich_product_from_source(item) for item in items],
            source_path=path,
        )

    if suffix in {".xlsx", ".xlsm"}:
        from openpyxl import load_workbook

        workbook = load_workbook(path, read_only=True, data_only=True)
        items: List[Dict[str, Any]] = []
        workbook_meta: Dict[str, Any] = {
            "source_file": str(path.resolve()),
            "sheet_count": 0,
            "data_row_count": 0,
            "sheet_names": [],
            "recognized_headers": [],
            "raw_headers": [],
            "template_signals": [],
        }
        for sheet in workbook.worksheets:
            rows = list(sheet.iter_rows(values_only=True))
            if not rows:
                continue

            header_index = _detect_header_row_index(rows)
            headers = [str(cell).strip() if cell is not None else "" for cell in rows[header_index]]
            mapped_headers = [_normalize_header(header) for header in headers]
            if sum(1 for item in mapped_headers if item) < 4:
                continue
            workbook_meta["sheet_count"] += 1
            workbook_meta["sheet_names"].append(sheet.title)
            workbook_meta["raw_headers"].extend([header for header in headers if header])
            workbook_meta["recognized_headers"].extend([header for header in mapped_headers if header])
            workbook_meta["template_signals"].extend(_detect_template_signals(headers))

            for row_offset, row in enumerate(rows[header_index + 1 :], start=header_index + 2):
                payload: Dict[str, Any] = {}
                for index, cell in enumerate(row):
                    key = mapped_headers[index] if index < len(mapped_headers) else ""
                    if not key or cell in (None, ""):
                        continue
                    payload[key] = cell
                if "jd_price" in payload:
                    payload.setdefault("price", payload["jd_price"])
                    market_price = derive_market_price(payload["jd_price"])
                    if market_price is not None:
                        payload.setdefault("market_price", market_price)
                if payload:
                    workbook_meta["data_row_count"] += 1
                    payload["source_meta"] = {
                        "source_file": str(path.resolve()),
                        "sheet_name": sheet.title,
                        "row_index": row_offset,
                        "workflow_doc": _default_workflow_doc_path(),
                        "template_features": {
                            "sheet_name": sheet.title,
                            "recognized_headers": [header for header in mapped_headers if header],
                            "raw_headers": [header for header in headers if header],
                            "signals": _detect_template_signals(headers),
                        },
                    }
                    items.append(_enrich_product_from_source(payload))
        return _annotate_publish_mode(items, source_path=path, workbook_meta=workbook_meta)

    raise ValueError(f"不支持的批量文件格式: {path.suffix}")


def _default_workflow_doc_path() -> str:
    candidates = sorted(Path(".").glob("*.docx"))
    for candidate in candidates:
        if "上架流程" in candidate.stem:
            return str(candidate.resolve())
    return str(candidates[0].resolve()) if candidates else ""


def _detect_template_signals(headers: List[str]) -> List[str]:
    signals: List[str] = []
    normalized_headers = [str(header or "").strip().lower() for header in headers if str(header or "").strip()]
    batch_keywords = [
        "批量",
        "sku",
        "商家编码",
        "子商品",
        "子sku",
        "规格1",
        "规格2",
        "规格值",
        "多规格",
        "销售属性",
    ]
    for header in normalized_headers:
        for keyword in batch_keywords:
            if keyword.lower() in header and keyword not in signals:
                signals.append(keyword)
    return signals


def _infer_publish_mode(
    items: List[Dict[str, Any]],
    *,
    workbook_meta: Dict[str, Any] | None = None,
) -> Tuple[str, str]:
    total_items = len(items)
    workbook_meta = workbook_meta or {}
    if total_items > 1:
        return "batch", f"multiple_rows:{total_items}"

    data_row_count = int(workbook_meta.get("data_row_count", total_items) or total_items)
    sheet_count = int(workbook_meta.get("sheet_count", 0) or 0)
    signals = [str(item) for item in (workbook_meta.get("template_signals") or []) if str(item).strip()]
    recognized_headers = [str(item) for item in (workbook_meta.get("recognized_headers") or []) if str(item).strip()]
    if data_row_count > 1:
        return "batch", f"data_rows:{data_row_count}"
    if sheet_count > 1 and total_items > 0:
        return "batch", f"multi_sheet:{sheet_count}"
    if any(signal for signal in signals if signal in {"批量", "sku", "子sku", "多规格", "销售属性"}):
        return "batch", f"template_signals:{','.join(signals)}"
    if {"title", "url"}.issubset(set(recognized_headers)) and any(
        header in {"unit", "jd_price", "price", "brand"} for header in recognized_headers
    ):
        return "single", "single_row_standard_listing"
    return "single", f"default_single:{total_items}"


def _annotate_publish_mode(
    items: List[Dict[str, Any]],
    source_path: Path | None = None,
    workbook_meta: Dict[str, Any] | None = None,
) -> List[Dict[str, Any]]:
    mode, reason = _infer_publish_mode(items, workbook_meta=workbook_meta)
    annotated: List[Dict[str, Any]] = []
    for index, item in enumerate(items, start=1):
        payload = dict(item or {})
        source_meta = dict(payload.get("source_meta") or {})
        if source_path is not None:
            source_meta.setdefault("source_file", str(source_path.resolve()))
        source_meta["publish_mode"] = mode
        source_meta["publish_mode_reason"] = reason
        source_meta["item_index"] = index
        source_meta["total_items"] = len(items)
        if workbook_meta:
            source_meta.setdefault(
                "template_features",
                {
                    "sheet_count": int(workbook_meta.get("sheet_count", 0) or 0),
                    "data_row_count": int(workbook_meta.get("data_row_count", len(items)) or len(items)),
                    "signals": list(workbook_meta.get("template_signals") or []),
                    "recognized_headers": list(workbook_meta.get("recognized_headers") or []),
                },
            )
        payload["publish_mode"] = mode
        payload["source_meta"] = source_meta
        annotated.append(payload)
    return annotated


def _merge_missing_fields(target: Dict[str, Any], source: Dict[str, Any], fields: List[str]) -> None:
    for field in fields:
        if target.get(field) not in (None, "", []):
            continue
        value = source.get(field)
        if value in (None, "", []):
            continue
        target[field] = value


def _extract_product_id_from_text(value: str) -> str:
    text = str(value or "")
    for pattern in (r"jd\.com/(\d+)\.html", r"skuId=(\d+)", r"\b(\d{8,})\b"):
        match = re.search(pattern, text, re.I)
        if match:
            return match.group(1)
    return ""


def _is_weak_model(value: Any) -> bool:
    text = str(value or "").strip()
    lowered = text.lower()
    if lowered in {"", "none", "n/a", "na", "null", "?", "？"}:
        return True
    if len(text) <= 2 and not any(ch.isdigit() or ("a" <= ch.lower() <= "z") for ch in text):
        return True
    return False


@lru_cache(maxsize=1)
def _load_local_product_presets() -> List[Dict[str, Any]]:
    presets: List[Dict[str, Any]] = []
    for path in sorted((Path("config")).glob("*.json")):
        try:
            payload = _read_json_file(path)
        except Exception:
            continue
        if not isinstance(payload, dict):
            continue
        product = payload.get("product", payload)
        if not isinstance(product, dict):
            continue
        presets.append({"path": str(path), "payload": payload, "product": product})
    return presets


def _matches_local_product_preset(payload: Dict[str, Any], preset_product: Dict[str, Any]) -> bool:
    payload_ids = {
        _extract_product_id_from_text(payload.get("product_id", "")),
        _extract_product_id_from_text(payload.get("url", "")),
        _extract_product_id_from_text(payload.get("jd_url", "")),
    } - {""}
    preset_ids = {
        _extract_product_id_from_text(preset_product.get("product_id", "")),
        _extract_product_id_from_text(preset_product.get("url", "")),
        _extract_product_id_from_text(preset_product.get("jd_url", "")),
    } - {""}
    if payload_ids and preset_ids and payload_ids.intersection(preset_ids):
        return True

    payload_model = str(payload.get("model", "") or "").strip().lower()
    preset_model = str(preset_product.get("model", "") or preset_product.get("sku_model", "") or "").strip().lower()
    if payload_model and preset_model and payload_model == preset_model:
        return True

    title = str(payload.get("title", "") or "").lower()
    if preset_model and title and preset_model in title:
        return True
    return False


def _extract_title_variant_signals(value: Any) -> Dict[str, str]:
    text = str(value or "")
    signals: Dict[str, str] = {}

    cable_length_match = re.search(r"总控\s*(\d+(?:\.\d+)?)\s*米", text, re.I)
    if cable_length_match is None:
        cable_length_match = re.search(r"(\d+(?:\.\d+)?)\s*米", text, re.I)
    if cable_length_match is not None:
        signals["cable_length_m"] = cable_length_match.group(1)

    socket_positions_match = re.search(r"【\s*(\d+)\s*位\s*】", text)
    if socket_positions_match is None:
        socket_positions_match = re.search(r"(\d+)\s*位", text)
    if socket_positions_match is not None:
        signals["socket_positions"] = socket_positions_match.group(1)

    return signals


def _titles_conflict_for_variant_merge(payload: Dict[str, Any], preset_product: Dict[str, Any]) -> bool:
    payload_title = str(payload.get("title", "") or "").strip()
    preset_title = str(preset_product.get("title", "") or "").strip()
    if not payload_title or not preset_title:
        return False
    if payload_title == preset_title:
        return False

    payload_signals = _extract_title_variant_signals(payload_title)
    preset_signals = _extract_title_variant_signals(preset_title)
    if not payload_signals or not preset_signals:
        return False

    for key, payload_value in payload_signals.items():
        preset_value = preset_signals.get(key)
        if preset_value and payload_value != preset_value:
            return True
    return False


def _merge_local_product_preset(payload: Dict[str, Any]) -> Dict[str, Any]:
    enriched = dict(payload)
    merged_attributes = dict(enriched.get("attributes") or {})
    for preset in _load_local_product_presets():
        product = preset["product"]
        if not _matches_local_product_preset(enriched, product):
            continue
        title_conflict = _titles_conflict_for_variant_merge(enriched, product)
        _merge_missing_fields(
            enriched,
            product,
            ["brand", "unit", "product_id", "url", "jd_url"],
        )
        if title_conflict:
            continue
        _merge_missing_fields(
            enriched,
            product,
            ["notes", "packing_list", "sales_unit"],
        )
        if _is_weak_model(enriched.get("model")) and product.get("model"):
            enriched["model"] = product.get("model")
        for key, value in dict(product.get("attributes") or {}).items():
            if merged_attributes.get(key) in (None, "") and value not in (None, ""):
                merged_attributes[key] = value
        if merged_attributes.get("current") in (None, "") and merged_attributes.get("rated_current") not in (None, ""):
            merged_attributes["current"] = merged_attributes["rated_current"]
        if merged_attributes:
            enriched["attributes"] = merged_attributes
    return enriched


def _enrich_product_from_source(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        return payload

    url = str(payload.get("source_url", payload.get("url", "")) or "").strip()
    if not url:
        return payload

    needs_detail = any(
        payload.get(field) in (None, "", [])
        for field in ("description_images", "detail_content", "description")
    )
    if not needs_detail:
        return payload

    try:
        from scraper import JDScraper

        scraped = JDScraper().scrape(url)
    except Exception:
        return payload

    if not scraped.get("success"):
        return payload

    enriched = dict(payload)
    _merge_missing_fields(
        enriched,
        scraped,
        [
            "product_id",
            "title",
            "price",
            "jd_price",
            "market_price",
            "brand",
            "category",
            "description",
            "detail_content",
            "description_images",
            "images",
        ],
    )
    if enriched.get("price") in (None, "") and scraped.get("price") not in (None, ""):
        enriched["price"] = scraped.get("price")
    if enriched.get("jd_price") in (None, "") and scraped.get("price") not in (None, ""):
        enriched["jd_price"] = scraped.get("price")
    if enriched.get("market_price") in (None, "") and enriched.get("jd_price") not in (None, ""):
        market_price = derive_market_price(enriched.get("jd_price"))
        if market_price is not None:
            enriched["market_price"] = market_price
    return _merge_local_product_preset(enriched)


def _detect_header_row_index(rows: List[tuple]) -> int:
    best_index = 0
    best_score = -1
    for index, row in enumerate(rows[:10]):
        headers = [str(cell).strip() if cell is not None else "" for cell in row]
        score = sum(1 for header in headers if _normalize_header(header))
        if score > best_score:
            best_index = index
            best_score = score
        if score >= 4:
            return index
    return best_index


def _normalize_header(header: str) -> str:
    raw = header.strip()
    normalized = (
        raw.lower()
        .replace("（", "(")
        .replace("）", ")")
        .replace("：", ":")
        .replace(" ", "")
    )

    exact_mapping = {
        "title": "title",
        "商品标题": "title",
        "名称": "title",
        "price": "price",
        "价格": "price",
        "category": "category",
        "类目": "category",
        "分类": "category",
        "sku": "sku",
        "SKU": "sku",
        "货号": "sku",
        "product_id": "product_id",
        "商品编号": "product_id",
        "url": "url",
        "链接": "url",
        "品牌": "brand",
        "商品型号": "model",
        "型号": "model",
        "长(mm)": "length_mm",
        "宽(mm)": "width_mm",
        "高(mm)": "height_mm",
        "重(kg)": "weight_kg",
        "重(kg）": "weight_kg",
        "单位": "unit",
        "备注": "notes",
    }
    if raw in exact_mapping:
        return exact_mapping[raw]
    if normalized in exact_mapping:
        return exact_mapping[normalized]

    contains_mapping = [
        ("商品名称", "title"),
        ("开票内容", "title"),
        ("申请业务", "business_line"),
        ("商品类目", "category"),
        ("品牌", "brand"),
        ("商品型号", "model"),
        ("长(mm", "length_mm"),
        ("宽(mm", "width_mm"),
        ("高(mm", "height_mm"),
        ("重(kg", "weight_kg"),
        ("单位", "unit"),
        ("京东挂网价", "jd_price"),
        ("下单金额", "jd_price"),
        ("京东链接", "url"),
        ("只能读取京东链接", "url"),
        ("商品资质", "qualification_files"),
        ("商品简述", "summary"),
        ("备注", "notes"),
    ]
    for needle, mapped in contains_mapping:
        if needle.lower().replace(" ", "") in normalized:
            return mapped
    return ""


def _product_payload(product_data: Dict[str, Any]) -> Dict[str, Any]:
    return product_data.get("product", product_data)


def _build_product_model(product_data: Dict[str, Any], source: str = "manual"):
    from models import Product

    src = _product_payload(product_data)
    images = product_data.get("images", src.get("images", [])) or []
    detail_images = product_data.get("description_images", src.get("description_images", [])) or []
    source_meta = product_data.get("source_meta", src.get("source_meta", {})) or {}
    category = src.get("category", "")
    product_id = str(src.get("product_id", src.get("sku", "")) or "").strip()
    if not product_id:
        product_id = _extract_product_id_from_text(src.get("source_url", src.get("url", "")))
    return Product(
        product_id=product_id,
        title=str(src.get("title", "")),
        source_url=str(src.get("source_url", src.get("url", ""))),
        category=str(category),
        category_path=str(src.get("category_path", category)),
        price=float(src.get("price", 0) or 0),
        stock=int(src.get("stock", 0) or 0),
        status=str(src.get("status", "draft")),
        source=source,
        attributes=src.get("attributes", {}) or {},
        images=images,
        detail_images=detail_images,
        source_meta=source_meta,
        raw_data=product_data,
    )


def _build_db(settings):
    from db import DatabaseManager

    return DatabaseManager(mysql_url=settings.MYSQL_URL, sqlite_url=settings.SQLITE_URL)


def _build_factory(settings_overrides: Dict[str, Any] | None = None):
    from agents.factory import AgentFactory

    if not settings_overrides:
        return AgentFactory()

    from settings import Settings

    settings = Settings(**settings_overrides)
    settings.ensure_dirs()
    return AgentFactory(settings=settings)


def _persist_product_snapshot(product_data: Dict[str, Any], *, source: str, task_id: str = "") -> Dict[str, Any]:
    from settings import get_settings

    product_model = _build_product_model(product_data, source=source)
    source_meta = dict(product_model.source_meta or {})
    if task_id:
        source_meta["task_id"] = task_id
    product_model.source_meta = source_meta

    settings = get_settings()
    db = _build_db(settings)
    db.create_tables()
    saved = db.save_product(product_model)
    return {
        "product_id": getattr(saved, "product_id", ""),
        "title": getattr(saved, "title", ""),
        "source": getattr(saved, "source", source),
    }


def _extract_plan_payload(plan_data: Any) -> Dict[str, Any]:
    """兼容完整计划包与旧版 steps-only 计划文件。"""
    if isinstance(plan_data, list):
        return {
            "task_id": "",
            "steps": plan_data,
            "product_data": {},
            "total_steps": len(plan_data),
        }

    if isinstance(plan_data, dict):
        steps = plan_data.get("plan")
        if steps is None:
            steps = plan_data.get("steps", [])
        if isinstance(steps, dict):
            steps = steps.get("steps", [])
        steps = steps or []
        return {
            "task_id": str(plan_data.get("task_id", "")),
            "steps": steps,
            "product_data": plan_data.get("product_data", {}),
            "screen_context": plan_data.get("screen_context", {}),
            "total_steps": int(plan_data.get("total_steps", len(steps)) or len(steps)),
        }

    raise ValueError("计划文件格式无效")


def _build_plan_package(plan_result: Dict[str, Any]) -> Dict[str, Any]:
    plan_steps = plan_result["plan"]
    return {
        "task_id": plan_result["task_id"],
        "product_data": plan_result["product_data"],
        "screen_context": plan_result.get("screen_context", {}),
        "plan": plan_steps,
        "total_steps": plan_result["total_steps"],
        "phases": _summarize_plan_phases(plan_steps),
        "workflow_policy": plan_result.get("workflow_policy", "default"),
        "workflow_doc": plan_result.get("workflow_doc", ""),
        "publish_mode": plan_result.get("publish_mode", ""),
    }


def _resolve_resume_step_index(plan_data: Any, steps: List[Dict[str, Any]]) -> int:
    if not isinstance(plan_data, dict):
        return 0

    plan_steps = plan_data.get("plan")
    if not isinstance(plan_steps, list):
        return 0

    for idx, step in enumerate(plan_steps):
        if str(step.get("status", "")).lower() != "success":
            return idx
    return len(steps)


_PHASE_ALIASES = {
    "1": "window_ready",
    "window": "window_ready",
    "window_ready": "window_ready",
    "2": "publish_page_ready",
    "page": "publish_page_ready",
    "publish_page": "publish_page_ready",
    "publish_page_ready": "publish_page_ready",
    "3": "category_ready",
    "category": "category_ready",
    "category_ready": "category_ready",
    "4": "product_info_ready",
    "product": "product_info_ready",
    "product_info": "product_info_ready",
    "product_info_ready": "product_info_ready",
    "5": "draft_saved",
    "draft": "draft_saved",
    "draft_saved": "draft_saved",
    "6": "draft_verified",
    "draft_verified": "draft_verified",
    "7": "publish_submitted",
    "publish": "publish_submitted",
    "publish_submitted": "publish_submitted",
    "8": "publish_verified",
    "publish_verified": "publish_verified",
}


def _normalize_phase_name(phase_name: str) -> str:
    key = str(phase_name or "").strip().lower().replace("-", "_").replace(" ", "_")
    return _PHASE_ALIASES.get(key, key)


def _summarize_plan_phases(steps: List[Dict[str, Any]]) -> List[str]:
    phases: List[str] = []
    for step in steps:
        phase = str(step.get("phase", "")).strip()
        if phase and phase not in phases:
            phases.append(phase)
    return phases


def _resolve_phase_step_index(steps: List[Dict[str, Any]], start_from_phase: str) -> Tuple[int, str]:
    normalized_phase = _normalize_phase_name(start_from_phase)
    if not normalized_phase:
        return 0, ""

    for idx, step in enumerate(steps):
        if _normalize_phase_name(step.get("phase", "")) == normalized_phase:
            return idx, normalized_phase

    available = ", ".join(_summarize_plan_phases(steps))
    raise ValueError(f"未找到 phase: {start_from_phase}。可用 phases: {available or '无'}")


def _read_batch_progress(progress_file: str) -> Dict[str, Any]:
    path = Path(progress_file)
    if not path.exists():
        return {"completed_count": 0, "failed_indices": [], "items": []}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {"completed_count": 0, "failed_indices": [], "items": []}


def _write_batch_progress(progress_file: str, payload: Dict[str, Any]) -> None:
    path = Path(progress_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _build_progress_callback(prefix: str = ""):
    def on_progress(step_index, total_steps, action, success, retries, observation, **_):
        status_icon = "OK" if success else "FAIL"
        retry_info = f"（重试 {retries} 次）" if retries > 1 else ""
        obs_status = ""
        if observation:
            vision = observation.get("status", "")
            stage = observation.get("stage", "")
            stage_prefix = f"{stage}:" if stage else ""
            if vision == "ok":
                obs_status = f" [{stage_prefix}视觉验证通过]".replace("[:", "[")
            elif vision == "error":
                obs_status = f" [{stage_prefix}视觉验证失败]".replace("[:", "[")
            elif vision == "unknown":
                obs_status = f" [{stage_prefix}动作结果兜底]".replace("[:", "[")
            else:
                obs_status = f" [{observation.get('reason', '')[:30]}]"
        line = f"[{step_index}/{total_steps}] {action}: {status_icon}{retry_info}{obs_status}".rstrip()
        click.echo(f"{prefix}{line}" if prefix else line)

    return on_progress


def _print_execution_diagnostics(result: Dict[str, Any], prefix: str = ""):
    risk_stats = result.get("risk_stats") or {}
    high_risk_count = int(risk_stats.get("high_risk_window_shift_count", 0) or 0)
    if high_risk_count > 0:
        click.echo(f"{prefix}高风险窗口漂移: {high_risk_count} 次")

    recovery_error = result.get("recovery_error", "")
    if recovery_error:
        click.echo(f"{prefix}恢复错误: {recovery_error}")

    vision_stats = result.get("vision_fallback_stats") or {}
    vision_count = int(vision_stats.get("count", 0) or 0)
    if vision_count > 0:
        template_hits = vision_stats.get("templates") or {}
        success_count = int(vision_stats.get("success_count", 0) or 0)
        failed_count = int(vision_stats.get("failed_count", 0) or 0)
        summary = "，".join(
            f"{template} {count}次"
            for template, count in sorted(template_hits.items(), key=lambda item: (-item[1], item[0]))
        )
        if summary:
            click.echo(f"{prefix}视觉兜底: {vision_count} 次（成功 {success_count} / 失败 {failed_count}，{summary}）")
        else:
            click.echo(f"{prefix}视觉兜底: {vision_count} 次（成功 {success_count} / 失败 {failed_count}）")

    failed_details = vision_stats.get("failed_details") or []
    for detail in failed_details:
        template_name = detail.get("template", "") or "unknown-template"
        screenshot = detail.get("screenshot", "") or "no-screenshot"
        action = detail.get("action", "") or "unknown-action"
        step = detail.get("step", "?")
        click.echo(
            f"{prefix}失败兜底: step={step} action={action} template={template_name} screenshot={screenshot}"
        )


def _default_plan_path(task_id: str) -> str:
    plan_dir = Path("data/plans")
    plan_dir.mkdir(parents=True, exist_ok=True)
    return str((plan_dir / f"{task_id}.json").resolve())


def _build_acceptance_run_paths(batch_file: str, plan_out: str = "", progress_file: str = "") -> Dict[str, str]:
    batch_path = Path(batch_file).resolve()
    run_id = f"acceptance-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
    base_dir = Path(plan_out).resolve() if plan_out else (Path("data") / "acceptance-runs" / run_id).resolve()
    base_dir.mkdir(parents=True, exist_ok=True)
    progress_path = (Path(progress_file).resolve() if progress_file else (base_dir / "progress.json").resolve())
    summary_path = (base_dir / "summary.json").resolve()
    return {
        "run_id": run_id,
        "batch_file": str(batch_path),
        "plan_dir": str(base_dir),
        "progress_file": str(progress_path),
        "summary_file": str(summary_path),
    }


def _record_acceptance_run_start(paths: Dict[str, str], workflow_policy: str, total_items: int):
    from models import AcceptanceRun
    from settings import get_settings

    db = _build_db(get_settings())
    db.create_tables()
    db.create_acceptance_run(
        AcceptanceRun(
            run_id=paths["run_id"],
            batch_file=paths["batch_file"],
            workflow_policy=workflow_policy,
            status="running",
            total_items=total_items,
            plan_dir=paths["plan_dir"],
            progress_file=paths["progress_file"],
            summary_file=paths["summary_file"],
        )
    )
    return db


def _run_db_preflight(settings) -> Dict[str, Any]:
    started_at = datetime.now().isoformat()
    db = _build_db(settings)
    probe = db.probe() if hasattr(db, "probe") else {"db_type": getattr(db, "db_type", "unknown")}
    probe["started_at"] = started_at
    try:
        db.create_tables()
        probe["create_tables"] = "ok"
    except Exception as exc:
        probe["create_tables"] = "error"
        probe["error"] = str(exc)
    probe["final_db_type"] = getattr(db, "db_type", probe.get("db_type", "unknown"))
    return probe


def _write_db_preflight(paths: Dict[str, str], payload: Dict[str, Any]) -> str:
    target = Path(paths["plan_dir"]) / "db-preflight.json"
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(target.resolve())


def _write_acceptance_summary(summary_file: str, payload: Dict[str, Any]) -> str:
    path = Path(summary_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path.resolve())


def _safe_filename_fragment(value: Any, default: str = "item") -> str:
    text = str(value or "").strip()
    if not text:
        return default
    text = re.sub('[<>:"/\\\\|?*\x00-\x1f]+', "-", text)
    text = re.sub(r"\s+", "-", text)
    text = text.strip(" .-_")
    return text[:120] or default


def _collect_step_screenshots(results: List[Dict[str, Any]]) -> List[str]:
    screenshots: List[str] = []
    for item in results or []:
        candidate = str(item.get("screenshot", "") or "").strip()
        if candidate and candidate not in screenshots:
            screenshots.append(candidate)
    return screenshots


def _build_result_page_judgement(exec_result: Dict[str, Any]) -> Dict[str, Any]:
    results = list(exec_result.get("results", []) or [])
    for item in reversed(results):
        observation = item.get("observation")
        if isinstance(observation, dict) and observation:
            return {
                "status": str(observation.get("status", "") or ""),
                "reason": str(observation.get("reason", "") or ""),
                "stage": str(observation.get("stage", "") or ""),
                "action": str(item.get("action", "") or ""),
                "step": int(item.get("step", 0) or 0),
            }
    return {
        "status": "unknown",
        "reason": str(exec_result.get("error", "") or ""),
        "stage": "",
        "action": "",
        "step": int(exec_result.get("failed_step", 0) or 0),
    }


def _build_execution_evidence(exec_result: Dict[str, Any], product_data: Dict[str, Any]) -> Dict[str, Any]:
    db_task = None
    db_steps: List[Dict[str, Any]] = []
    db_product = None
    try:
        from settings import get_settings

        db = _build_db(get_settings())
        task_id = str(exec_result.get("task_id", "") or "")
        product_id = str((exec_result.get("product_snapshot") or {}).get("product_id", "") or "")
        if task_id:
            db_task = db.get_task(task_id)
            db_steps = db.get_steps(task_id)
        if product_id:
            db_product = db.get_product(product_id)
    except Exception as exc:
        db_task = {"error": f"db-evidence-unavailable: {exc}"}

    return {
        "task_id": str(exec_result.get("task_id", "") or ""),
        "success": bool(exec_result.get("success", False)),
        "failed_step": int(exec_result.get("failed_step", 0) or 0),
        "error": str(exec_result.get("error", "") or ""),
        "publish_mode": str(exec_result.get("publish_mode", product_data.get("publish_mode", "")) or ""),
        "workflow_policy": str((exec_result.get("plan") or {}).get("workflow_policy", "") or ""),
        "product_snapshot": exec_result.get("product_snapshot") or {},
        "plan_file": str(exec_result.get("plan_file", "") or ""),
        "result_page_judgement": _build_result_page_judgement(exec_result),
        "screenshots": _collect_step_screenshots(list(exec_result.get("results", []) or [])),
        "risk_stats": dict(exec_result.get("risk_stats") or {}),
        "vision_fallback_stats": dict(exec_result.get("vision_fallback_stats") or {}),
        "db_task": db_task,
        "db_steps": db_steps,
        "db_product": db_product,
    }


def _write_item_evidence(base_dir: str, index: int, exec_result: Dict[str, Any], product_data: Dict[str, Any]) -> str:
    evidence_dir = Path(base_dir) / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    task_slug = _safe_filename_fragment(exec_result.get("task_id", "") or f"item-{index}", default=f"item-{index}")
    path = evidence_dir / f"{index:03d}-{task_slug}.json"
    payload = _build_execution_evidence(exec_result, product_data)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path.resolve())


def _resolve_plan_output_path(plan_out: str, task_id: str, treat_as_dir: bool = False) -> str:
    if not plan_out:
        return _default_plan_path(task_id)

    output_path = Path(plan_out)
    if treat_as_dir:
        output_path.mkdir(parents=True, exist_ok=True)
        return str((output_path / f"{task_id}.json").resolve())

    output_path.parent.mkdir(parents=True, exist_ok=True)
    return str(output_path.resolve())


def _invoke_executor_run(executor, **kwargs):
    run_method = executor.run
    try:
        signature = inspect.signature(run_method)
    except (TypeError, ValueError):
        return run_method(**kwargs)

    parameters = signature.parameters
    if any(param.kind == inspect.Parameter.VAR_KEYWORD for param in parameters.values()):
        return run_method(**kwargs)

    filtered_kwargs = {name: value for name, value in kwargs.items() if name in parameters}
    return run_method(**filtered_kwargs)


def _run_publish_flow(
    product_data: Dict[str, Any],
    plan_out: str = "",
    progress_prefix: str = "",
    start_from_phase: str = "",
    workflow_policy: str = "default",
    settings_overrides: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    factory = _build_factory(settings_overrides)
    planner = factory.create_planner()
    plan_result = planner.run(product_data=product_data, workflow_policy=workflow_policy)
    if not plan_result.get("success"):
        return {"success": False, "stage": "plan", "error": plan_result.get("error", "规划失败")}

    plan_package = _build_plan_package(plan_result)
    plan_file_path = _resolve_plan_output_path(plan_out, plan_result["task_id"])
    plan_path = Path(plan_file_path)
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(json.dumps(plan_package, ensure_ascii=False, indent=2), encoding="utf-8")
    plan_file = str(plan_path.resolve())

    try:
        persisted = _persist_product_snapshot(
            plan_result["product_data"],
            source=f"publish:{workflow_policy}",
            task_id=plan_result["task_id"],
        )
        click.echo(f"{progress_prefix}商品已落库: {persisted.get('product_id', 'N/A')}")
    except Exception as exc:
        return {"success": False, "stage": "persist", "error": f"商品落库失败: {exc}"}

    click.echo(f"{progress_prefix}Plan-and-Solve 完成，共 {plan_result['total_steps']} 步")

    executor = factory.create_executor()
    resume_step_index = 0
    resolved_phase = ""
    if start_from_phase:
        resume_step_index, resolved_phase = _resolve_phase_step_index(plan_result["plan"], start_from_phase)
        click.echo(f"{progress_prefix}混合执行：从 phase={resolved_phase}（步骤 {resume_step_index + 1}）开始")

    exec_result = _invoke_executor_run(
        executor,
        plan=plan_result["plan"],
        task_id=plan_result["task_id"],
        plan_file=plan_file,
        original_plan_data=plan_package,
        on_progress=_build_progress_callback(progress_prefix),
        resume_step_index=resume_step_index,
    )
    exec_result["task_id"] = plan_result["task_id"]
    exec_result["plan"] = plan_package
    exec_result["start_from_phase"] = resolved_phase
    exec_result["plan_file"] = plan_file
    exec_result["product_snapshot"] = persisted
    exec_result["publish_mode"] = plan_result.get("publish_mode", product_data.get("publish_mode", ""))
    return exec_result


@click.group()
@click.version_option(version="2.0.0", prog_name="jingmai")
def cli():
    """京麦商品发布自动化 v2.0"""


@cli.command()
@click.option("--config", "-c", "config_file", help="商品数据 JSON 文件路径")
@click.option("--data", "-d", help="商品数据 JSON 字符串")
@click.option("--plan-out", default="", help="可选：保存完整计划包 JSON，供监控/恢复执行")
@click.option("--start-from-phase", default="", help="混合执行：从指定业务 phase 开始，如 category_ready / product_info_ready / publish_submitted")
@click.option("--workflow-policy", type=click.Choice(["default", "doc_strict"]), default="default", help="计划策略")
def publish(config_file, data, plan_out, start_from_phase, workflow_policy):
    """发布商品（默认主入口：Plan-and-Solve → ReAct → Reflection）"""
    product_data = _load_product_data(config_file, data)
    _prepare_runtime_services()
    result = _run_publish_flow(
        product_data=product_data,
        plan_out=plan_out,
        progress_prefix="  ",
        start_from_phase=start_from_phase,
        workflow_policy=workflow_policy,
    )

    if result["success"]:
        _print_execution_diagnostics(result)
        click.echo(f"发布成功: task_id={result['task_id']}")
        return

    _print_execution_diagnostics(result)
    click.echo(f"发布失败: {result.get('error')}", err=True)
    if result.get("failed_step"):
        click.echo(f"失败步骤: {result['failed_step']}")
    sys.exit(1)


@cli.command()
@click.argument("task_desc", required=False, default="")
@click.option("--config", "-c", "config_file", help="商品数据 JSON 文件路径")
@click.option("--data", "-d", help="商品数据 JSON 字符串")
@click.option("--steps-only", is_flag=True, help="仅输出步骤数组，兼容旧版脚本")
@click.option("--workflow-policy", type=click.Choice(["default", "doc_strict"]), default="default", help="计划策略")
def plan(task_desc, config_file, data, steps_only, workflow_policy):
    """仅生成执行计划，不执行。"""
    from agents.factory import AgentFactory

    product_data = _load_product_data(config_file, data) if (config_file or data) else {}
    planner = AgentFactory().create_planner()
    result = planner.run(product_data=product_data, task_desc=task_desc, workflow_policy=workflow_policy)
    if result.get("success"):
        payload = result["plan"] if steps_only else _build_plan_package(result)
        click.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    click.echo(f"规划失败: {result.get('error')}", err=True)
    sys.exit(1)


@cli.command()
@click.option("--config", "-c", "config_file", required=True, help="计划 JSON 文件路径")
@click.option("--task-id", "-t", default="", help="任务 ID")
@click.option("--resume/--from-start", default=True, help="默认从首个非 success 步骤续跑；--from-start 强制从第 1 步重跑")
@click.option("--start-from-phase", default="", help="从指定业务 phase 开始执行，覆盖默认 resume 行为")
def execute(config_file, task_id, resume, start_from_phase):
    """执行已有计划文件（默认断点续跑；每步截图视觉验证，失败递进重试 3 次）"""
    from agents.factory import AgentFactory

    plan_data = _read_json_file(Path(config_file))
    payload = _extract_plan_payload(plan_data)
    steps = payload["steps"]
    actual_task_id = task_id or payload["task_id"]

    if not steps:
        click.echo("执行失败: 计划文件中没有可执行步骤", err=True)
        sys.exit(1)

    resolved_phase = ""
    if start_from_phase:
        resume_step_index, resolved_phase = _resolve_phase_step_index(steps, start_from_phase)
    else:
        resume_step_index = _resolve_resume_step_index(plan_data, steps) if resume else 0
    if resume_step_index >= len(steps):
        click.echo(f"计划中的 {len(steps)} 个步骤都已成功，无需重跑")
        return
    if resolved_phase:
        click.echo(f"从 phase={resolved_phase} 开始执行，起始步骤 {resume_step_index + 1}")
    elif resume_step_index > 0:
        click.echo(f"检测到前 {resume_step_index} 步已成功，从步骤 {resume_step_index + 1} 续跑")

    click.echo(f"ReAct 执行开始，共 {len(steps)} 步")

    executor = AgentFactory().create_executor()
    result = _invoke_executor_run(
        executor,
        plan=steps,
        task_id=actual_task_id,
        plan_file=str(Path(config_file).resolve()),
        original_plan_data=plan_data if isinstance(plan_data, dict) else {},
        on_progress=_build_progress_callback("  "),
        resume_step_index=resume_step_index,
    )

    if result["success"]:
        _print_execution_diagnostics(result)
        click.echo(f"执行成功: task_id={actual_task_id or 'N/A'}")
        return

    _print_execution_diagnostics(result)
    click.echo(f"执行失败: {result.get('error')}", err=True)
    if result.get("failed_step"):
        click.echo(f"失败步骤: {result['failed_step']}")
    sys.exit(1)


@cli.command()
@click.option("--question", "-q", default="", help="问题文本")
@click.option("--screenshot", "-s", default="", help="截图路径")
@click.argument("question_arg", required=False, default="")
def think(question, screenshot, question_arg):
    """LLM 思考分析。"""
    from agents.factory import AgentFactory

    q = question or question_arg
    if not q and not screenshot:
        click.echo("错误: 需要问题或截图", err=True)
        sys.exit(1)

    result = AgentFactory().create_thinker().run(question=q, screenshot_path=screenshot)
    if result.get("success"):
        click.echo(result["response"])
        return

    click.echo(f"思考失败: {result.get('error')}", err=True)
    sys.exit(1)


def _run_batch_publish_items(
    items: List[Dict[str, Any]],
    *,
    stop_on_error: bool,
    plan_out: str,
    resume: bool,
    progress_file: str,
    start_from_phase: str,
    workflow_policy: str,
    settings_overrides: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    success_count = 0
    fail_count = 0
    batch_plan_dir = Path(plan_out).resolve() if plan_out else None
    progress = _read_batch_progress(progress_file)
    start_index = int(progress.get("completed_count", 0) or 0) if resume else 0

    if start_index > 0:
        click.echo(f"批量续跑：从第 {start_index + 1} 个商品开始")

    for index, product_data in enumerate(items, start=1):
        if index <= start_index:
            continue
        payload = _product_payload(product_data)
        title = (payload.get("title") or "?")[:30]
        item_publish_mode = str(product_data.get("publish_mode", (product_data.get("source_meta") or {}).get("publish_mode", "single")) or "single")
        click.echo(f"\n[{index}/{len(items)}] 处理: {title}")
        try:
            item_plan_out = ""
            if batch_plan_dir is not None:
                item_plan_out = str(batch_plan_dir / f"item-{index}.json")

            exec_result = _run_publish_flow(
                product_data=product_data,
                plan_out=item_plan_out,
                progress_prefix="  ",
                start_from_phase=start_from_phase,
                workflow_policy=workflow_policy,
                settings_overrides=settings_overrides,
            )
            task_id = exec_result.get("task_id", "")
            if batch_plan_dir is not None and task_id:
                final_path = _resolve_plan_output_path(str(batch_plan_dir), task_id, treat_as_dir=True)
                interim_path = Path(item_plan_out)
                if interim_path.exists() and str(interim_path.resolve()) != final_path:
                    Path(final_path).write_text(interim_path.read_text(encoding="utf-8"), encoding="utf-8")
                    interim_path.unlink()

            vision_stats = exec_result.get("vision_fallback_stats") or {}
            vision_count = int(vision_stats.get("count", 0) or 0)
            successful_vision_count = int(vision_stats.get("success_count", 0) or 0)
            failed_vision_count = int(vision_stats.get("failed_count", 0) or 0)
            template_hits = vision_stats.get("templates") or {}
            failed_vision_details = vision_stats.get("failed_details") or []
            evidence_file = _write_item_evidence(str(batch_plan_dir or Path(progress_file).parent), index, exec_result, product_data)
            result_judgement = _build_result_page_judgement(exec_result)

            if exec_result.get("success"):
                _print_execution_diagnostics(exec_result, prefix="  ")
                click.echo(f"  成功: task_id={exec_result.get('task_id', 'N/A')}")
                success_count += 1
                progress["completed_count"] = index
                progress.setdefault("items", []).append(
                    {
                        "index": index,
                        "title": title,
                        "task_id": task_id,
                        "success": True,
                        "publish_mode": item_publish_mode,
                        "start_from_phase": exec_result.get("start_from_phase", ""),
                        "workflow_policy": workflow_policy,
                        "plan_file": str(exec_result.get("plan_file", "") or ""),
                        "evidence_file": evidence_file,
                        "result_page_judgement": result_judgement,
                        "product_snapshot": exec_result.get("product_snapshot") or {},
                        "vision_fallback_count": vision_count,
                        "vision_fallback_success_count": successful_vision_count,
                        "vision_fallback_failed_count": failed_vision_count,
                        "vision_templates": template_hits,
                        "vision_failed_details": failed_vision_details,
                    }
                )
                _write_batch_progress(progress_file, progress)
            else:
                _print_execution_diagnostics(exec_result, prefix="  ")
                stage = exec_result.get("stage", "execute")
                click.echo(f"  失败({stage}): {exec_result.get('error')}")
                if exec_result.get("failed_step"):
                    click.echo(f"  失败步骤: {exec_result['failed_step']}")
                fail_count += 1
                failed = progress.setdefault("failed_indices", [])
                if index not in failed:
                    failed.append(index)
                progress.setdefault("items", []).append(
                    {
                        "index": index,
                        "title": title,
                        "task_id": task_id,
                        "success": False,
                        "publish_mode": item_publish_mode,
                        "error": exec_result.get("error", ""),
                        "failed_step": exec_result.get("failed_step", 0),
                        "start_from_phase": exec_result.get("start_from_phase", ""),
                        "workflow_policy": workflow_policy,
                        "plan_file": str(exec_result.get("plan_file", "") or ""),
                        "evidence_file": evidence_file,
                        "result_page_judgement": result_judgement,
                        "product_snapshot": exec_result.get("product_snapshot") or {},
                        "vision_fallback_count": vision_count,
                        "vision_fallback_success_count": successful_vision_count,
                        "vision_fallback_failed_count": failed_vision_count,
                        "vision_templates": template_hits,
                        "vision_failed_details": failed_vision_details,
                    }
                )
                _write_batch_progress(progress_file, progress)
                if stop_on_error:
                    break
        except Exception as exc:
            click.echo(f"  异常: {exc}")
            fail_count += 1
            failed = progress.setdefault("failed_indices", [])
            if index not in failed:
                failed.append(index)
            progress.setdefault("items", []).append(
                {
                    "index": index,
                    "title": title,
                    "task_id": "",
                    "success": False,
                    "publish_mode": item_publish_mode,
                    "error": str(exc),
                    "failed_step": 0,
                    "start_from_phase": _normalize_phase_name(start_from_phase) if start_from_phase else "",
                    "workflow_policy": workflow_policy,
                }
            )
            _write_batch_progress(progress_file, progress)
            if stop_on_error:
                break

    click.echo(f"\n批量完成: {success_count} 成功, {fail_count} 失败")
    return {
        "success_count": success_count,
        "fail_count": fail_count,
        "total_items": len(items),
        "completed_count": int(progress.get("completed_count", 0) or 0),
        "failed_indices": list(progress.get("failed_indices", []) or []),
        "items": list(progress.get("items", []) or []),
        "progress_file": progress_file,
        "workflow_policy": workflow_policy,
    }


@cli.command()
@click.option("--file", "-f", "batch_file", help="批量商品 JSON/XLSX 文件")
@click.option("--dir", "-d", "dir_path", help="包含多个商品 JSON 的目录")
@click.option("--stop-on-error", is_flag=True, help="遇到错误时停止")
@click.option("--plan-out", default="", help="可选：保存计划包的目录，每个商品自动生成 {task_id}.json")
@click.option("--resume", is_flag=True, help="从 progress-file 继续批量上架")
@click.option("--progress-file", default="data/batch-progress.json", help="批量进度文件路径")
@click.option("--start-from-phase", default="", help="批量模式下每个商品从指定 phase 开始")
def batch(batch_file, dir_path, stop_on_error, plan_out, resume, progress_file, start_from_phase):
    """批量发布商品。"""
    if batch_file:
        items = _load_batch_items(Path(batch_file))
    elif dir_path:
        items = []
        for json_file in sorted(Path(dir_path).glob("*.json")):
            try:
                items.extend(_load_batch_items(json_file))
            except Exception:
                continue
    else:
        click.echo("错误: 需要 --file 或 --dir", err=True)
        sys.exit(1)

    _prepare_runtime_services()
    summary = _run_batch_publish_items(
        items,
        stop_on_error=stop_on_error,
        plan_out=plan_out,
        resume=resume,
        progress_file=progress_file,
        start_from_phase=start_from_phase,
        workflow_policy="default",
    )
    if summary["fail_count"] > 0 and stop_on_error:
        sys.exit(1)


@cli.command("live-run")
@click.option("--file", "batch_file", default="湖南上架表格.xlsx", help="默认使用湖南上架表格.xlsx")
@click.option("--plan-out", default="", help="计划输出目录，默认写入 data/live-run-YYYY-MM-DD")
@click.option("--progress-file", default="", help="进度文件路径，默认写入计划目录下 progress.json")
@click.option("--resume", is_flag=True, help="从进度文件续跑")
@click.option("--start-from-phase", default="", help="从指定 phase 开始执行")
@click.option("--video-observer/--no-video-observer", default=False, help="启用多帧截图观察器")
def live_run(batch_file, plan_out, progress_file, resume, start_from_phase, video_observer):
    """按文档驱动模板执行 live-run，默认停在首个失败商品。"""
    batch_path = Path(batch_file)
    if not batch_path.exists():
        click.echo(f"错误: 文件不存在 {batch_file}", err=True)
        sys.exit(1)

    items = _load_batch_items(batch_path)
    if not items:
        click.echo("错误: 未解析到可上架商品", err=True)
        sys.exit(1)

    default_dir = Path("data") / f"live-run-{Path(batch_file).stem}"
    plan_dir = str((Path(plan_out) if plan_out else default_dir).resolve())
    progress_path = str((Path(progress_file) if progress_file else Path(plan_dir) / "progress.json").resolve())
    click.echo(
        f"live-run: file={batch_path.name} mode={items[0].get('publish_mode', 'single')} "
        f"items={len(items)} workflow=doc_strict"
    )
    _prepare_runtime_services({"VIDEO_OBSERVER_ENABLED": video_observer})

    summary = _run_batch_publish_items(
        items,
        stop_on_error=True,
        plan_out=plan_dir,
        resume=resume,
        progress_file=progress_path,
        start_from_phase=start_from_phase,
        workflow_policy="doc_strict",
        settings_overrides={"VIDEO_OBSERVER_ENABLED": video_observer},
    )
    if summary["fail_count"] > 0:
        sys.exit(1)


@cli.command("acceptance-run")
@click.option("--file", "batch_file", default="湖南上架表格.xlsx", help="验收表文件，默认湖南上架表格.xlsx")
@click.option("--plan-out", default="", help="验收计划目录，默认 data/acceptance-runs/<run_id>")
@click.option("--progress-file", default="", help="验收进度文件路径")
@click.option("--resume", is_flag=True, help="从 progress 文件继续验收")
@click.option("--start-from-phase", default="", help="从指定业务 phase 开始执行")
@click.option("--video-observer/--no-video-observer", default=True, help="启用多帧截图观察器")
def acceptance_run(batch_file, plan_out, progress_file, resume, start_from_phase, video_observer):
    """真实验收：湖南上架表格.xlsx -> 京麦发布，并将结果落库。"""
    batch_path = Path(batch_file)
    if not batch_path.exists():
        click.echo(f"错误: 文件不存在 {batch_file}", err=True)
        sys.exit(1)

    items = _load_batch_items(batch_path)
    if not items:
        click.echo("错误: 未解析到可上架商品", err=True)
        sys.exit(1)

    workflow_policy = "doc_strict"
    paths = _build_acceptance_run_paths(batch_file, plan_out=plan_out, progress_file=progress_file)
    db = _record_acceptance_run_start(paths, workflow_policy, total_items=len(items))
    from settings import get_settings

    db_preflight = _run_db_preflight(get_settings())
    db_preflight_file = _write_db_preflight(paths, db_preflight)
    _prepare_runtime_services({"VIDEO_OBSERVER_ENABLED": video_observer})
    click.echo(
        f"acceptance-run: run_id={paths['run_id']} file={batch_path.name} "
        f"items={len(items)} workflow={workflow_policy} video_observer={video_observer}"
    )
    click.echo(
        f"DB preflight: type={db_preflight.get('final_db_type')} reachable={db_preflight.get('reachable')} "
        f"create_tables={db_preflight.get('create_tables')} report={db_preflight_file}"
    )

    try:
        summary = _run_batch_publish_items(
            items,
            stop_on_error=True,
            plan_out=paths["plan_dir"],
            resume=resume,
            progress_file=paths["progress_file"],
            start_from_phase=start_from_phase,
            workflow_policy=workflow_policy,
            settings_overrides={"VIDEO_OBSERVER_ENABLED": video_observer},
        )
        summary_payload = {
            "run_id": paths["run_id"],
            "batch_file": paths["batch_file"],
            "workflow_policy": workflow_policy,
            "video_observer_enabled": video_observer,
            "plan_dir": paths["plan_dir"],
            "progress_file": paths["progress_file"],
            "summary_file": paths["summary_file"],
            "db_preflight": db_preflight,
            "db_preflight_file": db_preflight_file,
            "summary": summary,
            "progress": _read_batch_progress(paths["progress_file"]),
        }
        _write_acceptance_summary(paths["summary_file"], summary_payload)
        final_status = "success" if summary["fail_count"] == 0 else "failed"
        db.update_acceptance_run(
            paths["run_id"],
            status=final_status,
            success_count=summary["success_count"],
            fail_count=summary["fail_count"],
            total_items=summary["total_items"],
            summary=summary_payload,
            summary_file=paths["summary_file"],
            progress_file=paths["progress_file"],
            plan_dir=paths["plan_dir"],
        )
        click.echo(f"验收结果已落库: run_id={paths['run_id']} status={final_status}")
        click.echo(f"验收总结: {paths['summary_file']}")
        if summary["fail_count"] > 0:
            sys.exit(1)
    except Exception as exc:
        error_payload = {
            "run_id": paths["run_id"],
            "batch_file": paths["batch_file"],
            "workflow_policy": workflow_policy,
            "video_observer_enabled": video_observer,
            "db_preflight": db_preflight,
            "db_preflight_file": db_preflight_file,
            "error": str(exc),
        }
        _write_acceptance_summary(paths["summary_file"], error_payload)
        db.update_acceptance_run(
            paths["run_id"],
            status="failed",
            fail_count=1,
            total_items=len(items),
            summary=error_payload,
            error=str(exc),
            summary_file=paths["summary_file"],
            progress_file=paths["progress_file"],
            plan_dir=paths["plan_dir"],
        )
        raise


@cli.command()
@click.argument("url_arg", required=False, default="")
@click.option("--url", "-u", help="商品 URL")
@click.option("--output", "-o", default="", help="输出 JSON 文件路径")
@click.option("--no-save", is_flag=True, help="只抓取，不写入数据库")
def scrape(url_arg, url, output, no_save):
    """采集商品信息，并默认写入 Product 表。"""
    from scraper import JDScraper
    from settings import get_settings

    actual_url = url or url_arg
    if not actual_url:
        click.echo("错误: 需要 --url", err=True)
        sys.exit(1)

    product = JDScraper().scrape(actual_url)
    if not product.get("success"):
        click.echo(f"采集失败: {product.get('error')}", err=True)
        sys.exit(1)

    if output:
        Path(output).write_text(json.dumps(product, ensure_ascii=False, indent=2), encoding="utf-8")

    if not no_save:
        settings = get_settings()
        db = _build_db(settings)
        db.create_tables()
        saved = db.save_product(_build_product_model(product, source="scrape"))
        click.echo(f"已写入数据库: {saved.product_id}")

    if output:
        click.echo(f"采集完成: {output}")
    else:
        click.echo(json.dumps(product, ensure_ascii=False, indent=2))


@cli.command()
def actions():
    """列出所有已注册动作。"""
    from actions import ActionRegistry

    click.echo(ActionRegistry.summary())


@cli.command("tasks")
@click.option("--status", "-s", default=None, help="状态过滤")
@click.option("--limit", "-l", default=20, help="显示数量")
def list_tasks(status, limit):
    """查看任务列表。"""
    from settings import get_settings

    db = _build_db(get_settings())
    tasks = db.list_tasks(status=status, limit=limit)
    if not tasks:
        click.echo("暂无任务")
        return

    for task in tasks:
        click.echo(f"  {task.get('task_id', '?')} | {task.get('status', '?')} | {task.get('product_id', '?')}")


@cli.command()
@click.option("--file", "-f", help="导入商品 JSON 文件")
@click.option("--list", "-l", "list_products", is_flag=True, help="列出已导入商品")
def products(file, list_products):
    """商品数据管理。"""
    from settings import get_settings

    db = _build_db(get_settings())
    db.create_tables()

    if list_products:
        items = db.list_products(limit=50)
        if not items:
            click.echo("暂无商品")
            return
        for item in items:
            click.echo(f"  {item.get('product_id', '?')} | {item.get('status', '?')} | {(item.get('title') or '')[:30]}")
        return

    if file:
        payload = _read_json_file(Path(file))
        saved = db.save_product(_build_product_model(payload, source="manual"))
        click.echo(f"商品已保存: {saved.product_id} - {(saved.title or '')[:30]}")
        return

    click.echo("使用 --file 导入或 --list 列出")


@cli.command()
@click.argument("task_id", required=False, default="")
def status(task_id):
    """环境检查或查看任务状态。"""
    from settings import get_settings

    settings = get_settings()

    if task_id:
        db = _build_db(settings)
        task = db.get_task(task_id)
        if not task:
            click.echo(f"任务不存在: {task_id}")
            return

        click.echo(f"任务: {task.get('task_id', '?')}")
        click.echo(f"状态: {task.get('status', '?')}")
        click.echo(f"商品: {task.get('product_id', '?')}")
        for step in db.list_steps(task_id):
            click.echo(f"  步骤 {step.get('step_index', '?')}: {step.get('action_name', '?')} - {step.get('status', '?')}")
        return

    checks = {
        "数据库": False,
        "LLM (Ollama)": False,
        "LLM (vLLM)": False,
        "Milvus": False,
    }

    try:
        db = _build_db(settings)
        db.create_tables()
        checks["数据库"] = True
    except Exception:
        checks["数据库"] = False

    try:
        from llm.manager import LLMManager

        llm = LLMManager(settings)
        checks["LLM (Ollama)"] = llm.ollama.health_check()
        checks["LLM (vLLM)"] = llm.vllm.health_check()
    except Exception:
        checks["LLM (Ollama)"] = False
        checks["LLM (vLLM)"] = False

    try:
        from memory.long_term import LongTermMemory

        ltm = LongTermMemory(
            host=settings.MILVUS_HOST,
            port=settings.MILVUS_PORT,
            collection_name=settings.MILVUS_COLLECTION,
            dim=settings.MILVUS_DIM,
        )
        checks["Milvus"] = ltm.is_available()
    except Exception:
        checks["Milvus"] = False

    click.echo("京麦商品发布自动化 v2.0 - 环境检查")
    click.echo("=" * 40)
    for name, ok in checks.items():
        icon = "OK" if ok else "FAIL"
        click.echo(f"  {name}: {icon}")


@cli.group()
def db():
    """数据库管理。"""


@db.command("init")
def db_init():
    """初始化数据库。"""
    from init_db import init_db

    db_instance = init_db()
    click.echo(f"数据库初始化完成: {db_instance.db_type}")


@cli.command("init-db")
def init_db_cmd():
    """初始化数据库。"""
    from init_db import init_db

    db_instance = init_db()
    click.echo(f"数据库初始化完成: {db_instance.db_type}")


@cli.group()
def memory():
    """记忆管理。"""


@memory.command("cleanup")
def memory_cleanup():
    from memory.manager import MemoryManager

    stats = MemoryManager().cleanup()
    click.echo(f"清理完成: {stats}")


@memory.command("create")
@click.option("--content", "-c", required=True, help="记忆内容")
@click.option(
    "--type",
    "-t",
    "mem_type",
    default="working",
    type=click.Choice(["working", "short_term", "long_term"]),
    help="记忆类型",
)
@click.option("--importance", "-i", default=0.5, help="重要度 0.0-1.0")
def memory_create(content, mem_type, importance):
    from memory.base import MemoryType
    from memory.manager import MemoryManager

    mapping = {
        "working": MemoryType.WORKING,
        "short_term": MemoryType.SHORT_TERM,
        "long_term": MemoryType.LONG_TERM,
    }
    item_id = MemoryManager().remember(content, memory_type=mapping[mem_type], importance=importance)
    click.echo(f"记忆已创建: {item_id} ({mem_type})")


@memory.command("stats")
def memory_stats():
    from memory.manager import MemoryManager

    for key, value in MemoryManager().stats().items():
        click.echo(f"  {key}: {value}")


@memory.command("search")
@click.option("--query", "-q", required=True, help="搜索关键词")
@click.option("--top", "-t", default=5, help="返回数量")
def memory_search(query, top):
    from memory.manager import MemoryManager

    results = MemoryManager().recall(query, top_k=top)
    if not results:
        click.echo("无匹配记忆")
        return
    for item in results:
        click.echo(f"  [{item.type.value}] {item.content[:60]} (重要度 {item.importance})")


@memory.command("clear")
@click.option("--confirm", is_flag=True, help="确认清空工作记忆")
def memory_clear(confirm):
    from memory.manager import MemoryManager

    if not confirm:
        click.echo("使用 --confirm 确认清空工作记忆")
        return
    MemoryManager().clear_working()
    click.echo("工作记忆已清空")


if __name__ == "__main__":
    cli()
