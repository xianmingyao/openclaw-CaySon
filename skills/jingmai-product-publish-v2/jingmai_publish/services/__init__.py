"""Service 层导出。"""

from .channel_ingress import FeishuPathChannelService, LocalPathChannelService
from .desktop_verify import DesktopVerificationService
from .draft_e2e import DraftE2EOptions, DraftE2EOrchestrator
from .excel_ingest import ExcelIngestService
from .image_service import ProductImageService
from .import_pipeline import ImportPipelineService
from .jingmai_workflow import JingmaiWorkflowService
from .retention_service import RuntimeRetentionService
from .task_ingress import TaskIngressService
from .task_runner import TaskRunner
from .task_service import PublishTaskService

__all__ = [
    "LocalPathChannelService",
    "DesktopVerificationService",
    "DraftE2EOptions",
    "DraftE2EOrchestrator",
    "ExcelIngestService",
    "FeishuPathChannelService",
    "ProductImageService",
    "ImportPipelineService",
    "JingmaiWorkflowService",
    "RuntimeRetentionService",
    "TaskIngressService",
    "TaskRunner",
    "PublishTaskService",
]

try:
    from .jd_fetch import JDProductFetchService

    __all__.append("JDProductFetchService")
except ModuleNotFoundError:
    JDProductFetchService = None  # type: ignore[assignment]

try:
    from .product_prepare import ProductDataPrepareService

    __all__.append("ProductDataPrepareService")
except ModuleNotFoundError:
    ProductDataPrepareService = None  # type: ignore[assignment]
