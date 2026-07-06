"""MiniMax-M3 生产评审运行时装配。"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any
from urllib.request import Request, urlopen

from jm_ufo_agent.core.settings import ReviewScorerSettings
from jm_ufo_agent.integrations.minimax_review import MiniMaxReviewClient, ReviewTransport
from jm_ufo_agent.strategies.review_score import MiniMaxReviewScoreStrategy
from jm_ufo_agent.utils.retry import RetryPolicy, retry_async


class UrllibReviewTransport:
    """基于标准库 urllib 的 Anthropic-compatible JSON transport。"""

    async def get_json(self, url: str, headers: dict[str, str]) -> dict[str, Any]:
        """执行 GET 请求并返回 JSON。"""

        # 真实网络 IO 放到 asyncio.to_thread，避免阻塞事件循环。
        # headers 由 MiniMaxReviewClient 构造，包含 x-api-key 和 anthropic-version。
        # 响应必须是 JSON object，否则 json.loads 会直接暴露错误。
        return await asyncio.to_thread(self._request_json, "GET", url, headers, None)

    async def post_json(self, url: str, headers: dict[str, str], payload: dict[str, Any]) -> dict[str, Any]:
        """执行 POST 请求并返回 JSON。"""

        # payload 使用 ensure_ascii=False，保留中文 spec/rubric。
        # 这里只负责 HTTP，不理解业务评分字段。
        # 网络异常不吞掉，由重试包装器或策略层记录为 unavailable。
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        return await asyncio.to_thread(self._request_json, "POST", url, headers, body)

    def _request_json(self, method: str, url: str, headers: dict[str, str], body: bytes | None) -> dict[str, Any]:
        """同步执行一次 HTTP 请求。"""

        # urllib 是标准库，避免为了评审器强制引入 aiohttp/httpx。
        # timeout 固定 60 秒，调用方外层仍有 retry policy 控制重试次数。
        # 返回值必须是 JSON object，防止 HTML 错误页被误当成评分结果。
        request = Request(url, data=body, headers=headers, method=method)
        with urlopen(request, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("MiniMax response must be a JSON object")
        return data


class RetryingReviewTransport:
    """给评审器 transport 增加指数退避。"""

    def __init__(self, inner: ReviewTransport, policy: RetryPolicy):
        """保存底层 transport 和重试策略。"""

        # inner 可以是真实 UrllibReviewTransport，也可以是测试 fake。
        # retry_async 会保留最后一次异常，方便上层记录真实失败类型。
        # 退避参数来自 ReviewScorerSettings，符合设计文档 F19/NF08。
        self.inner = inner
        self.policy = policy

    async def get_json(self, url: str, headers: dict[str, str]) -> dict[str, Any]:
        """带重试执行 GET。"""

        # /v1/models preflight 也需要退避，避免短暂网络抖动误判模型不可用。
        # operation 使用闭包捕获参数，保持 retry_async 接口简单。
        # 返回值原样交给 MiniMaxReviewClient 解析。
        return await retry_async(lambda: self.inner.get_json(url, headers), self.policy)

    async def post_json(self, url: str, headers: dict[str, str], payload: dict[str, Any]) -> dict[str, Any]:
        """带重试执行 POST。"""

        # /v1/messages 失败按指数退避重试。
        # 不在这里解析模型输出，避免 transport 和业务耦合。
        # 超过最大次数后异常抛给策略层，策略层会 halt 评审。
        return await retry_async(lambda: self.inner.post_json(url, headers, payload), self.policy)


@dataclass(frozen=True)
class ReviewPreflightReport:
    """MiniMax 评审器启动预检报告。"""

    ok: bool
    provider: str
    model: str
    base_url: str
    message: str
    error_type: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """转换为 CLI/dashboard 可输出的字典。"""

        # ok 表示 /v1/models 中确认存在目标模型。
        # message 保留人类可读的结论，便于生产前检查。
        # error_type 不包含 token 或 headers，避免泄露凭证。
        return {
            "ok": self.ok,
            "provider": self.provider,
            "model": self.model,
            "base_url": self.base_url,
            "message": self.message,
            "error_type": self.error_type,
        }


async def preflight_minimax_review_scorer(settings: ReviewScorerSettings, transport: ReviewTransport | None = None) -> ReviewPreflightReport:
    """执行 MiniMax-M3 /v1/models 预检并返回报告。"""

    # 该函数只有被 CLI 或 workflow 显式调用时才会访问网络。
    # transport 可注入 fake，保证单元测试不触发真实 MiniMax。
    # 失败时返回报告而不是抛异常，方便 readiness 汇总和 dashboard 展示。
    try:
        strategy = build_minimax_review_strategy(settings, transport=transport)
        ok = await strategy.client.preflight()
    except Exception as exc:
        return ReviewPreflightReport(
            ok=False,
            provider=settings.provider,
            model=settings.model,
            base_url=settings.base_url,
            message=f"review_scorer_unavailable: {exc}",
            error_type=exc.__class__.__name__,
        )
    if not ok:
        return ReviewPreflightReport(
            ok=False,
            provider=settings.provider,
            model=settings.model,
            base_url=settings.base_url,
            message=f"model_not_found: {settings.model}",
        )
    return ReviewPreflightReport(
        ok=True,
        provider=settings.provider,
        model=settings.model,
        base_url=settings.base_url,
        message=f"model_available: {settings.model}",
    )


def build_minimax_review_strategy(settings: ReviewScorerSettings, transport: ReviewTransport | None = None) -> MiniMaxReviewScoreStrategy:
    """根据配置构造可生产注入的 MiniMax 评审策略。"""

    # 该工厂只装配对象，不执行 /v1/models 或 /v1/messages。
    # 真实网络调用发生在 strategy.decide_async，被 workflow 显式触发。
    # transport 可注入 fake，保证单元测试不访问真实 MiniMax。
    policy = RetryPolicy(
        max_attempts=settings.max_call_attempts,
        base_delay_sec=settings.backoff_base_sec,
        max_delay_sec=settings.backoff_max_sec,
    )
    retrying_transport = RetryingReviewTransport(transport or UrllibReviewTransport(), policy)
    client = MiniMaxReviewClient(settings, retrying_transport)
    return MiniMaxReviewScoreStrategy(max_loop_steps=settings.max_loop_steps, client=client)
