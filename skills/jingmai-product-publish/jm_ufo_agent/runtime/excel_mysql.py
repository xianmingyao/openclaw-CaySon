"""Excel 到 MySQL 的显式生产导入入口。"""

from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from jm_ufo_agent.core.settings import MySQLSettings
from jm_ufo_agent.io.importer import ExcelImportSummary, ExcelProductImportService
from jm_ufo_agent.storage.mysql import AsyncMySQLClient
from jm_ufo_agent.storage.repositories.models import ProductRecord
from jm_ufo_agent.storage.repositories.products import ProductRepository


class MySQLWriteNotConfirmedError(PermissionError):
    """未显式确认 MySQL 写入时抛出的安全错误。"""


@dataclass(frozen=True)
class MySQLExcelImportReport:
    """Excel 写入 MySQL 后的读回验收报告。"""

    summary: ExcelImportSummary
    readback_count: int
    missing_readback_rows: list[int] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """转换为 CLI 可输出的 JSON 字典。"""

        # summary 保留原有解析/写入摘要，兼容 F01 已有验收字段。
        # readback_count 表示写入后能从 jm_products 按 row_index 读回的数量。
        # missing_readback_rows 非空时说明数据库写入或事务提交存在问题。
        payload = dict(self.summary.to_dict())
        payload["readback_count"] = self.readback_count
        payload["missing_readback_rows"] = list(self.missing_readback_rows)
        payload["readback_passed"] = not self.missing_readback_rows and self.readback_count == self.summary.written_count
        return payload


@dataclass(frozen=True)
class MySQLImportPreflightReport:
    """Excel 导入前的 MySQL 结构预检报告。"""

    ok: bool
    database: str
    products_table_exists: bool
    products_count: int | None = None
    message: str = ""
    error_type: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """转换为 CLI 可输出的 JSON 字典。"""

        # ok 表示当前数据库具备执行 F01 写入和读回的最低条件。
        # products_count 是只读查询结果，帮助判断表是否已经有历史数据。
        # error_type 不包含密码、host 等敏感连接细节。
        return {
            "ok": self.ok,
            "database": self.database,
            "products_table_exists": self.products_table_exists,
            "products_count": self.products_count,
            "message": self.message,
            "error_type": self.error_type,
        }


async def preflight_mysql_import_schema(settings: MySQLSettings, mysql_client: AsyncMySQLClient | None = None) -> MySQLImportPreflightReport:
    """只读检查 F01 需要的 MySQL schema 是否可用。"""

    # 该函数只执行 SHOW TABLES/COUNT，不写入任何业务数据。
    # mysql_client 可注入 fake，单元测试不需要真实数据库。
    # 真实连接失败时返回结构化报告，方便 CLI 和 dashboard 展示。
    client = mysql_client or AsyncMySQLClient(settings)
    try:
        pool = await client.connect()
        connection_cm = pool.acquire()
        async with connection_cm as connection:
            table_row = await _fetchone(connection, "SHOW TABLES LIKE %s", ("jm_products",))
            exists = table_row is not None
            count = None
            if exists:
                count_row = await _fetchone(connection, "SELECT COUNT(*) FROM jm_products", ())
                count = _first_int(count_row)
            return MySQLImportPreflightReport(
                ok=exists,
                database=settings.database,
                products_table_exists=exists,
                products_count=count,
                message="jm_products 可用" if exists else "缺少 jm_products 表",
            )
    except Exception as exc:
        return MySQLImportPreflightReport(
            ok=False,
            database=settings.database,
            products_table_exists=False,
            message=f"MySQL 预检失败: {exc}",
            error_type=exc.__class__.__name__,
        )


async def import_excel_to_mysql(
    xlsx_path: str | Path,
    settings: MySQLSettings,
    sheet_name: str | None = None,
    confirmed_write: bool = False,
    mysql_client: AsyncMySQLClient | None = None,
    service: ExcelProductImportService | None = None,
) -> ExcelImportSummary:
    """解析 Excel 并写入真实 MySQL。"""

    # 这是 F01 的真实写入边界，默认不允许执行，必须显式 confirmed_write=True。
    # mysql_client 和 service 都支持注入，单元测试可以不用连接真实 MySQL。
    # 函数只写 jm_products，不启动京东、京麦或任何桌面自动化能力。
    if not confirmed_write:
        raise MySQLWriteNotConfirmedError("写入 MySQL 必须显式确认 confirmed_write=True")

    client = mysql_client or AsyncMySQLClient(settings)
    importer = service or ExcelProductImportService()
    pool = await client.connect()
    connection_cm = pool.acquire()
    async with connection_cm as connection:
        repository = ProductRepository(connection)
        summary = await importer.import_file(xlsx_path, repository=repository, sheet_name=sheet_name)
        await _commit_if_supported(connection)
        return summary


