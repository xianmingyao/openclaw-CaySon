"""SightFlow-style runtime event loop with queue, schedule, and session state.

Aligns with sightflow-desktop-agent Host runtime queue pattern:
- enqueue: submit events into the processing queue
- schedule: delayed event submission
- stop: graceful shutdown
- session state: snapshot current runtime state

Also aligns with UI-TARS-desktop event stream pattern:
- Event types mirror the observe→decide→act→verify→repeat cycle
- Each event carries before/after state for traceability
"""

from __future__ import annotations

import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from queue import Queue
from threading import Event, Lock, Thread
from typing import Any, Callable


class EventStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EventType(str, Enum):
    """Runtime event types aligned with sightflow + UI-TARS patterns."""

    TASK_SUBMITTED = "task_submitted"
    TASK_STARTED = "task_started"
    OBSERVATION_COLLECTED = "observation_collected"
    ACTION_PLAN_GENERATED = "action_plan_generated"
    ACTION_EXECUTED = "action_executed"
    VERIFICATION_COMPLETED = "verification_completed"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    REFLECTION_RECORDED = "reflection_recorded"
    RUNTIME_STOPPED = "runtime_stopped"
    RUNTIME_PAUSED = "runtime_paused"
    RUNTIME_RESUMED = "runtime_resumed"


@dataclass(slots=True)
class RuntimeEvent:
    """A single event in the runtime event stream."""

    event_id: str = field(default_factory=lambda: f"evt-{uuid.uuid4().hex[:12]}")
    event_type: EventType = EventType.TASK_SUBMITTED
    payload: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    processed_at: datetime | None = None
    status: EventStatus = EventStatus.PENDING
    error: str | None = None


@dataclass(slots=True)
class ScheduleEntry:
    """A delayed event scheduled for future processing."""

    event: RuntimeEvent
    fire_at: datetime


@dataclass(slots=True)
class LoopSessionState:
    """Current runtime loop session state (aligned with sightflow session state)."""

    session_id: str = field(default_factory=lambda: f"loop-{uuid.uuid4().hex[:12]}")
    started_at: datetime | None = None
    stopped_at: datetime | None = None
    is_running: bool = False
    is_paused: bool = False
    event_count_total: int = 0
    event_count_completed: int = 0
    event_count_failed: int = 0
    current_event_id: str | None = None
    last_page_state: str | None = None
    window_handle: str | None = None

    def snapshot(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "stopped_at": self.stopped_at.isoformat() if self.stopped_at else None,
            "is_running": self.is_running,
            "is_paused": self.is_paused,
            "event_count_total": self.event_count_total,
            "event_count_completed": self.event_count_completed,
            "event_count_failed": self.event_count_failed,
            "current_event_id": self.current_event_id,
            "last_page_state": self.last_page_state,
            "window_handle": self.window_handle,
        }


