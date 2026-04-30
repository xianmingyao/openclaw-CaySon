"""
京麦商品发布自动化 - CLI 入口
"""
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

import click


def _read_json_file(path: Path) -> Any:
    """兼容普通 UTF-8 与 UTF-8 BOM。"""
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

        headers = [str(cell).strip() if cell is not None else "" for cell in rows[0]]
        mapped_headers = [_normalize_header(header) for header in headers]
        items: List[Dict[str, Any]] = []
        for row in rows[1:]:
            payload = {}
            for index, cell in enumerate(row):
                key = mapped_headers[index] if index < len(mapped_headers) else ""
                if not key or cell in (None, ""):
                    continue
                payload[key] = cell
            if payload:
                items.append(payload)
        return items

    raise ValueError(f"不支持的批量文件格式: {path.suffix}")


def _normalize_header(header: str) -> str:
    mapping = {
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
    }
    return mapping.get(header.strip(), header.strip())


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


@click.group()
@click.version_option(version="2.0.0", prog_name="jingmai")
def cli():
    """京麦商品发布自动化 v2.0"""


@cli.command()
@click.option("--config", "-c", "config_file", help="商品数据 JSON 文件路径")
@click.option("--data", "-d", help="商品数据 JSON 字符串")
def publish(config_file, data):
    """发布商品（规划 + 执行）"""
    from agents.factory import AgentFactory

    product_data = _load_product_data(config_file, data)
    factory = AgentFactory()

    planner = factory.create_planner()
    plan_result = planner.run(product_data=product_data)
    if not plan_result.get("success"):
        click.echo(f"规划失败: {plan_result.get('error')}", err=True)
        sys.exit(1)

    click.echo(f"规划完成: {plan_result['total_steps']} 步")
    executor = factory.create_executor()
    result = executor.run(plan=plan_result["plan"], task_id=plan_result["task_id"])

    if result["success"]:
        click.echo("发布成功")
        return

    click.echo(f"发布失败: {result.get('error')}", err=True)
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
    factory = AgentFactory()
    planner = factory.create_planner()
    result = planner.run(product_data=product_data, task_desc=task_desc)
    if result.get("success"):
        payload = result["plan"] if steps_only else {
            "task_id": result["task_id"],
            "product_data": result["product_data"],
            "plan": result["plan"],
            "total_steps": result["total_steps"],
        }
        click.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    click.echo(f"规划失败: {result.get('error')}", err=True)
    sys.exit(1)


@cli.command()
@click.option("--config", "-c", "config_file", required=True, help="计划 JSON 文件路径")
@click.option("--task-id", "-t", default="", help="任务 ID")
def execute(config_file, task_id):
    """执行已有计划文件。"""
    from agents.factory import AgentFactory

    plan_data = _read_json_file(Path(config_file))
    payload = _extract_plan_payload(plan_data)
    steps = payload["steps"]
    actual_task_id = task_id or payload["task_id"]
    if not steps:
        click.echo("执行失败: 计划文件中没有可执行步骤", err=True)
        sys.exit(1)
    factory = AgentFactory()
    result = factory.create_executor().run(plan=steps, task_id=actual_task_id)
    if result["success"]:
        if actual_task_id:
            click.echo(f"执行成功: task_id={actual_task_id}")
        else:
            click.echo("执行成功")
        return

    click.echo(f"执行失败: {result.get('error')}", err=True)
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
def batch(batch_file, dir_path, stop_on_error):
    """批量发布商品。"""
    from agents.factory import AgentFactory

    factory = AgentFactory()
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
    for index, product_data in enumerate(items, start=1):
        title = (_product_payload(product_data).get("title") or "?")[:30]
        click.echo(f"\n[{index}/{len(items)}] 处理: {title}")
        try:
            plan_result = factory.create_planner().run(product_data=product_data)
            if not plan_result.get("success"):
                click.echo(f"  规划失败: {plan_result.get('error')}")
                fail_count += 1
                if stop_on_error:
                    break
                continue

            exec_result = factory.create_executor().run(
                plan=plan_result["plan"],
                task_id=plan_result["task_id"],
            )
            if exec_result.get("success"):
                click.echo("  成功")
                success_count += 1
            else:
                click.echo(f"  失败: {exec_result.get('error')}")
                fail_count += 1
                if stop_on_error:
                    break
        except Exception as exc:
            click.echo(f"  异常: {exc}")
            fail_count += 1
            if stop_on_error:
                break

    click.echo(f"\n批量完成: {success_count} 成功, {fail_count} 失败")


@cli.command()
@click.argument("url_arg", required=False, default="")
@click.option("--url", "-u", help="商品 URL")
@click.option("--output", "-o", default="", help="输出 JSON 文件路径")
@click.option("--no-save", is_flag=True, help="只抓取，不写入数据库")
def scrape(url_arg, url, output, no_save):
    """采集商品信息，并默认写入 Product 表。"""
    from db import DatabaseManager
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
    from db import DatabaseManager
    from settings import get_settings

    settings = get_settings()
    db = _build_db(settings)
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
    from db import DatabaseManager
    from settings import get_settings

    settings = get_settings()
    db = _build_db(settings)
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
    from db import DatabaseManager
    from settings import get_settings

    settings = get_settings()

    # 有 task_id 参数时：查看任务执行状态
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

    # 无参数时：环境检查
    checks = {
        "数据库": False,
        "LLM (Ollama)": False,
        "Milvus": False,
    }

    # 检查数据库
    try:
        db = _build_db(settings)
        db.create_tables()
        checks["数据库"] = True
    except Exception:
        checks["数据库"] = False

    # 检查 LLM
    try:
        from llm.manager import LLMManager
        llm = LLMManager(settings)
        checks["LLM (Ollama)"] = llm.ollama.health_check()
        checks["LLM (vLLM)"] = llm.vllm.health_check()
    except Exception:
        checks["LLM (Ollama)"] = False
        checks["LLM (vLLM)"] = False

    # 检查 Milvus
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
@click.option("--query", "-q", required=True, help="搜索关键字")
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
