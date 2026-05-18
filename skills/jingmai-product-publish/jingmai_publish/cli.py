"""Command line entrypoints."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError

from jingmai_publish.bootstrap import init_database
from jingmai_publish.config import ConfigValidationError, load_settings, validate_settings
from jingmai_publish.db.session import create_engine_from_settings, create_session_factory
from jingmai_publish.desktop import UIATuningConfig
from jingmai_publish.services import (
    DesktopVerificationService,
    DraftE2EOptions,
    DraftE2EOrchestrator,
    FeishuPathChannelService,
    ImportPipelineService,
    LocalPathChannelService,
    RuntimeRetentionService,
    ScreenshotEvidenceService,
)

logger = logging.getLogger(__name__)

DESKTOP_STEPS = [
    "t1",
    "t2",
    "t3",
    "t4",
    "t4-extra",
    "t4-option-probe",
    "t5-probe",
    "t5-input-probe",
    "t5-row-probe",
    "t5-market-probe",
    "t5-first-row",
    "t5-required-fields",
    "t5-dimension-probe",
    "t5-weight-probe",
    "t6-probe",
    "t6-dialog-probe",
    "t6-main-image",
    "t6-transparent-image",
    "t6-detail-editor",
    "t7",
    "t8-probe",
    "t8-save-draft",
    "t8-publish-product",
    "both",
]


def _add_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--verbose", action="store_true", help="输出详细日志")
    parser.add_argument("--log-file", default=None, help="将日志写入指定文件")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="京麦桌面商品上架系统 CLI")
    _add_common_options(parser)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_db_parser = subparsers.add_parser("init-db", help="初始化数据库表结构")
    _add_common_options(init_db_parser)
    init_db_parser.add_argument("--root", default=".", help="项目根目录")

    config_parser = subparsers.add_parser("check-config", help="校验当前配置")
    _add_common_options(config_parser)
    config_parser.add_argument("--root", default=".", help="项目根目录")

    run_import_parser = subparsers.add_parser("run-import", help="读取 Excel 并创建上架任务")
    _add_common_options(run_import_parser)
    run_import_parser.add_argument("--excel", required=True, help="本地 Excel 文件路径")
    run_import_parser.add_argument("--mode", default="draft", choices=["draft", "publish"], help="任务模式")
    run_import_parser.add_argument("--store-id", default=None, help="店铺标识")
    run_import_parser.add_argument("--root", default=".", help="项目根目录")

    path_task_parser = subparsers.add_parser("run-local-path-task", help="从本地路径消息文件触发任务")
    _add_common_options(path_task_parser)
    path_task_parser.add_argument("--path-file", required=True, help="包含 Excel 本地路径的消息文件")
    path_task_parser.add_argument("--mode", default="draft", choices=["draft", "publish"], help="任务模式")
    path_task_parser.add_argument("--store-id", default=None, help="店铺标识")
    path_task_parser.add_argument("--source-channel", default="local_path_message", help="来源通道名")
    path_task_parser.add_argument("--root", default=".", help="项目根目录")

    feishu_task_parser = subparsers.add_parser("run-feishu-path-task", help="从飞书事件 payload 触发任务")
    _add_common_options(feishu_task_parser)
    feishu_task_parser.add_argument("--payload-file", required=True, help="Feishu/Lark 事件 payload JSON 文件")
    feishu_task_parser.add_argument("--mode", default="draft", choices=["draft", "publish"], help="任务模式")
    feishu_task_parser.add_argument("--store-id", default=None, help="店铺标识")
    feishu_task_parser.add_argument("--root", default=".", help="项目根目录")

    cleanup_parser = subparsers.add_parser("cleanup-runtime-logs", help="清理过期日志与截图")
    _add_common_options(cleanup_parser)
    cleanup_parser.add_argument("--root", default=".", help="项目根目录")

    evidence_parser = subparsers.add_parser("check-evidence", help="检查 runtime 截图证据是否存在")
    _add_common_options(evidence_parser)
    evidence_parser.add_argument("--root", default=".", help="项目根目录")

    draft_e2e_parser = subparsers.add_parser("run-draft-e2e", help="从 Excel 单行执行到京麦保存草稿")
    _add_common_options(draft_e2e_parser)
    draft_e2e_parser.add_argument("--excel", required=True, help="本地 Excel 文件路径")
    draft_e2e_parser.add_argument("--item-index", type=int, default=0, help="导入结果中的商品索引，默认第一条")
    draft_e2e_parser.add_argument("--store-id", default=None, help="店铺标识")
    draft_e2e_parser.add_argument("--required-attr", default=None, help="T4 最小必填属性值")
    draft_e2e_parser.add_argument("--current", default=None, help="T5 SKU 电流")
    draft_e2e_parser.add_argument("--factory-inventory", default=None, help="T5 厂直库存")
    draft_e2e_parser.add_argument("--main-image-path", required=True, help="T6 主图本地路径")
    draft_e2e_parser.add_argument("--transparent-image-path", required=True, help="T6 透图本地路径")
    draft_e2e_parser.add_argument("--detail-content", default=None, help="T6 详情内容")
    draft_e2e_parser.add_argument("--detail-content-file", default=None, help="T6 详情内容文件")
    draft_e2e_parser.add_argument("--rated-voltage", default=None, help="T4 扩展项：额定电压")
    draft_e2e_parser.add_argument("--cable-length", default=None, help="T4 扩展项：电缆长度")
    draft_e2e_parser.add_argument("--sale-unit", default=None, help="T7 销售单位")
    draft_e2e_parser.add_argument("--package-type", default="普通商品", help="T7 商品包装")
    draft_e2e_parser.add_argument("--delivery-mark", default="普通品", help="T7 特殊发货时效标记")
    draft_e2e_parser.add_argument("--package-list", default=None, help="T7 包装清单")
    draft_e2e_parser.add_argument("--warranty-period", default="365", help="T7 质保期")
    draft_e2e_parser.add_argument("--debug", action="store_true", help="输出调试信息")
    draft_e2e_parser.add_argument("--window-keyword", action="append", default=[], help="窗口标题关键词")
    draft_e2e_parser.add_argument("--preferred-class", action="append", default=[], help="控件类优先级")
    draft_e2e_parser.add_argument(
        "--click-alias",
        action="append",
        default=[],
        help="点击文本别名，格式：目标文本=别名1,别名2",
    )
    draft_e2e_parser.add_argument("--root", default=".", help="项目根目录")

    desktop_check_parser = subparsers.add_parser("run-desktop-check", help="执行 T1~T8 实机探针/闭环")
    _add_common_options(desktop_check_parser)
    desktop_check_parser.add_argument("--step", default="both", choices=DESKTOP_STEPS, help="验证步骤")
    desktop_check_parser.add_argument("--debug", action="store_true", help="输出调试信息")
    desktop_check_parser.add_argument("--window-keyword", action="append", default=[], help="窗口标题关键词")
    desktop_check_parser.add_argument("--preferred-class", action="append", default=[], help="控件类优先级")
    desktop_check_parser.add_argument(
        "--click-alias",
        action="append",
        default=[],
        help="点击文本别名，格式：目标文本=别名1,别名2",
    )
    desktop_check_parser.add_argument("--title", default=None, help="T4 商品标题")
    desktop_check_parser.add_argument("--model", default=None, help="T4 商品型号")
    desktop_check_parser.add_argument("--required-attr", default=None, help="T4 最小必填属性值")
    desktop_check_parser.add_argument("--brand", default=None, help="T4 品牌")
    desktop_check_parser.add_argument("--sku-cell-id", default=None, help="T5 单元格 automation_id")
    desktop_check_parser.add_argument("--sku-value", default=None, help="T5 写入值")
    desktop_check_parser.add_argument("--sku-submit", action="store_true", help="T5 输入后回车")
    desktop_check_parser.add_argument("--sku-name", default=None, help="T5 SKU 名称")
    desktop_check_parser.add_argument("--short-title", default=None, help="T5 短标题")
    desktop_check_parser.add_argument("--market-price", default=None, help="T5 市场价")
    desktop_check_parser.add_argument("--purchase-price", default=None, help="T5 采购价")
    desktop_check_parser.add_argument("--jd-price", default=None, help="T5 京东价")
    desktop_check_parser.add_argument("--current", default=None, help="T5 SKU 电流")
    desktop_check_parser.add_argument("--weight", default=None, help="T5/T7 重量")
    desktop_check_parser.add_argument("--stock", default=None, help="T5 SKU 库存")
    desktop_check_parser.add_argument("--length-mm", default=None, help="T5 长度")
    desktop_check_parser.add_argument("--width-mm", default=None, help="T5 宽度")
    desktop_check_parser.add_argument("--height-mm", default=None, help="T5 高度")
    desktop_check_parser.add_argument("--factory-inventory", default=None, help="T5 厂直库存")
    desktop_check_parser.add_argument("--rated-voltage", default=None, help="T4 扩展项：额定电压")
    desktop_check_parser.add_argument("--cable-length", default=None, help="T4 扩展项：电缆长度")
    desktop_check_parser.add_argument("--sale-unit", default=None, help="T7 销售单位")
    desktop_check_parser.add_argument("--package-type", default=None, help="T7 商品包装")
    desktop_check_parser.add_argument("--delivery-mark", default=None, help="T7 特殊发货时效标记")
    desktop_check_parser.add_argument("--package-list", default=None, help="T7 包装清单")
    desktop_check_parser.add_argument("--warranty-period", default=None, help="T7 质保期")
    desktop_check_parser.add_argument("--image-path", default=None, help="T6 主图或通用图片路径")
    desktop_check_parser.add_argument("--transparent-image-path", default=None, help="T6 透图路径")
    desktop_check_parser.add_argument("--detail-content", default=None, help="T6 详情内容")
    desktop_check_parser.add_argument("--detail-html", default=None, help="T6 详情 HTML 内容")
    desktop_check_parser.add_argument("--detail-content-file", default=None, help="T6 详情 HTML/文本文件")
    desktop_check_parser.add_argument("--jd-item-url", default=None, help="T6 从京东商品链接抓取图文详情")
    desktop_check_parser.add_argument(
        "--confirm-publish",
        action="store_true",
        help="明确允许执行正式发布。仅 t8-publish-product 生效；缺省会被发布守卫拦截。",
    )
    desktop_check_parser.add_argument("--root", default=".", help="项目根目录")

    return parser


def configure_logging(verbose: bool = False, log_file: str | None = None) -> None:
    """初始化 CLI 日志输出。"""

    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stderr)]
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_path, encoding="utf-8"))
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=handlers,
        force=True,
    )


def handle_init_db(root: str) -> int:
    settings = load_settings(root)
    engine = create_engine_from_settings(settings)
    init_database(engine)
    print("数据库初始化完成")
    return 0


def handle_check_config(root: str) -> int:
    settings = load_settings(root)
    errors = validate_settings(settings)
    result = {
        "success": not errors,
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "errors": errors,
        "paths": {
            "log_dir": str(settings.log_dir),
            "memory_dir": str(settings.memory_dir),
            "screenshot_dir": str(settings.screenshot_dir),
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


def handle_run_import(excel: str, mode: str, store_id: str | None, root: str) -> int:
    settings = load_settings(root)
    engine = create_engine_from_settings(settings)
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        pipeline = ImportPipelineService(session)
        result = pipeline.run_from_local_excel_path(excel_path=Path(excel), mode=mode, store_id=store_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def handle_run_local_path_task(
        path_file: str,
        mode: str,
        store_id: str | None,
        source_channel: str,
        root: str,
) -> int:
    settings = load_settings(root)
    engine = create_engine_from_settings(settings)
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        service = LocalPathChannelService(session)
        result = service.run_from_local_message(
            path_file,
            mode=mode,
            store_id=store_id,
            source_channel=source_channel,
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def handle_run_feishu_path_task(
        payload_file: str,
        mode: str,
        store_id: str | None,
        root: str,
) -> int:
    settings = load_settings(root)
    engine = create_engine_from_settings(settings)
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        service = FeishuPathChannelService(session)
        result = service.run_from_feishu_payload(payload_file, mode=mode, store_id=store_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def handle_cleanup_runtime_logs(root: str) -> int:
    settings = load_settings(root)
    engine = create_engine_from_settings(settings)
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        service = RuntimeRetentionService(session, settings.screenshot_dir)
        result = service.cleanup()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def handle_check_evidence(root: str) -> int:
    service = ScreenshotEvidenceService(root)
    result = service.collect()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["success"] else 1


def handle_run_draft_e2e(
        *,
        excel: str,
        item_index: int,
        store_id: str | None,
        required_attr: str | None,
        current: str | None,
        factory_inventory: str | None,
        main_image_path: str,
        transparent_image_path: str,
        detail_content: str | None,
        detail_content_file: str | None,
        rated_voltage: str | None,
        cable_length: str | None,
        sale_unit: str | None,
        package_type: str,
        delivery_mark: str,
        package_list: str | None,
        warranty_period: str,
        debug: bool,
        window_keywords: list[str],
        preferred_classes: list[str],
        click_aliases: dict[str, list[str]],
        root: str,
) -> int:
    settings = load_settings(root)
    engine = create_engine_from_settings(settings)
    session_factory = create_session_factory(engine)
    tuning = UIATuningConfig(
        window_keywords=window_keywords or ["京麦", "Jingmai"],
        preferred_classes=preferred_classes or ["Button", "MenuItem", "Hyperlink", "SplitButton"],
        click_text_aliases=click_aliases,
    )
    with session_factory() as session:
        orchestrator = DraftE2EOrchestrator(session, screenshot_dir=str(settings.screenshot_dir), tuning=tuning)
        try:
            result = orchestrator.run(
                DraftE2EOptions(
                    excel_path=excel,
                    item_index=item_index,
                    store_id=store_id,
                    required_attr=required_attr,
                    current=current,
                    factory_inventory=factory_inventory,
                    main_image_path=main_image_path,
                    transparent_image_path=transparent_image_path,
                    detail_content=detail_content,
                    detail_content_file=detail_content_file,
                    rated_voltage=rated_voltage,
                    cable_length=cable_length,
                    sale_unit=sale_unit,
                    package_type=package_type,
                    delivery_mark=delivery_mark,
                    package_list=package_list,
                    warranty_period=warranty_period,
                    debug=debug,
                )
            )
        except SQLAlchemyError as exc:
            result = {
                "success": False,
                "mode": "draft",
                "error": {
                    "code": "database_error",
                    "message": str(exc),
                    "hint": "请先确认数据库已初始化；开发环境可运行 `python cli.py init-db --root .`。",
                },
            }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("success") else 1


def _parse_click_aliases(raw_aliases: list[str]) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    for raw in raw_aliases:
        if "=" not in raw:
            continue
        target, alias_part = raw.split("=", 1)
        aliases = [item.strip() for item in alias_part.split(",") if item.strip()]
        mapping[target.strip()] = aliases
    return mapping


def handle_run_desktop_check(
        step: str,
        root: str,
        debug: bool = False,
        **kwargs,
) -> int:
    settings = load_settings(root)
    tuning = UIATuningConfig(
        window_keywords=kwargs.pop("window_keywords", None) or ["京麦", "Jingmai"],
        preferred_classes=kwargs.pop("preferred_classes", None) or ["Button", "MenuItem", "Hyperlink", "SplitButton"],
        click_text_aliases=kwargs.pop("click_aliases", None) or {},
    )
    service = DesktopVerificationService(str(settings.screenshot_dir), tuning=tuning)
    result = service.run(step=step, debug=debug, **kwargs)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(bool(getattr(args, "verbose", False)), getattr(args, "log_file", None))

    try:
        if args.command == "init-db":
            return handle_init_db(args.root)
        if args.command == "check-config":
            return handle_check_config(args.root)
        if args.command == "run-import":
            return handle_run_import(args.excel, args.mode, args.store_id, args.root)
        if args.command == "run-local-path-task":
            return handle_run_local_path_task(args.path_file, args.mode, args.store_id, args.source_channel, args.root)
        if args.command == "run-feishu-path-task":
            return handle_run_feishu_path_task(args.payload_file, args.mode, args.store_id, args.root)
        if args.command == "cleanup-runtime-logs":
            return handle_cleanup_runtime_logs(args.root)
        if args.command == "check-evidence":
            return handle_check_evidence(args.root)
        if args.command == "run-draft-e2e":
            return handle_run_draft_e2e(
                excel=args.excel,
                item_index=args.item_index,
                store_id=args.store_id,
                required_attr=args.required_attr,
                current=args.current,
                factory_inventory=args.factory_inventory,
                main_image_path=args.main_image_path,
                transparent_image_path=args.transparent_image_path,
                detail_content=args.detail_content,
                detail_content_file=args.detail_content_file,
                rated_voltage=args.rated_voltage,
                cable_length=args.cable_length,
                sale_unit=args.sale_unit,
                package_type=args.package_type,
                delivery_mark=args.delivery_mark,
                package_list=args.package_list,
                warranty_period=args.warranty_period,
                debug=args.debug,
                window_keywords=args.window_keyword,
                preferred_classes=args.preferred_class,
                click_aliases=_parse_click_aliases(args.click_alias),
                root=args.root,
            )
        if args.command == "run-desktop-check":
            return handle_run_desktop_check(
                args.step,
                args.root,
                args.debug,
                window_keywords=args.window_keyword,
                preferred_classes=args.preferred_class,
                click_aliases=_parse_click_aliases(args.click_alias),
                title=args.title,
                model=args.model,
                required_attribute=args.required_attr,
                brand=args.brand,
                sku_cell_id=args.sku_cell_id,
                sku_value=args.sku_value,
                sku_submit=args.sku_submit,
                sku_name=args.sku_name,
                short_title=args.short_title,
                market_price=args.market_price,
                purchase_price=args.purchase_price,
                jd_price=args.jd_price,
                current=args.current,
                weight=args.weight,
                stock=args.stock,
                length_mm=args.length_mm,
                width_mm=args.width_mm,
                height_mm=args.height_mm,
                factory_inventory=args.factory_inventory,
                rated_voltage=args.rated_voltage,
                cable_length=args.cable_length,
                sale_unit=args.sale_unit,
                package_type=args.package_type,
                delivery_mark=args.delivery_mark,
                package_list=args.package_list,
                warranty_period=args.warranty_period,
                image_path=args.image_path,
                transparent_image_path=args.transparent_image_path,
                detail_content=args.detail_content,
                detail_html=args.detail_html,
                detail_content_file=args.detail_content_file,
                jd_item_url=args.jd_item_url,
                confirm_publish=args.confirm_publish,
            )
    except ConfigValidationError as exc:
        logger.error("配置校验失败: %s", exc)
        print(json.dumps({"success": False, "error": {"code": "config_error", "message": str(exc)}}, ensure_ascii=False,
                         indent=2))
        return 2
    except ValueError as exc:
        logger.error("命令执行失败: %s", exc)
        print(json.dumps({"success": False, "error": {"code": "validation_error", "message": str(exc)}},
                         ensure_ascii=False, indent=2))
        return 2

    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
