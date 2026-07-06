"""VLM 调用审计 Repository。"""

from __future__ import annotations

from jm_ufo_agent.storage.repositories.base import SQLRepository
from jm_ufo_agent.storage.repositories.models import VlmCallRecord


class VlmCallRepository(SQLRepository):
    """写入 `jm_vlm_calls` 表。"""

    async def add(self, record: VlmCallRecord) -> None:
        """追加一条 VLM 调用记录。"""

        # VLM 调用成本高，必须记录类型、模型、耗时和 token。
        # cache_hit 用 0/1 写入，兼容 MySQL TINYINT(1)。
        # metadata_json 保存错误、图片 hash、prompt 摘要等审计信息。
        await self.execute(
            """
            INSERT INTO jm_vlm_calls (
                task_id, row_index, call_type, model, prompt_tokens, completion_tokens,
                latency_ms, status, cache_hit, metadata_json
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                record.task_id,
                record.row_index,
                record.call_type,
                record.model,
                record.prompt_tokens,
                record.completion_tokens,
                record.latency_ms,
                record.status,
                1 if record.cache_hit else 0,
                self.dumps_json(record.metadata),
            ),
        )
