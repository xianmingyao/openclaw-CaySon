"""
京麦商品发布自动化 - CLI 入口
"""
import inspect
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import click


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
        return data if isinstance(data, list) else [data]

    if suffix in {".xlsx", ".xlsm"}:
        from openpyxl import load_workbook

        workbook = load_workbook(path, read_only=True, data_only=True)
        sheet = workbook.active
        rows = list(sheet.iter_rows(values_only=True))
        if not rows:
            return []

        header_index = _detect_header_row_index(rows)
        headers = [str(cell).strip() if cell is not None else "" for cell in rows[header_index]]
        mapped_headers = [_normalize_header(header) for header in headers]
        items: List[Dict[str, Any]] = []
        for row in rows[header_index + 1 :]:
            payload: Dict[str, Any] = {}
            for index, cell in enumerate(row):
                key = mapped_headers[index] if index < len(mapped_headers) else ""
                if not key or cell in (None, ""):
                    continue
                payload[key] = cell
            if "jd_price" in payload:
                payload.setdefault("price", payload["jd_price"])
                payload.setdefault("market_price", payload["jd_price"])
            if payload:
                items.append(payload)
        return items

    raise ValueError(f"不支持的批量文件格式: {path.suffix}")


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
    category = src.get("category", "")
    return Product(
        product_id=str(src.get("product_id", src.get("sku", ""))),
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
        raw_data=product_data,
    )


def _build_db(settings):
    from db import DatabaseManager

    return DatabaseManager(mysql_url=settings.MYSQL_URL, sqlite_url=settings.SQLITE_URL)


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
            "total_steps": int(plan_data.get("total_steps", len(steps)) or len(steps)),
        }

    raise ValueError("计划文件格式无效")