class RuntimeEventLoop:
    """SightFlow-compatible runtime event loop.

    Manages the observe→decide→act→verify→repeat cycle through
    a thread-safe event queue with scheduling, stop, and session tracking.

    Usage::

        loop = RuntimeEventLoop(handler=my_handler, max_concurrent=1)
        loop.start()
        loop.enqueue(EventType.TASK_SUBMITTED, {"step": "t1"})
        # ... events get processed by handler ...
        loop.stop()
    """

    def __init__(
            self,
            handler: Callable[[RuntimeEvent], None] | None = None,
            *,
            max_concurrent: int = 1,
            session_id: str | None = None,
    ) -> None:
        self._queue: Queue[RuntimeEvent] = Queue()
        self._schedule_entries: list[ScheduleEntry] = []
        self._history: deque[RuntimeEvent] = deque(maxlen=1000)
        self._lock = Lock()
        self._stop_event = Event()
        self._pause_event = Event()
        self._pause_event.set()  # not paused initially
        self._worker_thread: Thread | None = None
        self._handler = handler
        self._max_concurrent = max(max_concurrent, 1)
        self._active_handlers: list[Thread] = []

        self.session = LoopSessionState(
            session_id=session_id or f"loop-{uuid.uuid4().hex[:12]}"
        )

        # External observers can subscribe to event lifecycles
        self._subscribers: list[Callable[[RuntimeEvent], None]] = []

    # ── public API ──────────────────────────────────────────────

    def enqueue(self, event_type: EventType, payload: dict[str, Any] | None = None) -> str:
        """Submit an event for immediate processing. Returns event_id."""
        event = RuntimeEvent(
            event_type=event_type,
            payload=payload or {},
        )
        self._queue.put(event)
        with self._lock:
            self.session.event_count_total += 1
        return event.event_id

    def schedule(
            self,
            event_type: EventType,
            payload: dict[str, Any] | None = None,
            *,
            delay_seconds: float = 0.0,
    ) -> str:
        """Schedule an event for future processing. Returns event_id."""
        event = RuntimeEvent(
            event_type=event_type,
            payload=payload or {},
        )
        fire_at = datetime.now() + timedelta(seconds=delay_seconds)
        with self._lock:
            self._schedule_entries.append(ScheduleEntry(event=event, fire_at=fire_at))
            self._schedule_entries.sort(key=lambda entry: entry.fire_at)
            self.session.event_count_total += 1
        return event.event_id

    def subscribe(self, callback: Callable[[RuntimeEvent], None]) -> None:
        """Subscribe to event lifecycle notifications."""
        self._subscribers.append(callback)

    def start(self) -> None:
        """Start the event loop worker thread."""
        if self._worker_thread is not None and self._worker_thread.is_alive():
            return
        self._stop_event.clear()
        self._pause_event.set()
        self.session.is_running = True
        self.session.started_at = datetime.now()
        self._worker_thread = Thread(target=self._run_loop, daemon=True, name="runtime-event-loop")
        self._worker_thread.start()

    def stop(self, *, timeout: float = 10.0) -> None:
        """Gracefully stop the event loop."""
        self._stop_event.set()
        self._pause_event.set()  # unpause so the loop can exit
        if self._worker_thread is not None:
            self._worker_thread.join(timeout=timeout)
        self.session.is_running = False
        self.session.stopped_at = datetime.now()
        stop_event = RuntimeEvent(
            event_type=EventType.RUNTIME_STOPPED,
            payload={"session_snapshot": self.session.snapshot()},
        )
        self._record_event(stop_event)
        self._notify(stop_event)

    def pause(self) -> None:
        """Pause event processing. Enqueued events stay queued."""
        self._pause_event.clear()
        self.session.is_paused = True

    def resume(self) -> None:
        """Resume event processing."""
        self._pause_event.set()
        self.session.is_paused = False

    def session_state(self) -> dict[str, Any]:
        """Return current session snapshot."""
        with self._lock:
            return self.session.snapshot()

    def event_history(self, *, limit: int = 50) -> list[dict[str, Any]]:
        """Return recent event history."""
        with self._lock:
            return [
                {
                    "event_id": e.event_id,
                    "event_type": e.event_type.value,
                    "status": e.status.value,
                    "created_at": e.created_at.isoformat(),
                    "processed_at": e.processed_at.isoformat() if e.processed_at else None,
                    "error": e.error,
                }
                for e in list(self._history)[-limit:]
            ]

    # ── internal ────────────────────────────────────────────────

    def _run_loop(self) -> None:
        """Main event loop: dequeue → process → repeat until stopped."""
        while not self._stop_event.is_set():
            # Wait if paused
            self._pause_event.wait()

            # Process any due scheduled events
            self._drain_scheduled()

            # Get next event (with short timeout to check stop/pause)
            try:
                event = self._queue.get(timeout=0.5)
            except Exception:  # queue.Empty is platform-dependent
                continue

            if self._stop_event.is_set():
                break

            self._process_event(event)

    def _drain_scheduled(self) -> None:
        """Move due scheduled events into the main queue."""
        now = datetime.now()
        with self._lock:
            due: list[RuntimeEvent] = []
            remaining: list[ScheduleEntry] = []
            for entry in self._schedule_entries:
                if entry.fire_at <= now:
                    due.append(entry.event)
                else:
                    remaining.append(entry)
            self._schedule_entries = remaining

        for event in due:
            self._queue.put(event)

    def _process_event(self, event: RuntimeEvent) -> None:
        """Process a single event through the handler chain."""
        event.status = EventStatus.PROCESSING
        self.session.current_event_id = event.event_id

        try:
            if self._handler is not None:
                self._handler(event)
            event.status = EventStatus.COMPLETED
            with self._lock:
                self.session.event_count_completed += 1
        except Exception as exc:
            event.status = EventStatus.FAILED
            event.error = str(exc)
            with self._lock:
                self.session.event_count_failed += 1

        event.processed_at = datetime.now()
        self._record_event(event)
        self._notify(event)
        self.session.current_event_id = None

    def _record_event(self, event: RuntimeEvent) -> None:
        """Record event in history for audit."""
        with self._lock:
            self._history.append(event)

    def _notify(self, event: RuntimeEvent) -> None:
        """Notify subscribers of event lifecycle changes."""
        for subscriber in self._subscribers:
            try:
                subscriber(event)
            except Exception:
                pass  # subscriber failures must not crash the loop
