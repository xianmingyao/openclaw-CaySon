"""Agent pipeline types: ActionStep, Plan, ReflectionDecision.

BL-091: Structured data classes replacing the hardcoded dispatch.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class StepValidationError(ValueError):
    """参数校验/配置错误 — 应直接传播，不被 pipeline 异常处理包装。"""

    pass


class StepCategory(str, Enum):
    """Functional category of an action step."""

    ATTACHMENT = "attachment"  # T1 — attach to window
    NAVIGATION = "navigation"  # T2, T3 — navigate pages
    DATA_ENTRY = "data_entry"  # T4, T5, T7 — fill form fields
    PROBE = "probe"  # probe steps — investigate state
    UPLOAD = "upload"  # T6 image uploads
    CONTENT = "content"  # T6 detail editor content
    ACTION = "action"  # T8 save / publish
    COMPOSITE = "composite"  # "both" pseudo-step


class ReflectionDecision(str, Enum):
    """Decision made by AgentReflection after evaluating an execution outcome.

    CONTINUE:        step succeeded, proceed to next step in plan.
    RETRY:           step failed, retry with same lane/parameters.
    RETRY_NEXT_LANE: step failed, switch to next retry lane (BL-103).
    HUMAN_ESCALATE:  all lanes exhausted, escalate to human review / failure reflection.
    SKIP:            step failed but is non-critical, skip and continue.
    ABORT:           step failed and is critical, halt the entire plan.
    """

    CONTINUE = "continue"
    RETRY = "retry"
    RETRY_NEXT_LANE = "retry_next_lane"
    HUMAN_ESCALATE = "human_escalate"
    SKIP = "skip"
    ABORT = "abort"


@dataclass(slots=True)
class RetryLane:
    """Alternative execution lane for a step (BL-103 lane switching).

    Each lane represents a different strategy/operator for accomplishing
    the same task. When the primary lane fails, the pipeline can switch
    to an alternative lane instead of retrying with the same approach.
    """

    lane_name: str  # e.g. "hover_modal", "text_fallback", "direct_click"
    method_name: str  # alternative method to execute on this lane
    description: str = ""
    param_overrides: dict[str, str] = field(default_factory=dict)  # extra params for this lane


@dataclass(slots=True)
class ActionStep:
    """Structured description of a single T-step action.

    Replaces the 500-line if/elif chain in TaskRunner._execute_step().
    Each entry maps a step name to its workflow method, parameters, and
    execution constraints.
    """

    step_name: str  # e.g. "t1", "t6-main-image"
    method_name: str  # workflow_service method or executor private method
    description: str = ""  # human-readable description
    required_params: tuple[str, ...] = ()  # kwargs required from params dict
    param_map: dict[str, str] = field(default_factory=dict)  # params key → method arg name
    preconditions: tuple[str, ...] = ()  # steps that must run before this one
    category: StepCategory = StepCategory.DATA_ENTRY
    max_retry_count: int = 3
    retry_lanes: tuple[RetryLane, ...] = ()  # BL-103: alternative lanes, empty = no lane switching
    same_lane_max_retries: int = 3  # BL-103: max retries per lane before switching to next


@dataclass(slots=True)
class Plan:
    """Ordered list of ActionSteps produced by AgentPlanner.

    Steps are topologically sorted by preconditions, with the target
    step last. The "both" pseudo-step expands to ["t1", "t2"].
    """

    target_step: str  # the originally requested step
    steps: list[ActionStep] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
