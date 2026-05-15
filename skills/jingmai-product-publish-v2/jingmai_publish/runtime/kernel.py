"""Host runtime wrapper for provider-oriented execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from jingmai_publish.runtime.providers import ProviderRegistry


@dataclass(slots=True)
class HostRuntime:
    """Wrap TaskRunner with provider-oriented metadata and event output."""

    task_runner: Any
    providers: ProviderRegistry

    def run(self, step: str = "both", debug: bool = False, **kwargs) -> dict[str, object]:
        """Run a task through the host runtime."""

        payload = kwargs
        if self.providers.channel is not None:
            payload = self.providers.channel.normalize_payload(dict(kwargs))

        session_seed = {
            "requested_step": step,
            "payload_keys": sorted(payload.keys()),
            "providers": self.providers.snapshot(),
        }
        observation = self.providers.observation.observe(session_seed) if self.providers.observation is not None else {}
        if self.providers.persistence is not None:
            self.providers.persistence.persist_event(
                "runtime_started",
                {"step": step, "observation": observation, "payload_keys": sorted(payload.keys())},
            )
        if self.providers.memory is not None:
            self.providers.memory.remember(
                "runtime_started",
                {"step": step, "payload_keys": sorted(payload.keys()), "observation": observation},
            )
        action_plan = (
            self.providers.action.execute(step, dict(payload))
            if self.providers.action is not None
            else {"action_name": step, "payload_keys": sorted(payload.keys())}
        )
        if self.providers.persistence is not None:
            self.providers.persistence.persist_event("runtime_action_plan", action_plan)

        result = self.task_runner.run(step=step, debug=debug, **payload)
        result["runtime"] = {
            "host": "HostRuntime",
            "providers": self.providers.snapshot(),
            "observation": observation,
            "action_plan": action_plan,
        }

        if self.providers.persistence is not None:
            self.providers.persistence.persist_event(
                "runtime_completed",
                {"step": step, "halted": result.get("session", {}).get("halted"), "keys": sorted(result.keys())},
            )
        if self.providers.memory is not None:
            session = result.get("session", {})
            self.providers.memory.remember(
                "runtime_completed",
                {
                    "step": step,
                    "halted": session.get("halted"),
                    "page_state": session.get("page_state"),
                    "completed_steps": session.get("completed_steps", []),
                },
            )
            for trace_item in session.get("trace", []):
                failure_signature = trace_item.get("failure_signature")
                if failure_signature:
                    self.providers.memory.remember(
                        "failure_signature",
                        {
                            "step": trace_item.get("planned_step"),
                            "attempt_no": trace_item.get("attempt_no"),
                            "failure_signature": failure_signature,
                            "after_state": trace_item.get("after_state"),
                        },
                    )
        return result
