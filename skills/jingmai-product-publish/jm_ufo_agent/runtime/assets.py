"""图片下载、转换和 VLM 审计流水线。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from jm_ufo_agent.agents.base import AgentContext
from jm_ufo_agent.agents.image_fetch import ImageFetchAgent
from jm_ufo_agent.agents.image_transform import ImageTransformAgent
from jm_ufo_agent.storage.repositories.models import ProductAssetRecord, VlmCallRecord


@dataclass(frozen=True)
class AssetPipelineReport:
    """商品素材处理报告。"""

    product_id: str
    downloaded_count: int
    transformed_count: int
    failed: bool
    assets: list[dict[str, Any]] = field(default_factory=list)
    vlm_attempts: list[dict[str, Any]] = field(default_factory=list)
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        """转换为证据字典。"""

        # downloaded_count 用于判断图片下载是否覆盖主图/副图。
        # transformed_count 用于判断 VLM 转换是否全部成功。
        # failed 为 True 时 workflow 应 halt 当前 row。
        return {
            "product_id": self.product_id,
            "downloaded_count": self.downloaded_count,
            "transformed_count": self.transformed_count,
            "failed": self.failed,
            "assets": list(self.assets),
            "vlm_attempts": list(self.vlm_attempts),
            "message": self.message,
        }


class AssetPipelineService:
    """串起 ImageFetchAgent、ImageTransformAgent 和审计 repository。"""

    def __init__(self, fetch_agent: ImageFetchAgent, transform_agent: ImageTransformAgent, asset_repo=None, vlm_repo=None):
        """保存 pipeline 依赖。"""

        # fetch_agent 可注入真实 downloader 或 fake handler。
        # transform_agent 可注入真实 VLM handler 或 fake handler。
        # repository 均可选，未提供时只返回报告，不落库。
        self.fetch_agent = fetch_agent
        self.transform_agent = transform_agent
        self.asset_repo = asset_repo
        self.vlm_repo = vlm_repo

    async def process_product(self, context: AgentContext) -> AssetPipelineReport:
        """处理单个商品的图片下载、转换和审计。"""

        # 先下载图片，再把下载结果放回转换上下文。
        # 下载资产会逐条写入 ProductAssetRepository，保留 URL/local_path/hash。
        # VLM 结果和尝试记录会写入 VlmCallRepository，方便成本与失败审计。
        fetch_result = await self.fetch_agent.fetch(context)
        assets = list(fetch_result.data.get("assets") or [])
        await self._record_assets(context, assets, transform_status="downloaded" if fetch_result.ok else "download_failed")
        transform_context = context.with_evidence("downloaded_assets", assets)
        transform_result = await self.transform_agent.transform_with_retry(transform_context)
        transformed_assets = list(transform_result.data.get("transformed_assets") or [])
        attempts = list(transform_result.data.get("attempts") or [])
        await self._record_vlm_call(context, transform_result.ok, attempts, transform_result.data)
        if transformed_assets:
            await self._record_assets(context, transformed_assets, transform_status="transformed")
        return AssetPipelineReport(
            product_id=str(context.product.get("product_id") or "unknown"),
            downloaded_count=len(assets),
            transformed_count=len(transformed_assets),
            failed=not fetch_result.ok or not transform_result.ok,
            assets=assets or transformed_assets,
            vlm_attempts=attempts,
            message=transform_result.message if not transform_result.ok else fetch_result.message,
        )

    async def _record_assets(self, context: AgentContext, assets: list[dict[str, Any]], transform_status: str) -> None:
        """把素材记录写入 repository。"""

        # repository 缺失时直接跳过，保持测试和 dry-run 轻量。
        # asset_type 默认按顺序生成 main/sub，调用方也可在 asset dict 中显式给出。
        # metadata 保存原始 asset 字段，避免丢失下载 hash、大小等证据。
        if self.asset_repo is None:
            return
        product_id = str(context.product.get("product_id") or "unknown")
        for index, asset in enumerate(assets):
            await self.asset_repo.upsert(
                ProductAssetRecord(
                    product_id=product_id,
                    task_id=context.task_id,
                    row_index=context.row_index,
                    asset_type=str(asset.get("asset_type") or ("main_image" if index == 0 else f"sub_image_{index}")),
                    local_path=asset.get("local_path") or asset.get("transformed_path"),
                    remote_url=asset.get("remote_url"),
                    transform_status=transform_status,
                    transformed_path=asset.get("transformed_path"),
                    metadata=dict(asset),
                )
            )

    async def _record_vlm_call(self, context: AgentContext, ok: bool, attempts: list[dict[str, Any]], metadata: dict[str, Any]) -> None:
        """把 VLM 调用审计写入 repository。"""

        # VLM 审计即使失败也要记录，方便后续分析成本和失败原因。
        # 当前 AgentResult 不含 token/latency 时用 0，占位字段保持 schema 稳定。
        # metadata 保留 attempts 和底层返回 data，避免后续排查缺证据。
        if self.vlm_repo is None:
            return
        await self.vlm_repo.add(
            VlmCallRecord(
                task_id=context.task_id,
                row_index=context.row_index,
                call_type="image_transform",
                model=str(metadata.get("model") or "unknown"),
                status="success" if ok else "failed",
                cache_hit=bool(metadata.get("cache_hit", False)),
                metadata={**metadata, "attempts": attempts},
            )
        )
