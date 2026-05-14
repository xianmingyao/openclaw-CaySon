"""任务导入入口服务。"""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import uuid

from jingmai_publish.repositories.runtime_log import RuntimeLogRepository
from jingmai_publish.repositories.upload_job import UploadJobRepository


class TaskIngressService:
    """负责接收本地文件路径并创建导入批次。"""

    def __init__(
        self,
        upload_job_repo: UploadJobRepository,
        runtime_log_repo: RuntimeLogRepository,
    ) -> None:
        """注入导入仓库和日志仓库。"""

        self.upload_job_repo = upload_job_repo
        self.runtime_log_repo = runtime_log_repo

    @staticmethod
    def calculate_file_sha256(file_path: str | Path) -> str:
        """计算文件内容哈希，用于导入批次去重与追踪。"""

        path = Path(file_path)
        digest = sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def create_job_from_local_path(self, excel_path: str | Path, session_id: str) -> str:
        """根据本地 Excel 路径创建导入批次。"""

        path = Path(excel_path)
        if not path.exists():
            raise FileNotFoundError(f"Excel 文件不存在: {path}")

        job_id = f"job-{uuid.uuid4().hex[:12]}"
        file_sha256 = self.calculate_file_sha256(path)
        self.upload_job_repo.create_job(
            job_id=job_id,
            source_type="local_path",
            source_file_path=str(path),
            source_file_name=path.name,
            file_sha256=file_sha256,
            business_type=None,
        )
        self.runtime_log_repo.append_log(
            session_id=session_id,
            task_id=None,
            job_id=job_id,
            log_type="prepare",
            message=f"已创建导入批次，文件路径: {path}",
        )
        return job_id
