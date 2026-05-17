"""AgentPlanner: topological plan generation from ActionStep preconditions.

BL-091: Replaces TaskRunner._build_plan() with structured, registry-driven planning.
"""

from __future__ import annotations

from collections import deque

from .registry import ActionRegistry
from .types import ActionStep, Plan


class AgentPlanner:
    """Generates an ordered execution plan from a requested step.

    Resolves preconditions transitively and produces a topologically
    sorted list of ActionSteps. The "both" pseudo-step expands to
    ["t1", "t2"].
    """

    def __init__(self, registry: ActionRegistry) -> None:
        self.registry = registry

    def plan(self, requested_step: str) -> Plan:
        """Build an ordered Plan from a requested step name.

        Raises ValueError if the step is unknown.
        """
        # Validate
        if not self.registry.validate_step(requested_step):
            raise ValueError(f"unsupported verification step: {requested_step}")

        # "both" 复合步骤特殊处理
        if requested_step == "both":
            steps = [
                self.registry.get("t1"),
                self.registry.get("t2"),
            ]
            return Plan(target_step=requested_step, steps=steps)

        # 收集所有需要的步骤（目标 + 传递依赖）
        step_set: dict[str, ActionStep] = {}
        self._collect_dependencies(requested_step, step_set)

        # 拓扑排序
        ordered = self._topological_sort(step_set, requested_step)

        return Plan(
            target_step=requested_step,
            steps=ordered,
            metadata={"total_steps": len(ordered)},
        )

    # ── internal ──────────────────────────────────────────────────

    def _collect_dependencies(
        self, step_name: str, collected: dict[str, ActionStep]
    ) -> None:
        """Recursively collect a step and all its precondition ancestors."""
        if step_name in collected:
            return
        step = self.registry.get(step_name)
        collected[step_name] = step
        for precondition in step.preconditions:
            self._collect_dependencies(precondition, collected)

    def _topological_sort(
        self,
        step_set: dict[str, ActionStep],
        target_step: str,
    ) -> list[ActionStep]:
        """Sort steps by dependency depth (BFS from roots).

        Steps with no preconditions are depth 0. Each step's depth
        is max(precondition depth) + 1. Steps are returned in
        increasing depth order, with the target step guaranteed last.
        """
        depth: dict[str, int] = {}

        # Compute depth for each step via BFS
        queue: deque[str] = deque()
        for name, step in step_set.items():
            if not step.preconditions:
                depth[name] = 0
                queue.append(name)

        # Initialize remaining with non-root steps
        remaining: dict[str, ActionStep] = {
            name: step
            for name, step in step_set.items()
            if name not in depth
        }

        while queue:
            current = queue.popleft()
            current_depth = depth[current]
            # Find steps that depend on current
            for name, step in list(remaining.items()):
                if current in step.preconditions:
                    # Check if all preconditions have depths computed
                    if all(p in depth for p in step.preconditions):
                        depth[name] = max(depth[p] for p in step.preconditions) + 1
                        queue.append(name)
                        del remaining[name]

        # Any remaining steps with circular or missing preconditions:
        # assign depth based on what we can compute
        for name in list(remaining.keys()):
            step = step_set[name]
            known_depths = [depth[p] for p in step.preconditions if p in depth]
            depth[name] = (max(known_depths) + 1) if known_depths else 0

        # Sort: by depth, then ensure target is last among same-depth steps
        def sort_key(item: tuple[str, ActionStep]) -> tuple[int, int]:
            name, _ = item
            return (depth.get(name, 0), 1 if name == target_step else 0)

        sorted_items = sorted(step_set.items(), key=sort_key)
        return [step for _, step in sorted_items]
