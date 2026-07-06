"""MiniMax-M3 评审客户端边界。"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Protocol

from jm_ufo_agent.core.settings import ReviewScorerSettings


class ReviewTransport(Protocol):
    """评审器 HTTP transport 协议。"""

    async def get_json(self, url: str, headers: dict[str, str]) -> dict[str, Any]:
        """执行 GET 并返回 JSON。"""

    async def post_json(self, url: str, headers: dict[str, str], payload: dict[str, Any]) -> dict[str, Any]:
        """执行 POST 并返回 JSON。"""


@dataclass(frozen=True)
class ReviewRubricItem:
    """评审 rubric 单项。"""

    item: str
    max_score: int = 100
    evidence: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ParsedReviewScore:
    """解析后的评审分数。"""

    overall_score: int
    max_score: int
    blocking_gaps: list[str]
    recommendations: list[str]
    raw: dict[str, Any]


class MiniMaxReviewClient:
    """MiniMax Anthropic-compatible 评审客户端。"""

    def __init__(self, settings: ReviewScorerSettings, transport: ReviewTransport):
        """初始化客户端。"""

        # settings 只保存 URL、模型和 token，不在构造时发请求。
        # transport 由外部注入，测试用 fake，生产可接 aiohttp/httpx。
        # 所有真实网络调用都必须通过显式方法触发。
        self.settings = settings
        self.transport = transport

    def headers(self) -> dict[str, str]:
        """构造请求头。"""

        # Anthropic API 使用 x-api-key 而非 Authorization: Bearer。
        # anthropic-version 是必需头，MiniMax Anthropic 兼容端点要求。
        # 不在日志中打印 headers，避免泄漏凭证。
        token = self.settings.api_key or ""
        return {
            "x-api-key": token,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

    async def preflight(self) -> bool:
        """检查 MiniMax-M3 模型是否可用。"""

        # 请求 Anthropic-compatible /v1/models 端点。
        # 只检查模型列表是否包含 settings.model。
        # 网络/鉴权异常不在这里吞掉，调用方应 halt 评审节点。
        url = f"{self.settings.base_url.rstrip('/')}/v1/models"
        payload = await self.transport.get_json(url, self.headers())
        models = payload.get("data", [])
        return any(item.get("id") == self.settings.model for item in models if isinstance(item, dict))

    def build_payload(self, spec_markdown: str, rubric: list[ReviewRubricItem]) -> dict[str, Any]:
        """构造 Anthropic /v1/messages 请求体。"""

        # Anthropic API: system 是顶层参数，不在 messages 中。
        # user content 使用 content blocks 格式 [{"type": "text", "text": "..."}]。
        # thinking 参数来自配置，保持 MiniMax-M3 adaptive 约定。
        # max_tokens 替代 OpenAI 的 max_completion_tokens。
        rubric_payload = [item.__dict__ for item in rubric]
        return {
            "model": self.settings.model,
            "max_tokens": 2000,
            "system": "你是京麦自动化需求评审员。只根据输入文档和rubric评分，输出JSON，不允许补造事实。",
            "thinking": {"type": self.settings.thinking},
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({"spec_markdown": spec_markdown, "rubric": rubric_payload}, ensure_ascii=False),
                        }
                    ],
                },
            ],
        }

    async def score(self, spec_markdown: str, rubric: list[ReviewRubricItem]) -> ParsedReviewScore:
        """调用评审器并解析结果。"""

        # score 是显式网络调用入口，默认测试不会触发真实 API。
        # transport 返回 Anthropic messages 响应。
        # 模型输出必须能解析为 JSON，否则抛出 ValueError。
        url = f"{self.settings.base_url.rstrip('/')}/v1/messages"
        response = await self.transport.post_json(url, self.headers(), self.build_payload(spec_markdown, rubric))
        # Anthropic 响应: content 是内容块列表，提取 text 类型的块
        content = ""
        for block in response.get("content", []):
            if block.get("type") == "text":
                content = block.get("text", "")
                break
        if not content:
            raise ValueError("MiniMax response contains no text content block")
        return self.parse_content(content)

    def parse_content(self, content: str) -> ParsedReviewScore:
        """解析模型输出 JSON。"""

        # 有些模型会把 JSON 包在 ```json 代码块里，这里做最小兼容。
        # 解析后只提取评审字段，不让模型输出影响业务状态。
        # 缺失字段使用保守默认值，blocking_gaps 缺失按空列表处理。
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.startswith("json"):
                cleaned = cleaned[len("json") :].strip()
        raw = json.loads(cleaned)
        return ParsedReviewScore(
            overall_score=int(raw.get("overall_score", 0)),
            max_score=int(raw.get("max_score", 100)),
            blocking_gaps=list(raw.get("blocking_gaps", [])),
            recommendations=list(raw.get("recommendations", [])),
            raw=raw,
        )
