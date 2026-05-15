"""真实京麦桌面验证入口服务。"""

from __future__ import annotations

from pathlib import Path

from jingmai_publish.desktop import RealWindowsUIAAdapter, UIATuningConfig, WindowManager
from jingmai_publish.runtime import (
    HostRuntime,
    JsonlMemoryProvider,
    ProviderRegistry,
    RuntimeLogPersistenceProvider,
)
from jingmai_publish.repositories.runtime_log import RuntimeLogRepository
from jingmai_publish.services.jingmai_workflow import JingmaiWorkflowService
from jingmai_publish.services.task_runner import TaskRunner


class DesktopVerificationService:
    """负责触发真实京麦窗口验证，并由 TaskRunner 驱动执行计划。"""

    def __init__(
        self,
        screenshot_dir: str,
        tuning: UIATuningConfig | None = None,
        runtime_log_repo: RuntimeLogRepository | None = None,
        memory_file: str | None = None,
    ) -> None:
        adapter = RealWindowsUIAAdapter(screenshot_dir=screenshot_dir, tuning=tuning)
        window_manager = WindowManager(adapter)
        self.workflow_service = JingmaiWorkflowService(window_manager)
        self.task_runner = TaskRunner(self.workflow_service)
        memory_target = memory_file or str(Path(screenshot_dir).parent / "memory" / "runtime-memory.jsonl")
        self.runtime = HostRuntime(
            task_runner=self.task_runner,
            providers=ProviderRegistry(
                observation=_DesktopObservationProvider(window_manager),
                action=_DesktopActionProvider(self.task_runner),
                persistence=RuntimeLogPersistenceProvider(runtime_log_repo),
                memory=JsonlMemoryProvider(memory_target),
            ),
        )

    def run(self, step: str = "both", debug: bool = False, **kwargs) -> dict[str, object]:
        if not hasattr(self, "task_runner") or self.task_runner.workflow_service is not self.workflow_service:
            self.task_runner = TaskRunner(self.workflow_service)
        if not hasattr(self, "runtime") or self.runtime.task_runner is not self.task_runner:
            self.runtime = HostRuntime(
                task_runner=self.task_runner,
                providers=ProviderRegistry(
                    observation=_DesktopObservationProvider(self.workflow_service.window_manager),
                    action=_DesktopActionProvider(self.task_runner),
                    persistence=_NullPersistenceProvider(),
                    memory=JsonlMemoryProvider(str(Path("logs/memory/runtime-memory.jsonl"))),
                ),
            )
        return self.runtime.run(step=step, debug=debug, **kwargs)


class _DesktopObservationProvider:
    """Observation provider for desktop runtime alignment."""

    def __init__(self, window_manager: WindowManager) -> None:
        self.window_manager = window_manager

    def observe(self, session: dict[str, object]) -> dict[str, object]:
        return {
            "requested_step": session.get("requested_step"),
            "provider": "desktop_uia",
            "window_keywords": list(self.window_manager.adapter.tuning.window_keywords),
        }


class _DesktopActionProvider:
    """Action provider wrapper for host runtime alignment."""

    def __init__(self, task_runner: TaskRunner) -> None:
        self.task_runner = task_runner

    def execute(self, action_name: str, payload: dict[str, object]) -> dict[str, object]:
        return {
            "action_name": action_name,
            "payload_keys": sorted(payload.keys()),
        }


class _NullPersistenceProvider:
    """No-op persistence provider used by the runtime shell."""

    def persist_event(self, event_type: str, payload: dict[str, object]) -> None:
        return None
