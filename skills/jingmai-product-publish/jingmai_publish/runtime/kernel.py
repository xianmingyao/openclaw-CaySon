"""Host runtime wrapper for provider-oriented execution.

Phase B upgrade: integrates RuntimeEventLoop + ProviderManifest into
the observe→decide→act→verify→repeat main loop aligned with both
sightflow-desktop-agent and UI-TARS-desktop.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from jingmai_publish.agent.types import StepValidationError
from jingmai_publish.runtime.event_loop import (
    EventType,
    RuntimeEvent,
    RuntimeEventLoop,
)
from jingmai_publish.runtime.manifest import (
    CapabilityCategory,
    ProviderManifest,
    build_default_manifests,
)
from jingmai_publish.runtime.providers import ProviderRegistry


@dataclass(slots=True)
class HostRuntime:
    """SightFlow-compatible host runtime.

    V2 (Phase B) upgrade:
    - Integrated RuntimeEventLoop for event-driven execution
    - Provider manifests for capability declaration
    - observe→decide→act→verify→repeat main loop
    - Session state tracking through LoopSessionState

    The runtime wraps a TaskRunner and orchestrates execution through
    the provider layer, emitting events at each stage of the loop.
    """

    task_runner: Any
    providers: ProviderRegistry = field(default_factory=ProviderRegistry)

    # Phase B additions
    event_loop: RuntimeEventLoop | None = None
    manifests: list[ProviderManifest] = field(default_factory=list)
    session_id: str = field(default_factory=lambda: f"host-{uuid.uuid4().hex[:12]}")

    def __post_init__(self) -> None:
        if not self.manifests:
            self.manifests = build_default_manifests()
        if self.event_loop is None:
            self.event_loop = RuntimeEventLoop(
                handler=self._handle_event,
                session_id=self.session_id,
            )

    # ── public API ──

    def run(self, step: str = "both", debug: bool = False, **kwargs) -> dict[str, object]:
        """Execute a task through the observe→decide→act→verify→repeat cycle.

        This is the main entry point. It:
        1. Normalizes the payload through the channel provider
        2. Emits TASK_SUBMITTED event
        3. Runs observation → action plan → execution → verification
        4. Emits TASK_COMPLETED or TASK_FAILED
        5. Returns structured result with runtime metadata
        """
        payload = dict(kwargs)
        if self.providers.channel is not None:
            payload = self.providers.channel.normalize_payload(payload)

        # Build session seed
        session_seed = {
            "requested_step": step,
            "payload_keys": sorted(payload.keys()),
            "providers": self.providers.snapshot(),
            "manifest_names": [m.name for m in self.manifests],
        }

        # ── OBSERVE ──
        observation = self._observe(session_seed)
        self._emit(EventType.OBSERVATION_COLLECTED, {
            "step": step,
            "observation": observation,
        })

        # ── DECIDE (action plan) ──
        action_plan = self._decide(step, payload)
        self._emit(EventType.ACTION_PLAN_GENERATED, {
            "step": step,
            "action_plan": action_plan,
        })

        # ── ACT ──
        self._emit(EventType.TASK_STARTED, {
            "step": step,
            "action": action_plan,
        })
        try:
            result = self.task_runner.run(step=step, debug=debug, **payload)
        except StepValidationError:
            raise  # 参数校验错误直接传播
        except Exception as exc:
            self._emit(EventType.TASK_FAILED, {
                "step": step,
                "error": str(exc),
            })
            return {
                "success": False,
                "error": str(exc),
                "runtime": self._runtime_meta(observation, action_plan),
            }

        self._emit(EventType.ACTION_EXECUTED, {
            "step": step,
            "session": result.get("session", {}),
        })

        # ── VERIFY ──
        verification = self._verify(result)
        self._emit(EventType.VERIFICATION_COMPLETED, {
            "step": step,
            "verification": verification,
        })

        # ── PERSIST ──
        self._persist(step, observation, action_plan, result, verification)

        # ── REMEMBER ──
        self._remember(step, result, verification)

        # ── Final result ──
        session = result.get("session", {})
        if session.get("halted"):
            self._emit(EventType.TASK_FAILED, {
                "step": step,
                "halted": True,
                "page_state": session.get("page_state"),
                "last_message": session.get("last_message"),
            })
        else:
            self._emit(EventType.TASK_COMPLETED, {
                "step": step,
                "page_state": session.get("page_state"),
                "completed_steps": session.get("completed_steps", []),
            })

        result["runtime"] = self._runtime_meta(observation, action_plan)
        result["verification"] = verification
        return result

    def run_async(self, step: str = "both", **kwargs) -> str:
        """Enqueue a task for background processing. Returns event_id.

        The task will be picked up by the event loop worker thread.
        Use session_state() to check progress.
        """
        return self.event_loop.enqueue(EventType.TASK_SUBMITTED, {
            "step": step,
            "kwargs": kwargs,
        }) if self.event_loop else ""

    def start_loop(self) -> None:
        """Start the background event loop."""
        if self.event_loop:
            self.event_loop.start()

    def stop_loop(self) -> None:
        """Stop the background event loop."""
        if self.event_loop:
            self.event_loop.stop()

    def session_state(self) -> dict[str, Any]:
        """Return current runtime session snapshot."""
        if self.event_loop:
            return self.event_loop.session_state()
        return {"session_id": self.session_id, "is_running": False}

    def event_history(self, *, limit: int = 50) -> list[dict[str, Any]]:
        """Return recent runtime event history."""
        if self.event_loop:
            return self.event_loop.event_history(limit=limit)
        return []

    def capability_matrix(self) -> dict[str, list[str]]:
        """Return which capabilities each loaded manifest provides."""
        matrix: dict[str, list[str]] = {}
        for manifest in self.manifests:
            matrix[manifest.name] = [c.category.value for c in manifest.capabilities]
        return matrix

    # ── internal: observe → decide → act → verify ──

    def _observe(self, session_seed: dict[str, Any]) -> dict[str, Any]:
        """Collect observation from the observation provider."""
        if self.providers.observation is not None:
            return self.providers.observation.observe(session_seed)
        return {"source": "session_seed", "keys": sorted(session_seed.keys())}

    def _decide(self, step: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Generate action plan from the action provider."""
        if self.providers.action is not None:
            return self.providers.action.execute(step, dict(payload))
        return {"action_name": step, "payload_keys": sorted(payload.keys())}

    def _verify(self, result: dict[str, object]) -> dict[str, Any]:
        """Verify execution result.

        BL-091: 使用 trace 中的 reflection 记录增强验证摘要。
        Phase C: 集成 vision provider 进行 before/after 截图视觉校验。

        Vision verification flow:
        1. 检查是否有 vision provider 和 before/after 截图
        2. 调用 compare_screenshots 对比截图变化
        3. 视觉校验结果合并入 verification 摘要
        """
        session = result.get("session", {})
        halted = bool(session.get("halted"))
        page_state = session.get("page_state")
        completed_steps = session.get("completed_steps", [])
        trace = session.get("trace", [])

        # 从 trace 中提取 reflection 统计
        total_attempts = len(trace)
        verified_attempts = sum(1 for t in trace if t.get("verified"))
        failed_attempts = total_attempts - verified_attempts
        failure_signatures = [
            t.get("failure_signature")
            for t in trace
            if t.get("failure_signature")
        ]

        vision_available = any(
            m.has_capability(CapabilityCategory.VISION) for m in self.manifests
        )

        verification = {
            "success": not halted,
            "method": "session_state",
            "page_state": page_state,
            "halted": halted,
            "completed_steps": completed_steps,
            "reflection_summary": {
                "total_attempts": total_attempts,
                "verified_attempts": verified_attempts,
                "failed_attempts": failed_attempts,
                "failure_signatures": failure_signatures,
                "trace": trace,
            },
            "vision_available": vision_available,
            "vision_used": False,
            "vision_result": None,
        }

        # ── Phase C: Vision-based verification ──
        if self.providers.vision is not None and vision_available:
            verification = self._verify_with_vision(result, verification)

        return verification

    def _verify_with_vision(
            self, result: dict[str, object], base_verification: dict[str, Any]
    ) -> dict[str, Any]:
        """使用 vision provider 增强验证结果。

        从 session 中提取 before/after 截图路径，
        调用 vision.compare_screenshots 进行对比分析。
        """
        session = result.get("session", {})
        before_path = session.get("screenshot_before")
        after_path = session.get("screenshot_after")

        if not before_path or not after_path:
            return base_verification

        try:
            from pathlib import Path
            if not Path(before_path).exists() or not Path(after_path).exists():
                return base_verification

            vision_result = self.providers.vision.compare_screenshots(
                before_path=str(before_path),
                after_path=str(after_path),
            )
            base_verification["vision_used"] = True
            base_verification["vision_result"] = vision_result.to_dict() if hasattr(vision_result, "to_dict") else str(
                vision_result)

            # 如果视觉校验也通过，增强 success
            if vision_result.success and not base_verification["success"]:
                base_verification["success"] = True
                base_verification["method"] = "vision_override"
        except Exception:
            # Vision 不可用时降级，不阻塞主流程
            base_verification["vision_used"] = False
            base_verification["vision_error"] = "vision provider 调用失败（已降级）"

        return base_verification

    def _persist(
            self,
            step: str,
            observation: dict[str, Any],
            action_plan: dict[str, Any],
            result: dict[str, object],
            verification: dict[str, Any],
    ) -> None:
        """Persist runtime artifacts through the persistence provider."""
        if self.providers.persistence is None:
            return
        session = result.get("session", {})
        self.providers.persistence.persist_event("runtime_started", {
            "step": step,
            "observation": observation,
            "payload_keys": sorted(action_plan.get("payload_keys", [])),
        })
        self.providers.persistence.persist_event("runtime_action_plan", action_plan)
        self.providers.persistence.persist_event("runtime_completed", {
            "step": step,
            "halted": session.get("halted"),
            "verification": verification,
        })

    def _remember(
            self,
            step: str,
            result: dict[str, object],
            verification: dict[str, Any],
    ) -> None:
        """Store execution memory through the memory provider."""
        if self.providers.memory is None:
            return
        session = result.get("session", {})
        self.providers.memory.remember("runtime_completed", {
            "step": step,
            "halted": session.get("halted"),
            "page_state": session.get("page_state"),
            "completed_steps": session.get("completed_steps", []),
            "verification": verification,
        })
        for trace_item in session.get("trace", []):
            failure_signature = trace_item.get("failure_signature")
            if failure_signature:
                self.providers.memory.remember("failure_signature", {
                    "step": trace_item.get("planned_step"),
                    "attempt_no": trace_item.get("attempt_no"),
                    "failure_signature": failure_signature,
                    "after_state": trace_item.get("after_state"),
                })

    def _emit(self, event_type: EventType, payload: dict[str, Any]) -> None:
        """Emit a runtime event through the event loop."""
        if self.event_loop:
            self.event_loop.enqueue(event_type, payload)

    def _handle_event(self, event: RuntimeEvent) -> None:
        """Default event handler for the event loop.

        This is called when the event loop processes an event.
        Override or extend for custom event handling.
        """
        pass

    def _runtime_meta(
            self, observation: dict[str, Any], action_plan: dict[str, Any]
    ) -> dict[str, Any]:
        """Build runtime metadata for result enrichment."""
        return {
            "host": "HostRuntime",
            "version": "2.0.0",
            "session_id": self.session_id,
            "providers": self.providers.snapshot(),
            "manifests": [m.name for m in self.manifests],
            "capabilities": self.capability_matrix(),
            "observation": observation,
            "action_plan": action_plan,
            "event_loop": self.event_loop.session_state() if self.event_loop else None,
            "timestamp": datetime.now().isoformat(),
        }
