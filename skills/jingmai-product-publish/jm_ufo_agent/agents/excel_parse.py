"""Excel 解析 Agent。"""

from __future__ import annotations

from jm_ufo_agent.agents.base import AgentContext
from jm_ufo_agent.agents.worker import WorkerAgent


class ExcelParseAgent(WorkerAgent):
    """负责解析上架 Excel 行。"""

    def __init__(self, handler=None):
        """初始化 Excel 解析 Agent。"""

        # handler 后续接入 openpyxl 解析。
        # 默认 dry-run 直接使用上下文商品。
        # 名称固定，便于 workflow 识别。
        super().__init__(name="excel_parse", handler=handler)

    async def parse_rows(self, context: AgentContext):
        """执行 dry-run Excel 解析。"""

        # Phase 2 不引入 openpyxl 依赖，保持基础包最小。
        # dry-run 使用 context.product 作为单行输入。
        # 后续真实解析应返回多行 ProductRecord 数据。
        result = await self.run(context)
        result.data.setdefault("rows", [context.product] if context.product else [])
        return result
