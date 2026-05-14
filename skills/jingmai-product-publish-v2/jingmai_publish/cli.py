"""命令行入口。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from jingmai_publish.bootstrap import init_database
from jingmai_publish.config import load_settings
from jingmai_publish.db.session import create_engine_from_settings, create_session_factory
from jingmai_publish.desktop import UIATuningConfig
from jingmai_publish.services import DesktopVerificationService
from jingmai_publish.services.import_pipeline import ImportPipelineService


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""

    parser = argparse.ArgumentParser(description="京麦桌面商品上架系统 CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_db_parser = subparsers.add_parser("init-db", help="初始化数据库表结构")
    init_db_parser.add_argument("--root", default=".", help="项目根目录，用于加载 .env")

    run_import_parser = subparsers.add_parser("run-import", help="读取 Excel 并创建上架任务")
    run_import_parser.add_argument("--excel", required=True, help="本地 Excel 文件路径")
    run_import_parser.add_argument("--mode", default="draft", choices=["draft", "publish"], help="任务模式")
    run_import_parser.add_argument("--store-id", default=None, help="店铺标识")
    run_import_parser.add_argument("--root", default=".", help="项目根目录，用于加载 .env")

    desktop_check_parser = subparsers.add_parser("run-desktop-check", help="执行真实京麦窗口 T1~T5 探针/验证")
    desktop_check_parser.add_argument("--step", default="both", choices=["t1", "t2", "t3", "t4", "t5-probe", "t5-input-probe", "both"], help="验证步骤")
    desktop_check_parser.add_argument("--debug", action="store_true", help="输出窗口枚举和候选控件调试信息")
    desktop_check_parser.add_argument("--window-keyword", action="append", default=[], help="窗口标题关键词，可多次传入")
    desktop_check_parser.add_argument("--preferred-class", action="append", default=[], help="控件类优先级，可多次传入")
    desktop_check_parser.add_argument(
        "--click-alias",
        action="append",
        default=[],
        help="点击文本别名，格式：目标文本=别名1,别名2",
    )
    desktop_check_parser.add_argument("--title", default=None, help="T4 用：商品标题")
    desktop_check_parser.add_argument("--model", default=None, help="T4 用：商品型号")
    desktop_check_parser.add_argument("--required-attr", default=None, help="T4 用：最小必填属性值")
    desktop_check_parser.add_argument("--brand", default=None, help="T4 用：品牌名称")
    desktop_check_parser.add_argument("--sku-cell-id", default=None, help="T5 输入实验用：目标单元格 automation_id")
    desktop_check_parser.add_argument("--sku-value", default=None, help="T5 输入实验用：写入值")
    desktop_check_parser.add_argument("--sku-submit", action="store_true", help="T5 输入实验用：输入后发送回车")
    desktop_check_parser.add_argument("--root", default=".", help="项目根目录，用于加载 .env")

    return parser


def handle_init_db(root: str) -> int:
    """执行数据库初始化。"""

    settings = load_settings(root)
    engine = create_engine_from_settings(settings)
    init_database(engine)
    print("数据库初始化完成")
    return 0


def handle_run_import(excel: str, mode: str, store_id: str | None, root: str) -> int:
    """执行导入主链路。"""

    settings = load_settings(root)
    engine = create_engine_from_settings(settings)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        pipeline = ImportPipelineService(session)
        result = pipeline.run_from_local_excel_path(
            excel_path=Path(excel),
            mode=mode,
            store_id=store_id,
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def _parse_click_aliases(raw_aliases: list[str]) -> dict[str, list[str]]:
    """解析命令行中的点击文本别名。"""

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
    window_keywords: list[str] | None = None,
    preferred_classes: list[str] | None = None,
    click_aliases: dict[str, list[str]] | None = None,
    title: str | None = None,
    model: str | None = None,
    required_attribute: str | None = None,
    brand: str | None = None,
    sku_cell_id: str | None = None,
    sku_value: str | None = None,
    sku_submit: bool = False,
) -> int:
    """执行真实京麦窗口的 T1~T5 实机验证。"""

    settings = load_settings(root)
    tuning = UIATuningConfig(
        window_keywords=window_keywords or ["京麦", "Jingmai"],
        preferred_classes=preferred_classes or ["Button", "MenuItem", "Hyperlink", "SplitButton"],
        click_text_aliases=click_aliases or {},
    )
    service = DesktopVerificationService(str(settings.screenshot_dir), tuning=tuning)
    result = service.run(
        step=step,
        debug=debug,
        title=title,
        model=model,
        required_attribute=required_attribute,
        brand=brand,
        sku_cell_id=sku_cell_id,
        sku_value=sku_value,
        sku_submit=sku_submit,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI 主入口。"""

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "init-db":
        return handle_init_db(args.root)

    if args.command == "run-import":
        return handle_run_import(args.excel, args.mode, args.store_id, args.root)

    if args.command == "run-desktop-check":
        return handle_run_desktop_check(
            args.step,
            args.root,
            args.debug,
            args.window_keyword,
            args.preferred_class,
            _parse_click_aliases(args.click_alias),
            args.title,
            args.model,
            args.required_attr,
            args.brand,
            args.sku_cell_id,
            args.sku_value,
            args.sku_submit,
        )

    parser.error(f"不支持的命令: {args.command}")
    return 2
