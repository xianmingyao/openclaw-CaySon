"""Agent 基础类型。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentContext:
    """Agent 调用上下文。"""

    task_id: str
    row_index: int | None = None
    product: dict[str, Any] = field(default_factory=dict)
    evidence: dict[str, Any] = field(default_factory=dict)

    def with_evidence(self, key: str, value: Any) -> "AgentContext":
        """返回带新增证据的新上下文。

        # 不直接修改原 evidence，避免多个节点共享引用后互相污染。
        # key 使用调用方给出的业务名称，方便后续追踪截图/OCR/读回值。
        # product 仍复用同一份字典，因为商品数据在 Phase 2 中只读使用。
        """

        next_evidence = dict(self.evidence)
        next_evidence[key] = value
        return AgentContext(task_id=self.task_id, row_index=self.row_index, product=self.product, evidence=next_evidence)


@dataclass(frozen=True)
class AgentResult:
    """Agent 执行结果。"""

    ok: bool
    message: str = ""
    data: dict[str, Any] = field(default_factory=dict)


class BaseAgent:
    """所有 Agent 的最小公共基类。"""

    def __init__(self, name: str):
        """初始化 Agent 名称。"""

        # name 会写入日志、证据和测试断言。
        # 基类不保存外部连接，避免构造阶段产生副作用。
        # 具体能力由子类暴露明确方法，而不是 ReAct 自由决策。
        self.name = name

    async def healthcheck(self) -> AgentResult:
        """检查 Agent 是否可用。"""

        # Phase 2 的默认实现只说明对象已初始化。
        # 需要外部资源的 Agent 可在子类中覆盖该方法。
        # 返回 AgentResult 而不是 bool，方便携带诊断信息。
        return AgentResult(ok=True, message=f"{self.name} ready")
