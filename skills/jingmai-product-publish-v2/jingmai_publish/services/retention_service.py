"""Runtime log and artifact retention service."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy.orm import Session

from jingmai_publish.models import RuntimeLog
from jingmai_publish.repositories.runtime_log import RuntimeLogRepository


class RuntimeRetentionService:
    """Clean expired runtime logs and related local artifacts."""

    def __init__(self, session: Session, screenshot_dir: str | Path) -> None:
        self.session = session
        self.screenshot_dir = Path(screenshot_dir)
        self.runtime_log_repo = RuntimeLogRepository(session)

    def cleanup(self, *, now: datetime | None = None, delete_orphan_screenshots: bool = True) -> dict[str, object]:
        """Delete expired DB logs and old screenshot artifacts."""

        current_time = now or datetime.now()
        expired_logs = (
            self.session.query(RuntimeLog)
            .filter(RuntimeLog.expire_at < current_time)
            .order_by(RuntimeLog.id.asc())
            .all()
        )
        deleted_paths: list[str] = []
        for log in expired_logs:
            if not log.detail_path:
                continue
            detail_path = Path(log.detail_path)
            if detail_path.exists() and detail_path.is_file():
                detail_path.unlink(missing_ok=True)
                deleted_paths.append(str(detail_path))

        deleted_log_count = self.runtime_log_repo.delete_expired_logs(current_time)

        deleted_orphan_screenshots: list[str] = []
        if delete_orphan_screenshots and self.screenshot_dir.exists():
            screenshot_cutoff = current_time - timedelta(days=3)
            for file_path in self.screenshot_dir.glob("**/*"):
                if not file_path.is_file():
                    continue
                modified_at = datetime.fromtimestamp(file_path.stat().st_mtime)
                if modified_at < screenshot_cutoff:
                    file_path.unlink(missing_ok=True)
                    deleted_orphan_screenshots.append(str(file_path))

        self.session.commit()
        return {
            "deleted_log_count": deleted_log_count,
            "deleted_detail_paths": deleted_paths,
            "deleted_orphan_screenshots": deleted_orphan_screenshots,
        }
