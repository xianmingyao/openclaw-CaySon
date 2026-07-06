"""命令行入口 — 集成 CLI 调用、进度展示和交互式 dashboard。"""

from __future__ import annotations

import argparse
import asyncio
import json
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from jm_ufo_agent.agents.base import AgentContext
from jm_ufo_agent.backends.ufo_adapter import UfoImportBackend, Win32WindowInspectorBackend
from jm_ufo_agent.backends.ufo_capabilities import UfoCapabilityScanner
from jm_ufo_agent.backends.web_surface import ScreenshotOcrService, TesseractOcrProvider
from jm_ufo_agent.backends.webview_backend import WebViewBackendConfig, run_webview_act
from jm_ufo_agent.core.settings import load_settings
from jm_ufo_agent.io.importer import ExcelProductImportService
from jm_ufo_agent.runtime.app import run_dryrun
from jm_ufo_agent.runtime.excel_mysql import import_excel_to_mysql_with_readback, preflight_mysql_import_schema
from jm_ufo_agent.runtime.halt_evidence import HaltEvidenceCollector
from jm_ufo_agent.runtime.mysql_schema import apply_mysql_schema
from jm_ufo_agent.runtime.production import ProductionRunConfig, assert_production_allowed, assess_production_readiness
from jm_ufo_agent.runtime.review import preflight_minimax_review_scorer
from jm_ufo_agent.runtime.small_batch import validate_small_batch_payload


# ---------------------------------------------------------------------------
# 进度展示组件（原 jm_ufo_agent/cli/progress.py）
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DashboardState:
    """Dashboard 展示状态。"""

    task_id: str
    row_index: int
    current_node: str
    status: str
    completion_score: float = 0.0
    verified_fields: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    evidence: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_graph_state(cls, state: Any) -> "DashboardState":
        """从 GraphState 或 state dict 构造展示状态。"""

        # CLI 可能拿到 GraphState 对象，也可能拿到 JSON 字典。
        # 统一转换后，文本 dashboard 和 Rich dashboard 共用同一份数据。
        # status 兼容 Enum 和普通字符串。
        payload = state.to_dict() if hasattr(state, "to_dict") else dict(state)
        status = payload.get("status", "")
        if hasattr(status, "value"):
            status = status.value
        return cls(
            task_id=str(payload.get("task_id", "")),
            row_index=int(payload.get("row_index", 0)),
            current_node=str(payload.get("current_node", "")),
            status=str(status),
            completion_score=float(payload.get("completion_score", 0.0)),
            verified_fields=list(payload.get("verified_fields") or []),
            blockers=list(payload.get("blockers") or []),
            evidence=dict(payload.get("evidence") or {}),
        )


class ProgressDashboard:
    """Rich dashboard 渲染器。"""

    def render_text(self, state: DashboardState) -> str:
        """渲染为纯文本 dashboard。"""

        # 纯文本输出是无依赖兜底，适合 CI 和 Windows 控制台。
        # 每个字段单独一行，便于日志检索。
        # blockers 只展示数量和内容，不展开全部 evidence。
        lines = [
            f"task_id: {state.task_id}",
            f"row_index: {state.row_index}",
            f"status: {state.status}",
            f"current_node: {state.current_node}",
            f"completion_score: {state.completion_score:.2f}",
            f"verified_fields: {len(state.verified_fields)}",
            f"blockers: {'; '.join(state.blockers) if state.blockers else '-'}",
        ]
        return "\n".join(lines)

    def render(self, state: DashboardState) -> str:
        """渲染 dashboard，并在可用时使用 Rich。"""

        # rich 是可选依赖，项目当前不强制安装。
        # 如果 rich 不存在，返回纯文本，不影响 CLI 使用。
        # 这里返回字符串而不是直接 print，方便单元测试。
        try:
            from rich.console import Console
            from rich.table import Table
        except Exception:
            return self.render_text(state)

        console = Console(record=True, width=100)
        table = Table(title="jm_ufo_agent progress")
        table.add_column("Field")
        table.add_column("Value")
        for key, value in {
            "task_id": state.task_id,
            "row_index": state.row_index,
            "status": state.status,
            "current_node": state.current_node,
            "completion_score": f"{state.completion_score:.2f}",
            "verified_fields": str(len(state.verified_fields)),
            "blockers": "; ".join(state.blockers) if state.blockers else "-",
        }.items():
            table.add_row(str(key), str(value))
        console.print(table)
        return console.export_text(clear=False)


