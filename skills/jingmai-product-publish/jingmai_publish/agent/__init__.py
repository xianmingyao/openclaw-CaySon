"""Agent decision layer: Planner → Executor → Reflection pipeline.

BL-091: Replaces hardcoded if/elif chain with structured agent pipeline.
Rule-driven, with extension points for LLM/Vision providers in Phase C.
BL-094A: Added ReflectionRecord for failure reflection persistence.
"""

from __future__ import annotations

from .executor import AgentExecutor
from .pipeline import AgentPipeline
from .planner import AgentPlanner
from .reflection import AgentReflection
from .reflection_record import ReflectionRecord
from .registry import REGISTRY, ActionRegistry
from .types import ActionStep, Plan, ReflectionDecision, StepCategory, StepValidationError

__all__ = [
    "ActionRegistry",
    "ActionStep",
    "AgentExecutor",
    "AgentPipeline",
    "AgentPlanner",
    "AgentReflection",
    "Plan",
    "REGISTRY",
    "ReflectionDecision",
    "ReflectionRecord",
    "StepCategory",
    "StepValidationError",
]
