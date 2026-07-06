"""图片转换 Agent。"""

from __future__ import annotations

import asyncio
from typing import Any

from jm_ufo_agent.agents.base import AgentContext, AgentResult
from jm_ufo_agent.agents.worker import WorkerAgent
from jm_ufo_agent.utils.retry import RetryPolicy


class ImageTransformAgent(WorkerAgent):
    """负责 VLM 图片转换。"""

    def __init__(self, handler=None):
        """初始化图片转换 Agent。"""

        # handler 后续接入真实 VLM 转换逻辑。
        # 默认不调用模型，控制成本和外部依赖。
        # 名称固定为 image_transform，便于证据和日志聚合。
        super().__init__(name="image_transform", handler=handler)

    async def transform(self, context: AgentContext):
        """执行 dry-run 图片转换。"""

        # VLM 是高成本能力，dry-run 中不调用模型。
        # 返回 transformed_assets 字段，保持后续节点数据形状稳定。
        # 失败/重试策略由 transform_with_retry 统一处理。
        result = await self.run(context)
        result.data.setdefault("transformed_assets", [])
        return result

    async def transform_with_retry(self, context: AgentContext, policy: RetryPolicy | None = None) -> AgentResult:
        """按 VLM 三次失败规则执行转换。"""

        # F11 要求 VLM 失败 3 次后 halt 当前 row，因此这里不把失败伪装成成功。
        # policy 可注入，测试时把 base_delay_sec 设为 0，避免等待真实退避时间。
        # 返回 AgentResult 而不是抛异常，workflow 节点可以统一写入 halt evidence。
        retry_policy = policy or RetryPolicy(max_attempts=3, base_delay_sec=0.0, max_delay_sec=0.0)
        attempts: list[dict[str, Any]] = []
        for attempt_index in range(retry_policy.max_attempts):
            try:
                result = await self.transform(context)
                result.data.setdefault("attempts", attempts + [{"attempt": attempt_index + 1, "ok": True}])
                return result
            except Exception as exc:
                attempts.append({"attempt": attempt_index + 1, "ok": False, "error": str(exc)})
                if attempt_index < retry_policy.max_attempts - 1:
                    await asyncio.sleep(retry_policy.delay_for_attempt(attempt_index))
        return AgentResult(
            ok=False,
            message="VLM 图片转换连续失败 3 次，已中止当前 row",
            data={
                "attempts": attempts,
                "halt_reason": "vlm_transform_failed",
            },
        )