# ---------------------------------------------------------------------------
# 交互式 dashboard 入口（原 jm_ufo_agent/cli/interactive.py）
# ---------------------------------------------------------------------------

def render_dashboard(state) -> str:
    """渲染一次 dashboard。"""

    # 目前交互模式先提供单次快照渲染。
    # 后续接入真实运行时事件流后，可以在这里扩展 live refresh。
    # 返回字符串便于 CLI 打印和测试断言。
    return ProgressDashboard().render(DashboardState.from_graph_state(state))


def render_live_dashboard(states) -> str:
    """渲染多帧 dashboard，模拟实时进度流。"""

    # 真实运行时接入后，states 可以来自 async event stream 或 checkpoint 轮询。
    # 当前实现把多帧状态渲染为连续文本，适合 CLI JSONL 回放和单元测试。
    # 每一帧都复用 ProgressDashboard，避免单帧和实时视图展示字段不一致。
    dashboard = ProgressDashboard()
    frames: list[str] = []
    for index, state in enumerate(states, start=1):
        frames.append(f"frame: {index}")
        frames.append(dashboard.render(DashboardState.from_graph_state(state)).rstrip())
    return "\n".join(frames)


async def stream_dashboard_from_jsonl(
    states_jsonl: str | Path,
    poll_interval_sec: float = 1.0,
    max_frames: int | None = None,
    printer: Callable[[str], None] | None = None,
    use_rich_live: bool = False,
) -> int:
    """持续读取 JSONL 状态流并实时渲染 dashboard。"""

    # 这是 F13 的实时 TUI 边界：生产进程只要持续追加 JSONL 状态即可被 dashboard 跟随。
    # printer 可注入，测试时收集输出；CLI 运行时默认直接 print。
    # max_frames 为 None 时持续跟随；测试和脚本验收可传入有限帧数避免阻塞。
    path = Path(states_jsonl)
    emit = printer or print
    dashboard = ProgressDashboard()
    seen_lines = 0
    rendered_frames = 0
    live = _start_rich_live(use_rich_live and printer is None)
    try:
        while max_frames is None or rendered_frames < max_frames:
            if path.exists():
                lines = path.read_text(encoding="utf-8-sig").splitlines()
                for line in lines[seen_lines:]:
                    if not line.strip():
                        seen_lines += 1
                        continue
                    payload = json.loads(line)
                    if not isinstance(payload, dict):
                        raise ValueError("JSONL 每行必须是 object")
                    rendered_frames += 1
                    rendered = dashboard.render(DashboardState.from_graph_state(payload)).rstrip()
                    if live is not None:
                        live.update(rendered)
                    else:
                        emit(f"frame: {rendered_frames}")
                        emit(rendered)
                    seen_lines += 1
                    if max_frames is not None and rendered_frames >= max_frames:
                        return rendered_frames
            await asyncio.sleep(max(0.0, poll_interval_sec))
        return rendered_frames
    finally:
        if live is not None:
            live.stop()


def _start_rich_live(enabled: bool):
    """按需启动 Rich Live 渲染器。"""

    # Rich 是可选依赖；缺失时返回 None，调用方自动走文本输出。
    # 只在真实 CLI 输出时启用，测试 printer 注入时不启动交互 UI。
    # 返回对象只依赖 update/stop 两个方法，降低和 Rich 版本的耦合。
    if not enabled:
        return None
    try:
        from rich.live import Live
    except Exception:
        return None
    live = Live("", refresh_per_second=4, transient=False)
    live.start()
    return live


