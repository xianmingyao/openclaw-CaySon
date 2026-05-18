"""Tests for BL-100 Runtime Event Loop."""

from __future__ import annotations

import time
from unittest.mock import MagicMock

from jingmai_publish.runtime.event_loop import (
    EventStatus,
    EventType,
    RuntimeEvent,
    RuntimeEventLoop,
)


class TestRuntimeEvent:
    """RuntimeEvent dataclass tests."""

    def test_default_event_has_pending_status(self):
        event = RuntimeEvent(event_type=EventType.TASK_SUBMITTED)
        assert event.status == EventStatus.PENDING
        assert event.event_id.startswith("evt-")
        assert event.payload == {}
        assert event.error is None

    def test_event_serialization(self):
        event = RuntimeEvent(
            event_type=EventType.TASK_COMPLETED,
            payload={"step": "t1", "result": "ok"},
        )
        assert event.event_type == EventType.TASK_COMPLETED
        assert event.payload["step"] == "t1"


class TestRuntimeEventLoop:
    """RuntimeEventLoop core functionality tests."""

    def test_create_loop(self):
        loop = RuntimeEventLoop()
        assert loop.session is not None
        assert loop.session.session_id.startswith("loop-")
        assert not loop.session.is_running

    def test_custom_session_id(self):
        loop = RuntimeEventLoop(session_id="my-custom-session")
        assert loop.session.session_id == "my-custom-session"

    def test_enqueue_returns_event_id(self):
        loop = RuntimeEventLoop()
        event_id = loop.enqueue(EventType.TASK_SUBMITTED, {"step": "t1"})
        assert event_id.startswith("evt-")

    def test_enqueue_increments_count(self):
        loop = RuntimeEventLoop()
        loop.enqueue(EventType.TASK_SUBMITTED, {"step": "t1"})
        loop.enqueue(EventType.TASK_SUBMITTED, {"step": "t2"})
        assert loop.session.event_count_total == 2

    def test_schedule_returns_event_id(self):
        loop = RuntimeEventLoop()
        event_id = loop.schedule(
            EventType.TASK_SUBMITTED,
            {"step": "delayed"},
            delay_seconds=0.01,
        )
        assert event_id.startswith("evt-")

    def test_schedule_increments_count(self):
        loop = RuntimeEventLoop()
        loop.schedule(EventType.TASK_SUBMITTED, {"step": "d1"}, delay_seconds=0.01)
        loop.schedule(EventType.TASK_SUBMITTED, {"step": "d2"}, delay_seconds=0.02)
        assert loop.session.event_count_total == 2

    def test_start_stop_lifecycle(self):
        loop = RuntimeEventLoop()
        loop.start()
        assert loop.session.is_running
        assert loop.session.started_at is not None

        loop.stop()
        assert not loop.session.is_running
        assert loop.session.stopped_at is not None

    def test_pause_resume(self):
        loop = RuntimeEventLoop()
        loop.start()
        loop.pause()
        assert loop.session.is_paused

        loop.resume()
        assert not loop.session.is_paused

        loop.stop()

    def test_session_state_snapshot(self):
        loop = RuntimeEventLoop(session_id="test-snapshot")
        state = loop.session_state()
        assert state["session_id"] == "test-snapshot"
        assert "is_running" in state
        assert "event_count_total" in state
        assert "event_count_completed" in state
        assert "event_count_failed" in state

    def test_subscriber_notified_on_event(self):
        loop = RuntimeEventLoop()
        handler = MagicMock()
        loop._handler = handler
        loop.enqueue(EventType.TASK_SUBMITTED, {"step": "t1"})
        # Process one event manually
        loop.start()

        # Wait briefly for processing
        time.sleep(0.2)

        loop.stop()
        assert handler.called

    def test_subscriber_callback(self):
        loop = RuntimeEventLoop()
        received_events = []

        def on_event(event: RuntimeEvent) -> None:
            received_events.append(event.event_type)

        loop.subscribe(on_event)
        # Use a handler that just processes
        loop._handler = lambda e: None
        loop.start()
        loop.enqueue(EventType.TASK_SUBMITTED, {"step": "t1"})
        time.sleep(0.3)
        loop.stop()

        assert len(received_events) >= 1

    def test_event_history(self):
        loop = RuntimeEventLoop()
        loop._handler = lambda e: None
        loop.start()
        loop.enqueue(EventType.TASK_SUBMITTED, {"step": "t1"})
        loop.enqueue(EventType.TASK_STARTED, {"step": "t1"})

        time.sleep(0.3)
        loop.stop()

        history = loop.event_history()
        assert len(history) >= 2
        for entry in history:
            assert "event_id" in entry
            assert "event_type" in entry
            assert "status" in entry

    def test_idempotent_start(self):
        """Starting an already-running loop should be safe."""
        loop = RuntimeEventLoop()
        loop.start()
        loop.start()  # Should not crash
        loop.stop()

    def test_idempotent_stop(self):
        """Stopping an already-stopped loop should be safe."""
        loop = RuntimeEventLoop()
        loop.start()
        loop.stop()
        loop.stop()  # Should not crash


class TestEventTypeEnum:
    """EventType enumeration covers the full observe→decide→act→verify→repeat cycle."""

    def test_all_event_types_exist(self):
        expected = {
            "task_submitted",
            "task_started",
            "observation_collected",
            "action_plan_generated",
            "action_executed",
            "verification_completed",
            "task_completed",
            "task_failed",
            "reflection_recorded",
            "runtime_stopped",
            "runtime_paused",
            "runtime_resumed",
        }
        actual = {e.value for e in EventType}
        assert expected == actual
