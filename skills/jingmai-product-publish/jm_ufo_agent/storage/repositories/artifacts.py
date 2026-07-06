"""执行证据 Repository。"""

from __future__ import annotations

from jm_ufo_agent.storage.repositories.base import SQLRepository
from jm_ufo_agent.storage.repositories.models import ArtifactRecord


class ArtifactRepository(SQLRepository):
    """读写 `jm_artifacts` 表。"""

    async def add(self, record: ArtifactRecord) -> None:
        """追加一条截图/OCR/页面签名证据。"""

        # artifacts 是只追加证据表，不做覆盖。
        # 真实截图文件放在 artifact_dir，这里只保存路径和元数据。
        # metadata_json 记录 OCR 摘要、窗口标题等轻量信息。
        await self.execute(
            """
            INSERT INTO jm_artifacts (task_id, row_index, artifact_type, storage_path, metadata_json)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (record.task_id, record.row_index, record.artifact_type, record.storage_path, self.dumps_json(record.metadata)),
        )