# ---------------------------------------------------------------------------
# CLI 命令定义与分发
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """构造 CLI 参数解析器。"""

    # argparse 是标准库，避免为命令行入口额外引入 Typer/Click 依赖。
    # 所有会触达真实京麦窗口的能力都挂在 run 的安全门控之后。
    # dry-run 保持旧入口，避免已有脚本和测试被破坏。
    parser = argparse.ArgumentParser(prog="jm-ufo-agent")
    subparsers = parser.add_subparsers(dest="command", required=True)

    dryrun = subparsers.add_parser("dry-run", help="运行单行商品 dry-run 工作流")
    dryrun.add_argument("--task-id", required=True)
    dryrun.add_argument("--row-index", type=int, required=True)
    dryrun.add_argument("--product-json", required=True)

    run = subparsers.add_parser("run", help="按文档入口启动任务，默认使用 dry-run backend")
    run.add_argument("--task-id", required=True)
    run.add_argument("--row-index", type=int, default=82)
    run.add_argument("--product-json", default="{}")
    run.add_argument("--backend", choices=["dry-run", "ufo-observe", "webview-act"], default="dry-run")
    run.add_argument("--confirm-real-jingmai", action="store_true")
    run.add_argument("--observe-only", action=argparse.BooleanOptionalAction, default=True)
    run.add_argument("--artifact-dir", default="artifacts")
    run.add_argument("--use-tesseract", action="store_true")

    dashboard = subparsers.add_parser("dashboard", help="渲染一次 Rich/text 进度面板")
    dashboard.add_argument("--state-json", required=True)

    live_dashboard = subparsers.add_parser("live-dashboard", help="从 JSONL 状态流渲染多帧进度面板")
    live_dashboard.add_argument("--states-jsonl", required=True)

    tail_dashboard = subparsers.add_parser("tail-dashboard", help="实时跟随 JSONL 状态流并渲染 dashboard")
    tail_dashboard.add_argument("--states-jsonl", required=True)
    tail_dashboard.add_argument("--poll-interval-sec", type=float, default=1.0)
    tail_dashboard.add_argument("--max-frames", type=int, default=None)
    tail_dashboard.add_argument("--rich-live", action="store_true")

    inspect_ufo = subparsers.add_parser("inspect-ufo", help="检查本机 UFO v1 可适配源码路径")
    inspect_ufo.add_argument("--ufo-root", default="E:/PY/UFO/ufo")

    subparsers.add_parser("inspect-jingmai-window", help="只读枚举京麦窗口技术事实，不点击、不输入")

    capture_halt = subparsers.add_parser("capture-halt-evidence", help="只读采集京麦现场 halt evidence")
    capture_halt.add_argument("--task-id", required=True)
    capture_halt.add_argument("--row-index", type=int, required=True)
    capture_halt.add_argument("--node", default="MANUAL_CHECK")
    capture_halt.add_argument("--reason", default="manual_capture")
    capture_halt.add_argument("--artifact-dir", default="artifacts")
    capture_halt.add_argument("--use-tesseract", action="store_true")

    import_excel = subparsers.add_parser("import-excel", help="解析真实 xlsx 并输出批量导入验收摘要")
    import_excel.add_argument("--xlsx", required=True)
    import_excel.add_argument("--sheet-name", default=None)
    import_excel.add_argument("--write-mysql", action="store_true")
    import_excel.add_argument("--confirm-write-mysql", action="store_true")
    import_excel.add_argument("--env-file", default=".env")

    readiness = subparsers.add_parser("production-readiness", help="根据能力开关评估真实 E2E 是否可启动")
    readiness.add_argument("--capabilities-json", required=True)

    small_batch = subparsers.add_parser("validate-small-batch", help="校验 row5-row7 草稿闭环证据，全部通过才允许进入 row82")
    small_batch.add_argument("--evidence-json", required=True)

    minimax_preflight = subparsers.add_parser("minimax-preflight", help="explicitly preflight MiniMax-M3 /models")
    minimax_preflight.add_argument("--env-file", default=".env")

    mysql_preflight = subparsers.add_parser("mysql-preflight", help="只读检查 Excel 导入需要的 MySQL schema")
    mysql_preflight.add_argument("--env-file", default=".env")

    mysql_schema = subparsers.add_parser("mysql-apply-schema", help="显式应用 MySQL schema 文件")
    mysql_schema.add_argument("--env-file", default=".env")
    mysql_schema.add_argument("--schema", default="jm_ufo_agent/storage/schema/mysql.sql")
    mysql_schema.add_argument("--confirm-apply-schema", action="store_true")

    crawl_jd = subparsers.add_parser("crawl-jd", help="抓取京东商品数据（标题、价格、图片URL）")
    crawl_jd.add_argument("--jd-url", required=True, help="京东商品页 URL")
    crawl_jd.add_argument("--cookie", default="", help="可选 Cookie，用于登录后抓取")
    crawl_jd.add_argument("--jd-html", default=None, help="本地 HTML 文件路径，跳过网络抓取直接解析")

    download_images = subparsers.add_parser("download-images", help="下载商品图片到本地")
    download_images.add_argument("--product-json", required=True, help="包含 image_urls 的商品 JSON")
    download_images.add_argument("--output-dir", default="artifacts/images", help="图片输出目录")
    download_images.add_argument("--max-retries", type=int, default=3, help="单张图片最大重试次数")

    return parser


