"""京东商品快照 Repository。"""

from __future__ import annotations

from sqlalchemy.orm import Session

from jingmai_publish.models import JDProductSnapshot


class JDProductSnapshotRepository:
    """负责京东商品快照的读写。"""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create_snapshot(self, **kwargs) -> JDProductSnapshot:
        """创建一条抓取快照记录。"""

        snapshot = JDProductSnapshot(**kwargs)
        self.session.add(snapshot)
        self.session.flush()
        return snapshot

    def get_latest_by_job_item_id(self, job_item_id: int) -> JDProductSnapshot | None:
        """读取某个商品行的最新快照。"""

        return (
            self.session.query(JDProductSnapshot)
            .filter(JDProductSnapshot.job_item_id == job_item_id)
            .order_by(JDProductSnapshot.fetched_at.desc(), JDProductSnapshot.id.desc())
            .first()
        )
