"""Command line entrypoints."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from jingmai_publish.bootstrap import init_database
from jingmai_publish.config import load_settings
from jingmai_publish.db.session import create_engine_from_settings, create_session_factory
from jingmai_publish.desktop import UIATuningConfig
from jingmai_publish.services import (
    DesktopVerificationService,
    FeishuPathChannelService,
    ImportPipelineService,
    LocalPathChannelService,
    RuntimeRetentionService,
)


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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="京麦桌面商品上架系统 CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_db_parser = subparsers.add_parser("init-db", help="初始化数据库表结构")
    init_db_parser.add_argument("--root", default=".", help="项目根目录")

    run_import_parser = subparsers.add_parser("run-import", help="读取 Excel 并创建上架任务")
    run_import_parser.add_argument("--excel", required=True, help="本地 Excel 文件路径")
    run_import_parser.add_argument("--mode", default="draft", choices=["draft", "publish"], help="任务模式")
    run_import_parser.add_argument("--store-id", default=None, help="店铺标识")
    run_import_parser.add_argument("--root", default=".", help="项目根目录")

    path_task_parser = subparsers.add_parser("run-local-path-task", help="从本地路径消息文件触发任务")
    path_task_parser.add_argument("--path-file", required=True, help="包含 Excel 本地路径的消息文件")
    path_task_parser.add_argument("--mode", default="draft", choices=["draft", "publish"], help="任务模式")
    path_task_parser.add_argument("--store-id", default=None, help="店铺标识")
    path_task_parser.add_argument("--source-channel", default="local_path_message", help="来源通道名")
    path_task_parser.add_argument("--root", default=".", help="项目根目录")

    feishu_task_parser = subparsers.add_parser("run-feishu-path-task", help="从飞书事件 payload 触发任务")
    feishu_task_parser.add_argument("--payload-file", required=True, help="Feishu/Lark 事件 payload JSON 文件")
    feishu_task_parser.add_argument("--mode", default="draft", choices=["draft", "publish"], help="任务模式")
    feishu_task_parser.add_argument("--store-id", default=None, help="店铺标识")
    feishu_task_parser.add_argument("--root", default=".", help="项目根目录")

    cleanup_parser = subparsers.add_parser("cleanup-runtime-logs", help="清理过期日志与截图")
    cleanup_parser.add_argument("--root", default=".", help="项目根目录")

    desktop_check_parser = subparsers.add_parser("run-desktop-check", help="执行 T1~T8 实机探针/闭环")
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
    desktop_check_parser.add_argument("--weight", default=None, help="T5/T7 重量")
    desktop_check_parser.add_argument("--length-mm", default=None, help="T5 长度")
    desktop_check_parser.add_argument("--width-mm", default=None, help="T5 宽度")
    desktop_check_parser.add_argument("--height-mm", default=None, help="T5 高度")
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
    desktop_check_parser.add_argument("--root", default=".", help="项目根目录")

    return parser


def handle_init_db(root: str) -> int:
    settings = load_settings(root)
    engine = create_engine_from_settings(settings)
    init_database(engine)
    print("数据库初始化完成")
    return 0


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

    if args.command == "init-db":
        return handle_init_db(args.root)
    if args.command == "run-import":
        return handle_run_import(args.excel, args.mode, args.store_id, args.root)
    if args.command == "run-local-path-task":
        return handle_run_local_path_task(args.path_file, args.mode, args.store_id, args.source_channel, args.root)
    if args.command == "run-feishu-path-task":
        return handle_run_feishu_path_task(args.payload_file, args.mode, args.store_id, args.root)
    if args.command == "cleanup-runtime-logs":
        return handle_cleanup_runtime_logs(args.root)
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
            weight=args.weight,
            length_mm=args.length_mm,
            width_mm=args.width_mm,
            height_mm=args.height_mm,
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
        )

    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