def main(argv: list[str] | None = None) -> int:
    """执行 CLI。"""

    # main 只做参数分发，真实工作流仍在 runtime 层中组织。
    # 输出统一使用 JSON 或文本 dashboard，方便 CI、PowerShell 和人工复制查看。
    # 真实 backend 目前只允许 observe-only，防止误点京麦生产窗口。
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "dry-run":
        product: dict[str, Any] = _load_json_object(args.product_json)
        state = asyncio.run(run_dryrun(task_id=args.task_id, row_index=args.row_index, product=product))
        print(json.dumps(state.to_dict(), ensure_ascii=False, sort_keys=True))
        return 0

    if args.command == "run":
        assert_production_allowed(
            ProductionRunConfig(
                backend=args.backend,
                confirmed_real_jingmai=args.confirm_real_jingmai,
                observe_only=args.observe_only,
            )
        )
        product = _load_json_object(args.product_json)
        if args.backend == "webview-act":
            # webview-act走 PyAutoGui +剪贴板 + OCR闭环。
            # production.py 已限定 webview-act 为唯一可写白名单。
            # field_coords从 product.fallback_coord 取（run_webview_act内部提取）。
            config = WebViewBackendConfig(
                allow_write=not args.observe_only,
                field_coords={},
                artifact_dir=Path(args.artifact_dir),
                use_tesseract=args.use_tesseract,
            )
            payload = asyncio.run(
                run_webview_act(
                    task_id=args.task_id,
                    row_index=args.row_index,
                    product=product,
                    config=config,
                )
            )
            payload["runtime_backend"] = args.backend
            print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
            return 0
        state = asyncio.run(run_dryrun(task_id=args.task_id, row_index=args.row_index, product=product))
        payload = state.to_dict()
        payload["runtime_backend"] = args.backend
        payload["observe_only"] = args.observe_only
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return 0

    if args.command == "dashboard":
        state_payload = _load_json_object(args.state_json)
        print(render_dashboard(state_payload))
        return 0

    if args.command == "live-dashboard":
        states = _load_jsonl_objects(args.states_jsonl)
        print(render_live_dashboard(states))
        return 0

    if args.command == "tail-dashboard":
        # tail 模式面向真实运行时状态流，默认持续跟随 JSONL 文件。
        # --max-frames 可让 CI 或人工验收跑有限帧后退出。
        # 该命令只读状态文件，不触发任何京麦、京东或 MiniMax 操作。
        asyncio.run(
            stream_dashboard_from_jsonl(
                args.states_jsonl,
                poll_interval_sec=args.poll_interval_sec,
                max_frames=args.max_frames,
                use_rich_live=args.rich_live,
            )
        )
        return 0

    if args.command == "inspect-ufo":
        backend = UfoImportBackend(Path(args.ufo_root))
        report = UfoCapabilityScanner(Path(args.ufo_root)).scan()
        payload = {
            "ufo_root": str(backend.ufo_root),
            "ufo_root_exists": backend.ufo_root.exists(),
            "source_files": backend.source_files(),
            "capability_report": report.to_dict(),
        }
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return 0

    if args.command == "inspect-jingmai-window":
        facts = asyncio.run(Win32WindowInspectorBackend().inspect_jingmai())
        print(json.dumps({"found": facts.found, "main_title": facts.main_title, "main_class_name": facts.main_class_name, "qt_child_count": facts.qt_child_count, **facts.webview_summary()}, ensure_ascii=False, sort_keys=True))
        return 0

    if args.command == "capture-halt-evidence":
        # 该命令只读窗口事实、截图和可选 OCR，不执行点击、输入或保存草稿。
        # --use-tesseract 是显式开关，缺少 OCR 依赖时会在 evidence 中暴露错误。
        # artifact-dir 由用户指定，方便把现场证据归档到当前任务目录。
        backend = Win32WindowInspectorBackend()
        ocr_service = None
        if args.use_tesseract:
            screenshot_path = Path(args.artifact_dir) / args.task_id / f"row{args.row_index}_{args.node}_ocr.png"
            ocr_service = ScreenshotOcrService(TesseractOcrProvider(backend, screenshot_path))
        collector = HaltEvidenceCollector(
            artifact_dir=Path(args.artifact_dir),
            window_backend=backend,
            ocr_service=ocr_service,
        )
        evidence = asyncio.run(collector.collect(args.task_id, args.row_index, args.node, args.reason))
        print(json.dumps(evidence, ensure_ascii=False, sort_keys=True))
        return 0

    if args.command == "import-excel":
        if args.write_mysql:
            # 真实 MySQL 写入必须通过两个显式开关，避免把解析验收误当成生产导入。
            # 配置从 env-file 读取，不在命令行中暴露数据库密码。
            # 该分支只写 Excel 商品表，不启动京东抓取或京麦桌面操作。
            settings = load_settings(args.env_file)
            summary = asyncio.run(
                import_excel_to_mysql_with_readback(
                    args.xlsx,
                    settings.mysql,
                    sheet_name=args.sheet_name,
                    confirmed_write=args.confirm_write_mysql,
                )
            )
            payload = summary.to_dict()
            payload["dry_run"] = False
            payload["repository"] = "mysql"
            print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
            return 0
        summary = asyncio.run(ExcelProductImportService().import_file(args.xlsx, sheet_name=args.sheet_name))
        payload = summary.to_dict()
        payload["dry_run"] = True
        payload["repository"] = None
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return 0

    if args.command == "production-readiness":
        capabilities = {key: bool(value) for key, value in _load_json_object(args.capabilities_json).items()}
        print(json.dumps(assess_production_readiness(capabilities).to_dict(), ensure_ascii=False, sort_keys=True))
        return 0

    if args.command == "validate-small-batch":
        payload = _load_json_object(args.evidence_json)
        report = validate_small_batch_payload(payload)
        print(json.dumps(report.to_dict(), ensure_ascii=False, sort_keys=True))
        return 0

    if args.command == "minimax-preflight":
        # 该命令是显式生产前检查入口；只有用户主动调用时才访问 MiniMax /models。
        # 配置从 .env 读取，避免把 API key 写入命令行历史或测试代码。
        # 输出不包含 Authorization header，防止凭证出现在日志里。
        settings = load_settings(args.env_file)
        report = asyncio.run(preflight_minimax_review_scorer(settings.review_scorer))
        print(json.dumps(report.to_dict(), ensure_ascii=False, sort_keys=True))
        return 0

    if args.command == "mysql-preflight":
        # 只读预检 MySQL schema，不写入 Excel 商品数据。
        # 真实连接只有用户显式运行该命令时才发生。
        # 输出不包含数据库密码，便于复制到验收记录。
        settings = load_settings(args.env_file)
        report = asyncio.run(preflight_mysql_import_schema(settings.mysql))
        print(json.dumps(report.to_dict(), ensure_ascii=False, sort_keys=True))
        return 0

    if args.command == "mysql-apply-schema":
        # 该命令会修改数据库结构，必须显式传入 --confirm-apply-schema。
        # schema 路径默认指向项目内 DDL，调用方也可以传入审核后的文件。
        # 输出只包含执行数量和错误摘要，不打印数据库密码。
        settings = load_settings(args.env_file)
        report = asyncio.run(
            apply_mysql_schema(
                settings.mysql,
                args.schema,
                confirmed_apply=args.confirm_apply_schema,
            )
        )
        print(json.dumps(report.to_dict(), ensure_ascii=False, sort_keys=True))
        return 0

    if args.command == "crawl-jd":
        # 抓取京东商品数据。--jd-html 跳过网络，--jd-url + transport 走真实抓取。
        # cookie 为空时不注入，避免空凭证写进证据。
        from jm_ufo_agent.agents.jd_crawler import (
            CookieJdTransport,
            JdCrawlerAgent,
            JdPageParser,
            RateLimitedJdTransport,
            RetryingJdTransport,
            UrlopenJdTransport,
        )

        product = {"jd_url": args.jd_url}
        context = AgentContext(task_id="crawl-jd", product=product)

        if args.jd_html:
            # 本地 HTML 直接解析，不访问网络。
            html = Path(args.jd_html).read_text(encoding="utf-8-sig")
            product["jd_html"] = html
            agent = JdCrawlerAgent()
        else:
            # 构造 transport 链：限速 → 重试 → Cookie → urllib。
            inner = UrlopenJdTransport()
            if args.cookie:
                inner = CookieJdTransport(inner, cookie=args.cookie)
            transport = RateLimitedJdTransport(RetryingJdTransport(inner, max_attempts=3, delay_sec=1.0), min_interval_sec=0.5)
            agent = JdCrawlerAgent(transport=transport)

        result = asyncio.run(agent.crawl(context))
        print(json.dumps(result.data, ensure_ascii=False, sort_keys=True))
        return 0

    if args.command == "download-images":
        # 下载商品图片到本地目录。image_urls 来自商品 JSON 的 image_urls 或 sub_images 字段。
        from jm_ufo_agent.agents.image_fetch import ImageFetchAgent, RetryingImageDownloader, UrlopenImageDownloader

        product = _load_json_object(args.product_json)
        output_dir = Path(args.output_dir)
        downloader = RetryingImageDownloader(
            UrlopenImageDownloader(output_dir),
            max_attempts=args.max_retries,
            delay_sec=1.0,
        )
        agent = ImageFetchAgent(downloader=downloader)
        context = AgentContext(task_id="download-images", product=product)
        result = asyncio.run(agent.fetch(context))
        print(json.dumps(result.data, ensure_ascii=False, sort_keys=True))
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


