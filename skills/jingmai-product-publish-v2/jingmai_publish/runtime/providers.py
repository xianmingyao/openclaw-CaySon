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


@dataclass(slots=True)
class ProviderRegistry:
    """Lightweight provider registry for the host runtime."""

    observation: ObservationProvider | None = None
    action: ActionProvider | None = None
    persistence: PersistenceProvider | None = None
    channel: ChannelProvider | None = None
    memory: MemoryProvider | None = None
    extras: dict[str, Any] = field(default_factory=dict)

    def snapshot(self) -> dict[str, Any]:
        """Return a structured view of the registered providers."""

        return {
            "observation": type(self.observation).__name__ if self.observation is not None else None,
            "action": type(self.action).__name__ if self.action is not None else None,
            "persistence": type(self.persistence).__name__ if self.persistence is not None else None,
            "channel": type(self.channel).__name__ if self.channel is not None else None,
            "memory": type(self.memory).__name__ if self.memory is not None else None,
            "extras": sorted(self.extras.keys()),
        }