def _build_plan_package(plan_result: Dict[str, Any]) -> Dict[str, Any]:
    plan_steps = plan_result["plan"]
    return {
        "task_id": plan_result["task_id"],
        "product_data": plan_result["product_data"],
        "plan": plan_steps,
        "total_steps": plan_result["total_steps"],
        "phases": _summarize_plan_phases(plan_steps),
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
) -> Dict[str, Any]:
    from agents.factory import AgentFactory

    factory = AgentFactory()
    planner = factory.create_planner()
    plan_result = planner.run(product_data=product_data)
    if not plan_result.get("success"):
        return {"success": False, "stage": "plan", "error": plan_result.get("error", "规划失败")}

    plan_package = _build_plan_package(plan_result)
    plan_file_path = _resolve_plan_output_path(plan_out, plan_result["task_id"])
    plan_path = Path(plan_file_path)
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(json.dumps(plan_package, ensure_ascii=False, indent=2), encoding="utf-8")
    plan_file = str(plan_path.resolve())

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
def publish(config_file, data, plan_out, start_from_phase):
    """发布商品（默认主入口：Plan-and-Solve → ReAct → Reflection）"""
    product_data = _load_product_data(config_file, data)
    result = _run_publish_flow(
        product_data=product_data,
        plan_out=plan_out,
        progress_prefix="  ",
        start_from_phase=start_from_phase,
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
def plan(task_desc, config_file, data, steps_only):
    """仅生成执行计划，不执行。"""
    from agents.factory import AgentFactory

    product_data = _load_product_data(config_file, data) if (config_file or data) else {}
    planner = AgentFactory().create_planner()
    result = planner.run(product_data=product_data, task_desc=task_desc)
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

    success_count = 0
    fail_count = 0
    total_high_risk_count = 0
    products_with_recovery_error = 0
    total_vision_fallback_count = 0
    total_successful_vision_fallback_count = 0
    total_failed_vision_fallback_count = 0
    products_with_vision_fallback = 0
    template_hit_totals: Dict[str, int] = {}
    template_success_totals: Dict[str, int] = {}
    template_failed_totals: Dict[str, int] = {}
    risky_titles: List[str] = []
    batch_plan_dir = Path(plan_out).resolve() if plan_out else None
    progress = _read_batch_progress(progress_file)
    start_index = int(progress.get("completed_count", 0) or 0) if resume else 0

    if start_index > 0:
        click.echo(f"批量续跑：从第 {start_index + 1} 个商品开始")

    for index, product_data in enumerate(items, start=1):
        if index <= start_index:
            continue
        title = (_product_payload(product_data).get("title") or "?")[:30]
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
            )
            task_id = exec_result.get("task_id", "")
            if batch_plan_dir is not None and task_id:
                final_path = _resolve_plan_output_path(str(batch_plan_dir), task_id, treat_as_dir=True)
                interim_path = Path(item_plan_out)
                if interim_path.exists() and str(interim_path.resolve()) != final_path:
                    Path(final_path).write_text(interim_path.read_text(encoding="utf-8"), encoding="utf-8")
                    interim_path.unlink()

            risk_count = int((exec_result.get("risk_stats") or {}).get("high_risk_window_shift_count", 0) or 0)
            recovery_error = exec_result.get("recovery_error", "")
            vision_stats = exec_result.get("vision_fallback_stats") or {}
            vision_count = int(vision_stats.get("count", 0) or 0)
            successful_vision_count = int(vision_stats.get("success_count", 0) or 0)
            failed_vision_count = int(vision_stats.get("failed_count", 0) or 0)
            template_hits = vision_stats.get("templates") or {}
            template_success_hits = vision_stats.get("templates_success") or {}
            template_failed_hits = vision_stats.get("templates_failed") or {}
            failed_vision_details = vision_stats.get("failed_details") or []
            total_high_risk_count += risk_count
            if recovery_error:
                products_with_recovery_error += 1
            total_vision_fallback_count += vision_count
            total_successful_vision_fallback_count += successful_vision_count
            total_failed_vision_fallback_count += failed_vision_count
            if vision_count > 0:
                products_with_vision_fallback += 1
            for template_name, count in template_hits.items():
                template_hit_totals[template_name] = template_hit_totals.get(template_name, 0) + int(count or 0)
            for template_name, count in template_success_hits.items():
                template_success_totals[template_name] = template_success_totals.get(template_name, 0) + int(count or 0)
            for template_name, count in template_failed_hits.items():
                template_failed_totals[template_name] = template_failed_totals.get(template_name, 0) + int(count or 0)
            if risk_count > 0 or recovery_error:
                risk_reasons = []
                if risk_count > 0:
                    risk_reasons.append(f"{risk_count}次高风险漂移")
                if recovery_error:
                    risk_reasons.append("有恢复错误")
                risky_titles.append(f"{title}（{'，'.join(risk_reasons)}）")

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
                        "start_from_phase": exec_result.get("start_from_phase", ""),
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
                        "error": exec_result.get("error", ""),
                        "failed_step": exec_result.get("failed_step", 0),
                        "start_from_phase": exec_result.get("start_from_phase", ""),
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
                    "error": str(exc),
                    "failed_step": 0,
                    "start_from_phase": _normalize_phase_name(start_from_phase) if start_from_phase else "",
                }
            )
            _write_batch_progress(progress_file, progress)
            if stop_on_error:
                break

    click.echo(
        f"\n批量完成: {success_count} 成功, {fail_count} 失败, "
        f"{total_high_risk_count} 次高风险窗口漂移, "
        f"{products_with_recovery_error} 个商品出现恢复错误, "
        f"{products_with_vision_fallback} 个商品触发视觉兜底, "
        f"{total_vision_fallback_count} 次视觉兜底"
        f"（成功 {total_successful_vision_fallback_count} / 失败 {total_failed_vision_fallback_count}）"
    )
    if risky_titles:
        click.echo("高风险商品: " + "；".join(risky_titles))
    if template_hit_totals:
        template_summary = "；".join(
            f"{name} {count}次"
            for name, count in sorted(template_hit_totals.items(), key=lambda item: (-item[1], item[0]))
        )
        click.echo("视觉兜底模板统计: " + template_summary)
    if template_success_totals or template_failed_totals:
        success_summary = "；".join(
            f"{name} {count}次"
            for name, count in sorted(template_success_totals.items(), key=lambda item: (-item[1], item[0]))
        ) or "无"
        failed_summary = "；".join(
            f"{name} {count}次"
            for name, count in sorted(template_failed_totals.items(), key=lambda item: (-item[1], item[0]))
        ) or "无"
        click.echo(f"视觉兜底结果: 成功[{success_summary}]；失败[{failed_summary}]")


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