def _load_json_object(value: str) -> dict[str, Any]:
    """读取 JSON object。"""

    # Windows PowerShell 对命令行 JSON 引号很容易二次处理。
    # 三种来源都支持：
    # 1. "@path.json" — 显式从文件读，utf-8-sig 兼容 Windows BOM。
    # 2. 裸路径且文件存在 — 自动从文件读，避免用户必须加 @ 前缀。
    # 3. inline JSON 字符串 — 仍按原行为解析。
    if value.startswith("@"):
        text = Path(value[1:]).read_text(encoding="utf-8-sig")
    elif Path(value).exists():
        text = Path(value).read_text(encoding="utf-8-sig")
    else:
        text = value
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("JSON 参数必须是 object")
    return data


def _load_product_json(value: str) -> dict[str, Any]:
    """兼容旧测试和旧脚本的商品 JSON 读取入口。"""

    # 旧版 CLI 只暴露 _load_product_json，已有测试和脚本可能直接导入。
    # 新版内部统一使用 _load_json_object，避免 state-json/product-json 各写一套解析。
    # 保留该薄封装可以让命令行重构不影响外部调用者。
    return _load_json_object(value)


def _load_jsonl_objects(path: str) -> list[dict[str, Any]]:
    """读取 JSONL 状态流文件。"""

    # live-dashboard 用 JSONL 表示多帧状态，每行一帧。
    # 空行会被跳过，方便人工编辑和日志拼接。
    # 每一行都必须是 JSON object，否则立即报错，避免 dashboard 展示半坏数据。
    rows: list[dict[str, Any]] = []
    for line in Path(path).read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        data = json.loads(line)
        if not isinstance(data, dict):
            raise ValueError("JSONL 每行必须是 object")
        rows.append(data)
    return rows


if __name__ == "__main__":
    raise SystemExit(main())
