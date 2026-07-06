"""MySQL schema 显式应用工具。"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from jm_ufo_agent.core.settings import MySQLSettings
from jm_ufo_agent.storage.mysql import AsyncMySQLClient


class MySQLSchemaApplyNotConfirmedError(PermissionError):
    """未显式确认 schema 应用时抛出的安全错误。"""


@dataclass(frozen=True)
class MySQLSchemaApplyReport:
    """MySQL schema 应用报告。"""

    ok: bool
    schema_path: str
    statement_count: int
    applied_count: int
    errors: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """转换为 CLI JSON 输出。"""

        # statement_count 表示从 SQL 文件中解析出的语句数量。
        # applied_count 表示已经成功执行的语句数量。
        # errors 只记录错误类型和消息，不包含数据库密码。
        return {
            "ok": self.ok,
            "schema_path": self.schema_path,
            "statement_count": self.statement_count,
            "applied_count": self.applied_count,
            "errors": list(self.errors),
        }


async def apply_mysql_schema(
    settings: MySQLSettings,
    schema_path: str | Path,
    confirmed_apply: bool = False,
    mysql_client: AsyncMySQLClient | None = None,
) -> MySQLSchemaApplyReport:
    """显式应用 MySQL schema 文件。"""

    # 该函数会修改数据库结构，必须 confirmed_apply=True。
    # mysql_client 可注入 fake，测试不连接真实 MySQL。
    # 每条语句顺序执行，失败时停止并返回已执行数量。
    if not confirmed_apply:
        raise MySQLSchemaApplyNotConfirmedError("应用 MySQL schema 必须显式确认 confirmed_apply=True")
    path = Path(schema_path)
    statements = split_sql_statements(path.read_text(encoding="utf-8"))
    client = mysql_client or AsyncMySQLClient(settings)
    pool = await client.connect()
    applied_count = 0
    errors: list[dict[str, Any]] = []
    connection_cm = pool.acquire()
    async with connection_cm as connection:
        for statement in statements:
            try:
                await _execute(connection, statement)
                applied_count += 1
            except Exception as exc:
                errors.append({"error_type": exc.__class__.__name__, "error": str(exc), "statement_index": applied_count + 1})
                break
        await _commit_if_supported(connection)
    return MySQLSchemaApplyReport(
        ok=not errors and applied_count == len(statements),
        schema_path=str(path),
        statement_count=len(statements),
        applied_count=applied_count,
        errors=errors,
    )


def split_sql_statements(sql_text: str) -> list[str]:
    """把 schema SQL 文本拆成可执行语句。"""

    # 当前 schema 文件只使用普通 DDL，不包含存储过程，因此按分号拆分足够。
    # 注释行会被移除，避免 fake connection 和部分驱动误执行注释。
    # 空语句会被过滤，保持 statement_count 稳定。
    lines = []
    for raw_line in sql_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("--"):
            continue
        lines.append(raw_line)
    return [statement.strip() for statement in "\n".join(lines).split(";") if statement.strip()]


async def _execute(connection: Any, statement: str) -> Any:
    """兼容 fake connection 和真实 cursor 执行 SQL。"""

    # fake connection 可以直接实现 execute。
    # asyncmy 连接通常需要 cursor 上下文。
    # params 为空，因为 schema 文件不接受用户输入。
    if hasattr(connection, "execute"):
        return await connection.execute(statement, ())
    async with connection.cursor() as cursor:
        return await cursor.execute(statement)


async def _commit_if_supported(connection: Any) -> None:
    """在连接支持 commit 时提交事务。"""

    # DDL 在部分 MySQL 配置下会隐式提交，但显式 commit 更利于 fake 测试和兼容。
    # 没有 commit 方法时直接跳过。
    # 如果 commit 返回 awaitable，则等待完成。
    commit = getattr(connection, "commit", None)
    if commit is None:
        return
    result = commit()
    if hasattr(result, "__await__"):
        await result
