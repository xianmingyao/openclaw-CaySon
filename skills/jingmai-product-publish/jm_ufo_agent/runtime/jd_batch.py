"""京东批量抓取成功率验证服务。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from jm_ufo_agent.agents.base import AgentContext
from jm_ufo_agent.agents.jd_crawler import JdCrawlerAgent


@dataclass(frozen=True)
class JdCrawlBatchReport:
    """京东批量抓取报告。"""

    total: int
    success_count: int
    success_rate: float
    failed_rows: list[dict[str, Any]] = field(default_factory=list)
    samples: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """转换为可落库/CLI 输出的字典。"""

        # success_rate 是 F02 95% 验收的核心指标。
        # failed_rows 保留 row_index/product_id/message，便于重试或人工排查。
        # samples 只保存前几条成功结果，避免日志过大。
        return {
            "total": self.total,
            "success_count": self.success_count,
            "success_rate": self.success_rate,
            "failed_rows": list(self.failed_rows),
            "samples": list(self.samples),
        }


class JdBatchCrawlService:
    """批量调用 JdCrawlerAgent 并计算成功率。"""

    def __init__(self, agent: JdCrawlerAgent):
        """保存京东抓取 Agent。"""

        # agent 可注入真实 transport 或测试 fake handler。
        # 服务本身不创建网络连接，是否访问京东由 agent 的 transport 决定。
        # 这样真实抓取必须由调用方显式装配，避免误触外部网站。
        self.agent = agent

    async def crawl_products(self, task_id: str, products: list[dict[str, Any]], required_success_rate: float = 0.95) -> JdCrawlBatchReport:
        """批量抓取商品并生成成功率报告。"""

        # 每个 product 独立执行，单行失败不会中断整批统计。
        # 成功必须同时具备标题、价格、图片列表，符合 F02 验收语义。
        # required_success_rate 只用于报告 failed_rows，不在这里抛异常。
        successes: list[dict[str, Any]] = []
        failed_rows: list[dict[str, Any]] = []
        for index, product in enumerate(products, start=1):
            context = AgentContext(task_id=task_id, row_index=int(product.get("row_index") or index), product=product)
            try:
                result = await self.agent.crawl(context)
            except Exception as exc:
                failed_rows.append({"row_index": context.row_index, "product_id": product.get("product_id"), "message": str(exc)})
                continue
            if self._is_success(result.data):
                successes.append(result.data)
            else:
                failed_rows.append({"row_index": context.row_index, "product_id": product.get("product_id"), "message": "missing title/price/images", "data": result.data})
        total = len(products)
        success_rate = (len(successes) / total) if total else 0.0
        if total and success_rate < required_success_rate:
            failed_rows.append({"row_index": None, "product_id": None, "message": f"success_rate_below_{required_success_rate:.2f}", "success_rate": success_rate})
        return JdCrawlBatchReport(total=total, success_count=len(successes), success_rate=success_rate, failed_rows=failed_rows, samples=successes[:5])

    def _is_success(self, data: dict[str, Any]) -> bool:
        """判断单条京东抓取结果是否满足 F02。"""

        # 标题为空说明页面结构或抓取失败。
        # 价格为空说明没有拿到核心采购/参考价格。
        # 图片列表为空会阻断 F03，因此 F02 也视为不完整。
        return bool(data.get("title")) and bool(data.get("price")) and bool(data.get("image_urls"))
