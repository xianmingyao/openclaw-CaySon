"""Repository 数据模型。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class TaskRecord:
    """上架任务记录。"""

    task_id: str
    status: str
    current_row: int | None = None
    workflow_version: str = "v2.0.0"
    state: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProductRecord:
    """待上架商品记录。"""

    product_id: str
    row_index: int
    title: str
    raw_data: dict[str, Any] = field(default_factory=dict)
    enriched_data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class FieldProgressRecord:
    """字段级断点记录。"""

    task_id: str
    row_index: int
    field_name: str
    status: str
    evidence: dict[str, Any] = field(default_factory=dict)
    updated_at: datetime | None = None


@dataclass(frozen=True)
class RowExecutionRecord:
    """行级断点续传记录。"""

    task_id: str
    row_index: int
    status: str
    current_field: str | None = None
    retry_count: int = 0
    last_error: str | None = None
    page_signature: str | None = None
    completion_score: float = 0.0
    completion_passed: bool = False
    completion_details: dict[str, Any] = field(default_factory=dict)
    evaluation_loop_count: int = 0
    review_score: float = 0.0
    review_decision: str = ""
    review_details: dict[str, Any] = field(default_factory=dict)
    draft_evidence: dict[str, Any] = field(default_factory=dict)
    updated_at: datetime | None = None


@dataclass(frozen=True)
class ArtifactRecord:
    """截图、OCR、页面签名等本地证据记录。"""

    task_id: str
    row_index: int
    artifact_type: str
    storage_path: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProductAssetRecord:
    """商品图片/素材记录。"""

    product_id: str
    asset_type: str
    task_id: str | None = None
    row_index: int | None = None
    local_path: str | None = None
    remote_url: str | None = None
    transform_status: str = "pending"
    transformed_path: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StepLogRecord:
    """单个 workflow 节点的执行日志。"""

    task_id: str
    node_name: str
    status: str
    row_index: int | None = None
    duration_ms: int | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LocatorCacheRecord:
    """字段定位缓存记录。"""

    field_key: str
    page_signature: str
    selector_type: str
    selector_value: str
    confidence: float = 0.0
    hit_count: int = 0


@dataclass(frozen=True)
class DraftVerificationRecord:
    """保存草稿后的验证记录。"""

    task_id: str
    row_index: int
    verification_result: str
    product_id: str | None = None
    draft_url: str | None = None
    completion_score: float = 0.0
    diff: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class VlmCallRecord:
    """VLM 调用审计记录。"""

    call_type: str
    model: str
    status: str
    task_id: str | None = None
    row_index: int | None = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: int = 0
    cache_hit: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class JsonTableRecord:
    """通用 JSON 表记录。"""

    table_name: str
    task_id: str
    row_index: int | None = None
    payload: dict[str, Any] = field(default_factory=dict)