async def import_excel_to_mysql_with_readback(
    xlsx_path: str | Path,
    settings: MySQLSettings,
    sheet_name: str | None = None,
    confirmed_write: bool = False,
    mysql_client: AsyncMySQLClient | None = None,
    service: ExcelProductImportService | None = None,
) -> MySQLExcelImportReport:
    """解析 Excel、写入 MySQL，并按 row_index 读回验收。"""

    # 该函数比 import_excel_to_mysql 多一步 readback，专门服务 F01 真实 MySQL 验收。
    # 为了读回所有 row，这里先解析出 records，再逐条 upsert，避免只验证 first_rows。
    # 仍然要求 confirmed_write=True，防止误连生产数据库。
    if not confirmed_write:
        raise MySQLWriteNotConfirmedError("写入 MySQL 必须显式确认 confirmed_write=True")

    client = mysql_client or AsyncMySQLClient(settings)
    importer = service or ExcelProductImportService()
    records = importer.parser.parse(xlsx_path, sheet_name=sheet_name)
    pool = await client.connect()
    connection_cm = pool.acquire()
    async with connection_cm as connection:
        repository = ProductRepository(connection)
        written_count = 0
        for record in records:
            await repository.upsert(record)
            written_count += 1
        await _commit_if_supported(connection)
        missing_rows = await _missing_readback_rows(repository, records)
    summary = ExcelImportSummary(
        source_path=str(xlsx_path),
        parsed_count=len(records),
        written_count=written_count,
        generated_id_rows=[record.row_index for record in records if record.product_id == f"row_{record.row_index}"],
        first_rows=[_record_preview(record) for record in records[:5]],
    )
    return MySQLExcelImportReport(summary=summary, readback_count=written_count - len(missing_rows), missing_readback_rows=missing_rows)


async def _missing_readback_rows(repository: ProductRepository, records: list[ProductRecord]) -> list[int]:
    """检查写入后哪些 Excel 行无法从 MySQL 读回。"""

    # 按 row_index 读回，直接对应 F01 的“product 表行数等于 xlsx 实际行数”。
    # 只返回缺失行号，不把完整商品数据输出到日志里。
    # 读回失败会抛出原始数据库异常，调用方据此 halt 或人工处理。
    missing: list[int] = []
    for record in records:
        stored = await repository.get_by_row(record.row_index)
        if stored is None:
            missing.append(record.row_index)
    return missing


def _record_preview(record: ProductRecord) -> dict[str, object]:
    """生成导入报告中的轻量商品预览。"""

    # 该 helper 和 ExcelProductImportService 的 preview 字段保持一致。
    # 避免为了 readback 报告暴露 raw_data 全量 Excel 内容。
    # 只输出人工核对最需要的 row/product_id/title。
    return {"row_index": record.row_index, "product_id": record.product_id, "title": record.title}


async def _commit_if_supported(connection: Any) -> None:
    """在底层连接支持 commit 时提交事务。"""

    # asyncmy 连接默认可能需要显式 commit，fake connection 也可以提供该方法供测试断言。
    # 不强制所有连接实现 commit，避免破坏已有 fake repository 测试。
    # 如果 commit 返回 awaitable，则等待它完成，确保 CLI 返回前写入已落盘。
    commit = getattr(connection, "commit", None)
    if commit is None:
        return
    result = commit()
    if inspect.isawaitable(result):
        await result


async def _fetchone(connection: Any, sql: str, params: tuple[Any, ...]) -> Any:
    """兼容 fake connection 和真实 cursor 的单行查询。"""

    # fake connection 可以直接实现 fetchone，测试更轻量。
    # asyncmy 连接通常需要 cursor 上下文，这里做统一兼容。
    # 查询异常不吞掉，由 preflight 转成结构化报告。
    if hasattr(connection, "fetchone"):
        return await connection.fetchone(sql, params)
    async with connection.cursor() as cursor:
        await cursor.execute(sql, params)
        return await cursor.fetchone()


def _first_int(row: Any) -> int | None:
    """从数据库 COUNT 查询结果中提取整数。"""

    # 不同驱动可能返回 tuple、list 或 dict。
    # 提取失败时返回 None，不把计数解析问题误判为表不存在。
    # dict 优先取第一个 value，兼容 DictCursor。
    if row is None:
        return None
    if isinstance(row, dict):
        values = list(row.values())
        return int(values[0]) if values else None
    if isinstance(row, (tuple, list)):
        return int(row[0]) if row else None
    return int(row)
