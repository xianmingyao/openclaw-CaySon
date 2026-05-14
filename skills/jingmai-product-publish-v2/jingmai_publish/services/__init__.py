"""Service 层导出。

说明：
- 这里优先导出当前仓库中已经落地的服务
- 某些计划中的服务文件可能尚未恢复到工作区
- 为避免一个未实现模块阻塞整个 CLI 入口，这里对可选服务做安全导入
"""

from .desktop_verify import DesktopVerificationService
from .excel_ingest import ExcelIngestService
from .image_service import ProductImageService
from .import_pipeline import ImportPipelineService
from .jingmai_workflow import JingmaiWorkflowService
from .task_service import PublishTaskService
from .task_ingress import TaskIngressService

__all__ = [
    "DesktopVerificationService",
    "ExcelIngestService",
    "ProductImageService",
    "ImportPipelineService",
    "JingmaiWorkflowService",
    "PublishTaskService",
    "TaskIngressService",
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
