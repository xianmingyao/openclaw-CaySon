"""安全动作策略。"""

from __future__ import annotations

from jm_ufo_agent.agents.base import AgentResult
from jm_ufo_agent.agents.jm_product_form import JmProductFormAgent
from jm_ufo_agent.strategies.plan import FieldPlan


class GuardedActionStrategy:
    """通过安全桌面 Agent 执行字段动作。"""

    def __init__(self, form_agent: JmProductFormAgent | None = None):
        """初始化安全动作策略。"""

        # form_agent 默认是 dry-run 桌面 Agent。
        # 真实 GUI backend 必须注入到 form_agent 中。
        # Strategy 不绕过 Agent，确保 SafetyPolicy 始终生效。
        self.form_agent = form_agent or JmProductFormAgent()

    async def fill_field(self, plan: FieldPlan, evidence: dict | None = None) -> AgentResult:
        """执行单字段填充。"""

        # FieldPlan 只描述“填什么”，不直接触碰 UI。
        # evidence 透传给 Agent/Command，便于后续审计。
        # 返回 AgentResult，由 VerifyStrategy 判断是否推进。
        return await self.form_agent.fill_field(plan.field_name, plan.value, evidence=evidence or {})

    async def save_draft(self, evidence: dict | None = None) -> AgentResult:
        """执行保存草稿动作。"""

        # 保存草稿仍走 Agent 的 submit 方法。
        # SafetyPolicy 会阻断任何误标成发布的动作。
        # 结果只代表动作已发出，不代表草稿已验证成功。
        return await self.form_agent.save_draft(evidence=evidence or {})
