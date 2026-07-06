"""Repository 集合。"""

from __future__ import annotations

from jm_ufo_agent.storage.repositories.artifacts import ArtifactRepository
from jm_ufo_agent.storage.repositories.assets import ProductAssetRepository
from jm_ufo_agent.storage.repositories.draft_verifications import DraftVerificationRepository
from jm_ufo_agent.storage.repositories.field_progress import FieldProgressRepository
from jm_ufo_agent.storage.repositories.locator_cache import LocatorCacheRepository
from jm_ufo_agent.storage.repositories.models import (
    ArtifactRecord,
    DraftVerificationRecord,
    FieldProgressRecord,
    JsonTableRecord,
    LocatorCacheRecord,
    ProductAssetRecord,
    ProductRecord,
    RowExecutionRecord,
    StepLogRecord,
    TaskRecord,
    VlmCallRecord,
)
from jm_ufo_agent.storage.repositories.products import ProductRepository
from jm_ufo_agent.storage.repositories.rows import RowExecutionRepository
from jm_ufo_agent.storage.repositories.step_logs import StepLogRepository
from jm_ufo_agent.storage.repositories.tasks import TaskRepository
from jm_ufo_agent.storage.repositories.vlm_calls import VlmCallRepository

__all__ = [
    "ArtifactRecord",
    "ArtifactRepository",
    "DraftVerificationRecord",
    "DraftVerificationRepository",
    "FieldProgressRecord",
    "FieldProgressRepository",
    "JsonTableRecord",
    "LocatorCacheRecord",
    "LocatorCacheRepository",
    "ProductAssetRecord",
    "ProductAssetRepository",
    "ProductRecord",
    "ProductRepository",
    "RowExecutionRecord",
    "RowExecutionRepository",
    "StepLogRecord",
    "StepLogRepository",
    "TaskRecord",
    "TaskRepository",
    "VlmCallRecord",
    "VlmCallRepository",
]
