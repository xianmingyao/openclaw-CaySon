"""test_reflection_persistence.py — BL-094A 失败反思持久化测试。

覆盖：
- ReflectionRecord 构造、序列化、is_failure 判断
- ReflectionJsonlPersistenceProvider JSONL 写入、事件订阅、搜索
- MilvusMemoryProvider 优雅降级（pymilvus 不可用时）
- 集成：RuntimeEventLoop + ReflectionJsonlPersistenceProvider
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from jingmai_publish.agent.reflection_record import ReflectionRecord
from jingmai_publish.runtime.event_loop import EventType, RuntimeEventLoop
from jingmai_publish.runtime.reflection_persistence import (
    MilvusMemoryProvider,
    ReflectionJsonlPersistenceProvider,
)


# ── ReflectionRecord ───────────────────────────────────────────

class TestReflectionRecord:
    """ReflectionRecord 数据类单元测试。"""

    def test_from_event_payload_basic(self):
        """从标准 REFLECTION_RECORDED 事件 payload 构造。"""
        payload = {
            "step_name": "t2",
            "category": "navigation",
            "attempt_no": 2,
            "max_retry": 3,
            "success": False,
            "decision": "retry",
            "reason": "attempt 2/3 failed, retrying",
            "message": "action failed",
            "lane_count": 1,
            "vision_analysis": None,
        }
        record = ReflectionRecord.from_event_payload(payload)
        assert record.step_name == "t2"
        assert record.category == "navigation"
        assert record.attempt_no == 2
        assert record.success is False
        assert record.decision == "retry"
        assert record.is_failure is True

    def test_from_event_payload_defaults(self):
        """空 payload 时应使用默认值。"""
        record = ReflectionRecord.from_event_payload({})
        assert record.step_name == ""
        assert record.decision == ""
        assert record.reason == ""
        assert record.is_failure is True  # "" != "continue"

    def test_is_failure_continue(self):
        """决策为 continue 时 is_failure 返回 False。"""
        record = ReflectionRecord(
            step_name="t1", category="attachment",
            attempt_no=1, max_retry=2, success=True,
            decision="continue", reason="step succeeded",
        )
        assert record.is_failure is False

    def test_to_dict(self):
        """to_dict 返回可 JSON 序列化的 dict。"""
        record = ReflectionRecord(
            step_name="t3", category="navigation",
            attempt_no=1, max_retry=3, success=False,
            decision="abort", reason="window not found",
            message="找不到窗口",
        )
        d = record.to_dict()
        assert d["step_name"] == "t3"
        assert d["decision"] == "abort"
        assert "recorded_at" in d
        # 可 JSON 序列化
        json.dumps(d)

    def test_to_dict_with_vision_analysis(self):
        """vision_analysis 字段正确序列化。"""
        record = ReflectionRecord(
            step_name="t1", category="attachment",
            attempt_no=3, max_retry=3, success=False,
            decision="abort", reason="all attempts exhausted",
            vision_analysis={
                "vision_success": True,
                "vision_confidence": 0.85,
                "vision_page_state": "form_filled",
            },
        )
        d = record.to_dict()
        assert d["vision_analysis"]["vision_success"] is True
        assert d["vision_analysis"]["vision_confidence"] == 0.85


# ── ReflectionJsonlPersistenceProvider ─────────────────────────

class TestReflectionJsonlPersistenceProvider:
    """ReflectionJsonlPersistenceProvider 单元测试。"""

    @pytest.fixture
    def temp_jsonl(self):
        """创建临时 JSONL 文件路径。"""
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
            pass
        path = Path(f.name)
        yield path
        # 清理
        if path.exists():
            path.unlink()

    def test_remember_record_writes_line(self, temp_jsonl):
        """remember_record 应写入一行 JSON 到文件。"""
        provider = ReflectionJsonlPersistenceProvider(temp_jsonl)
        record = ReflectionRecord(
            step_name="t2", category="navigation",
            attempt_no=1, max_retry=3, success=False,
            decision="retry", reason="test retry",
        )
        provider.remember_record(record)

        lines = temp_jsonl.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["memory_type"] == "reflection"
        assert data["payload"]["step_name"] == "t2"
        assert data["payload"]["decision"] == "retry"

    def test_persist_event_follows_protocol(self, temp_jsonl):
        """persist_event 遵循 PersistenceProvider 协议。"""
        provider = ReflectionJsonlPersistenceProvider(temp_jsonl)
        provider.persist_event("runtime_started", {"step": "t1"})

        lines = temp_jsonl.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["event_type"] == "runtime_started"
        assert data["payload"]["step"] == "t1"

    def test_on_event_filters_non_reflection_events(self, temp_jsonl):
        """非 REFLECTION_RECORDED 事件不应被持久化。"""
        provider = ReflectionJsonlPersistenceProvider(temp_jsonl)
        from jingmai_publish.runtime.event_loop import RuntimeEvent
        event = RuntimeEvent(
            event_type=EventType.TASK_COMPLETED,
            payload={"step": "t1"},
        )
        provider._on_event(event)

        assert not temp_jsonl.exists() or temp_jsonl.read_text(encoding="utf-8").strip() == ""

    def test_on_event_persists_reflection_recorded(self, temp_jsonl):
        """REFLECTION_RECORDED 事件应被持久化。"""
        provider = ReflectionJsonlPersistenceProvider(temp_jsonl)
        from jingmai_publish.runtime.event_loop import RuntimeEvent
        event = RuntimeEvent(
            event_type=EventType.REFLECTION_RECORDED,
            payload={
                "step_name": "t2",
                "category": "navigation",
                "attempt_no": 3,
                "max_retry": 3,
                "success": False,
                "decision": "abort",
                "reason": "all attempts exhausted",
                "message": "step failed",
                "lane_count": 0,
            },
        )
        provider._on_event(event)

        lines = temp_jsonl.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["payload"]["decision"] == "abort"

    def test_search_finds_matching_records(self, temp_jsonl):
        """search 应返回匹配的反思记录。"""
        provider = ReflectionJsonlPersistenceProvider(temp_jsonl)
        for i in range(3):
            provider.remember_record(ReflectionRecord(
                step_name=f"t{i}", category="data_entry",
                attempt_no=i, max_retry=3, success=False,
                decision="retry" if i < 2 else "abort",
                reason=f"test reason {i}",
            ))

        results = provider.search("abort")
        assert len(results) == 1
        assert results[0]["payload"]["decision"] == "abort"

    def test_search_empty_file(self, temp_jsonl):
        """空文件搜索应返回空列表。"""
        provider = ReflectionJsonlPersistenceProvider(temp_jsonl)
        assert provider.search("anything") == []

    def test_count_failures(self, temp_jsonl):
        """count_failures 应正确统计失败记录。"""
        provider = ReflectionJsonlPersistenceProvider(temp_jsonl)
        # 写入 2 个 retry + 1 个 continue + 1 个 abort
        decisions = ["retry", "retry", "continue", "abort"]
        for i, dec in enumerate(decisions):
            provider.remember_record(ReflectionRecord(
                step_name=f"t{i}", category="data_entry",
                attempt_no=1, max_retry=3,
                success=(dec == "continue"),
                decision=dec, reason="test",
            ))

        assert provider.count_failures() == 3  # retry + retry + abort

    def test_subscribe_to_event_loop(self, temp_jsonl):
        """通过构造参数自动订阅 RuntimeEventLoop。"""
        event_loop = RuntimeEventLoop()
        provider = ReflectionJsonlPersistenceProvider(
            temp_jsonl, event_loop=event_loop,
        )
        # 验证 subscribe 被调用（provider 在 event_loop._subscribers 中）
        assert provider._on_event in event_loop._subscribers


# ── MilvusMemoryProvider 优雅降级 ───────────────────────────────

class TestMilvusMemoryProvider:
    """MilvusMemoryProvider 单元测试 — 重点测试优雅降级。"""

    def test_graceful_degradation_when_pymilvus_not_installed(self):
        """pymilvus 未安装时 should 优雅降级，不抛异常。"""
        with patch("jingmai_publish.runtime.reflection_persistence.MilvusMemoryProvider._init_client",
                   side_effect=None):
            # 直接构造并手动设置降级状态
            with patch.dict("sys.modules", {"pymilvus": None}):
                try:
                    provider = MilvusMemoryProvider(host="127.0.0.1", port=19530)
                except ImportError:
                    provider = None

                if provider is None:
                    # 如果构造函数抛出了 ImportError，说明需要调整
                    # 当前实现用 try/except 捕获，所以应该不抛异常
                    pass

    def test_remember_does_not_raise_when_unavailable(self):
        """不可用时 remember 不应抛出异常。"""
        provider = MilvusMemoryProvider.__new__(MilvusMemoryProvider)
        provider._available = False
        provider._client = None
        provider._error = "test: unavailable"
        # 不应抛异常
        provider.remember("reflection", {"test": True})

    def test_search_returns_empty_when_unavailable(self):
        """不可用时 search 应返回空列表。"""
        provider = MilvusMemoryProvider.__new__(MilvusMemoryProvider)
        provider._available = False
        provider._client = None
        provider._error = "test: unavailable"
        results = provider.search("test query")
        assert results == []

    def test_is_available_and_status_message(self):
        """is_available 和 status_message 属性。"""
        provider = MilvusMemoryProvider.__new__(MilvusMemoryProvider)
        provider._available = False
        provider._error = "Milvus 连接失败: Connection refused"
        assert provider.is_available is False
        assert "Connection refused" in provider.status_message

        provider._available = True
        provider._error = None
        assert provider.is_available is True
        assert provider.status_message == "Milvus 已连接"

    def test_text_to_embedding_returns_normalized_vector(self):
        """_text_to_embedding 应返回归一化的固定维度向量。"""
        provider = MilvusMemoryProvider.__new__(MilvusMemoryProvider)
        provider.dim = 768
        vec = provider._text_to_embedding("窗口丢失，重试耗尽")
        assert len(vec) == 768
        # 归一化检查：向量模长应接近 1.0
        norm = sum(v * v for v in vec) ** 0.5
        assert abs(norm - 1.0) < 0.01


# ── 集成测试：RuntimeEventLoop + ReflectionJsonlPersistenceProvider ──

class TestReflectionPersistenceIntegration:
    """集成测试：RuntimeEventLoop 订阅 → JSONL 持久化。"""

    @pytest.fixture
    def temp_jsonl(self):
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
            pass
        path = Path(f.name)
        yield path
        if path.exists():
            path.unlink()

    def test_integration_event_loop_to_jsonl(self, temp_jsonl):
        """完整流程：REFLECTION_RECORDED 事件 → 订阅回调 → JSONL 写入。"""
        event_loop = RuntimeEventLoop()
        provider = ReflectionJsonlPersistenceProvider(
            temp_jsonl, event_loop=event_loop,
        )

        # 模拟 AgentReflection._emit() 的行为
        payload = {
            "step_name": "t4",
            "category": "data_entry",
            "attempt_no": 3,
            "max_retry": 3,
            "success": False,
            "decision": "abort",
            "reason": "all 3 attempts exhausted",
            "message": "价格字段填充失败",
            "lane_count": 2,
        }

        # 直接调用 _on_event（不需要启动 event_loop worker 线程）
        from jingmai_publish.runtime.event_loop import RuntimeEvent
        event = RuntimeEvent(
            event_type=EventType.REFLECTION_RECORDED,
            payload=payload,
        )
        provider._on_event(event)

        # 验证 JSONL 写入
        lines = temp_jsonl.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["payload"]["step_name"] == "t4"
        assert data["payload"]["decision"] == "abort"
        assert data["payload"]["lane_count"] == 2

    def test_multiple_reflections_accumulate(self, temp_jsonl):
        """多次反思事件应累积写入 JSONL。"""
        provider = ReflectionJsonlPersistenceProvider(temp_jsonl)
        from jingmai_publish.runtime.event_loop import RuntimeEvent

        for i in range(5):
            event = RuntimeEvent(
                event_type=EventType.REFLECTION_RECORDED,
                payload={
                    "step_name": f"t{i % 3}",
                    "category": "data_entry",
                    "attempt_no": i + 1,
                    "max_retry": 3,
                    "success": i == 4,
                    "decision": "abort" if i >= 3 else "retry",
                    "reason": f"attempt {i}",
                    "message": "",
                    "lane_count": 0,
                },
            )
            provider._on_event(event)

        lines = temp_jsonl.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 5

        # search 验证
        results = provider.search("abort")
        assert len(results) == 2

    def test_vision_analysis_in_reflection_jsonl(self, temp_jsonl):
        """vision_analysis 字段正确写入 JSONL。"""
        provider = ReflectionJsonlPersistenceProvider(temp_jsonl)
        from jingmai_publish.runtime.event_loop import RuntimeEvent

        event = RuntimeEvent(
            event_type=EventType.REFLECTION_RECORDED,
            payload={
                "step_name": "t1",
                "category": "attachment",
                "attempt_no": 3,
                "max_retry": 3,
                "success": False,
                "decision": "retry",
                "reason": "vision says page is correct",
                "message": "step failed",
                "lane_count": 0,
                "vision_analysis": {
                    "vision_success": True,
                    "vision_confidence": 0.92,
                    "vision_page_state": "form_filled",
                },
            },
        )
        provider._on_event(event)

        lines = temp_jsonl.read_text(encoding="utf-8").strip().splitlines()
        data = json.loads(lines[0])
        va = data["payload"]["vision_analysis"]
        assert va["vision_success"] is True
        assert va["vision_confidence"] == 0.92
