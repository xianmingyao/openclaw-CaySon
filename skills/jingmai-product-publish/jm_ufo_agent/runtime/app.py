"""应用运行入口。"""

from __future__ import annotations

from jm_ufo_agent.workflow.graph import DryRunWorkflow
from jm_ufo_agent.workflow.state import GraphState


async def run_dryrun(task_id: str, row_index: int, product: dict) -> GraphState:
    """运行单行 dry-run 工作流。"""

    # 构造 GraphState 作为唯一状态容器。
    # DryRunWorkflow 不连接外部系统，适合 CI 和本地验证。
    # 返回完整 state，调用方可打印或落库。
    state = GraphState(task_id=task_id, row_index=row_index, product=product)
    workflow = DryRunWorkflow()
    return await workflow.run(state)


async def run_dryrun_with_workflow(task_id: str, row_index: int, product: dict, workflow: DryRunWorkflow) -> GraphState:
    """使用外部注入 workflow 运行 dry-run。"""

    # 该入口用于注入 saver、fake strategy 或真实 backend。
    # 状态构造仍在这里统一完成。
    # 返回完整 state，便于调用方落库或打印。
    state = GraphState(task_id=task_id, row_index=row_index, product=product)
    return await workflow.run(state)
