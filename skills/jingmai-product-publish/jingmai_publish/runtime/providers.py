"""Provider layer aligned with the implementation plan."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


class ObservationProvider(Protocol):
    """Supplies structured observations for the runtime host."""

    def observe(self, session: dict[str, Any]) -> dict[str, Any]:
        """Return current observation payload."""


class ActionProvider(Protocol):
    """Executes a planned action inside the host runtime."""

    def execute(self, action_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Execute an action and return a structured result."""


class PersistenceProvider(Protocol):
    """Persists runtime events and artifacts."""

    def persist_event(self, event_type: str, payload: dict[str, Any]) -> None:
        """Persist a runtime event."""


class ChannelProvider(Protocol):
    """Delivers inbound/outbound task payloads."""

    def normalize_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Normalize inbound payload into the host contract."""


class MemoryProvider(Protocol):
    """Stores and retrieves execution memory."""

    def remember(self, memory_type: str, payload: dict[str, Any]) -> None:
        """Persist a memory item."""

    def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """Return matching memory items."""


class VisionProvider(Protocol):
    """Phase C: 视觉分析能力 — 截图分析、元素定位、前后对比。

    对应 BL-092 OllamaVisionProvider，但协议层与具体实现解耦。
    """

    def analyze_screenshot(self, image_path: str, prompt: str | None = None) -> Any:
        """分析单张截图，返回 VisionAnalysis 等价结构。"""

    def locate_element(self, image_path: str, description: str) -> Any:
        """在截图中定位指定元素，返回 VisionAnalysis 含 bbox/point。"""

    def compare_screenshots(
            self, before_path: str, after_path: str, prompt: str | None = None
    ) -> Any:
        """对比两张截图，识别变化。"""


class GroundingProvider(Protocol):
    """Phase C: 三路元素定位仲裁 — UIA/Vision/Anchor 候选融合。

    对应 BL-095 ThreeWayGroundingProvider。
    """

    def ground(
            self,
            target: str,
            window_handle: str = "",
            screenshot_path: str | None = None,
            page_text: str = "",
            target_type: str = "automation_id",
    ) -> Any:
        """执行三路 grounding 仲裁，返回 GroundingResult。"""


@dataclass(slots=True)
class ProviderRegistry:
    """Lightweight provider registry for the host runtime."""

    observation: ObservationProvider | None = None
    action: ActionProvider | None = None
    persistence: PersistenceProvider | None = None
    channel: ChannelProvider | None = None
    memory: MemoryProvider | None = None
    vision: VisionProvider | None = None
    grounding: GroundingProvider | None = None
    extras: dict[str, Any] = field(default_factory=dict)

    def snapshot(self) -> dict[str, Any]:
        """Return a structured view of the registered providers."""

        return {
            "observation": type(self.observation).__name__ if self.observation is not None else None,
            "action": type(self.action).__name__ if self.action is not None else None,
            "persistence": type(self.persistence).__name__ if self.persistence is not None else None,
            "channel": type(self.channel).__name__ if self.channel is not None else None,
            "memory": type(self.memory).__name__ if self.memory is not None else None,
            "vision": type(self.vision).__name__ if self.vision is not None else None,
            "grounding": type(self.grounding).__name__ if self.grounding is not None else None,
            "extras": sorted(self.extras.keys()),
        }
