"""BL-094A: 失败反思持久化 — JSONL 本地写入 + Milvus 向量存储。

ReflectionJsonlPersistenceProvider:
  订阅 RuntimeEventLoop，将 REFLECTION_RECORDED 事件写入 JSONL 文件。

MilvusMemoryProvider:
  实现 MemoryProvider 协议，将反思记录写入 Milvus 向量数据库。
  pymilvus 为可选依赖，不可用时优雅降级（仅 JSONL 可用）。
"""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from jingmai_publish.agent.reflection_record import ReflectionRecord
from jingmai_publish.runtime.event_loop import EventType, RuntimeEvent, RuntimeEventLoop


# ── Reflection JSONL 持久化 ──────────────────────────────────────

class ReflectionJsonlPersistenceProvider:
    """将 REFLECTION_RECORDED 事件持久化到本地 JSONL 文件。

    通过 RuntimeEventLoop.subscribe() 订阅事件，自动写入。
    遵循 PersistenceProvider 协议（persist_event 方法），
    同时也支持直接调用 remember_record()。

    用法::

        provider = ReflectionJsonlPersistenceProvider("logs/memory/reflection-memory.jsonl")
        event_loop.subscribe(provider._on_event)
    """

    def __init__(
            self,
            target_file: str | Path,
            *,
            event_loop: RuntimeEventLoop | None = None,
    ) -> None:
        self.target_file = Path(target_file)
        self.target_file.parent.mkdir(parents=True, exist_ok=True)

        if event_loop is not None:
            event_loop.subscribe(self._on_event)

    # ── PersistenceProvider 协议 ──

    def persist_event(self, event_type: str, payload: dict[str, Any]) -> None:
        """持久化任意运行时事件（PersistenceProvider 协议）。"""
        record = {
            "event_type": event_type,
            "recorded_at": datetime.now().isoformat(timespec="seconds"),
            "payload": self._normalize(payload),
        }
        self._write_line(record)

    # ── ReflectionRecord 专用接口 ──

    def remember_record(self, record: ReflectionRecord) -> None:
        """持久化一条 ReflectionRecord。"""
        self._write_line({
            "memory_type": "reflection",
            "created_at": record.recorded_at,
            "payload": record.to_dict(),
        })

    # ── 事件订阅 ──

    def _on_event(self, event: RuntimeEvent) -> None:
        """RuntimeEventLoop 订阅回调：只持久化 REFLECTION_RECORDED 事件。"""
        if event.event_type != EventType.REFLECTION_RECORDED:
            return
        record = ReflectionRecord.from_event_payload(event.payload)
        self.remember_record(record)

    # ── 查询 ──

    def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """从 JSONL 中搜索匹配的反思记录。"""
        if not self.target_file.exists():
            return []

        matched: list[dict[str, Any]] = []
        lowered = query.lower()
        lines = self.target_file.read_text(encoding="utf-8").splitlines()
        for raw_line in reversed(lines):
            if not raw_line.strip():
                continue
            try:
                record = json.loads(raw_line)
            except json.JSONDecodeError:
                continue
            haystack = json.dumps(record, ensure_ascii=False).lower()
            if lowered in haystack:
                matched.append(record)
            if len(matched) >= limit:
                break
        return matched

    def count_failures(self) -> int:
        """统计 JSONL 中失败记录数量。"""
        if not self.target_file.exists():
            return 0
        count = 0
        for line in self.target_file.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            payload = record.get("payload", {})
            if payload.get("decision") != "continue":
                count += 1
        return count

    # ── 内部方法 ──

    def _write_line(self, data: dict[str, Any]) -> None:
        """追加一行 JSON 到目标文件。"""
        with self.target_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(data, ensure_ascii=False, default=str) + "\n")

    @staticmethod
    def _normalize(payload: dict[str, Any]) -> dict[str, Any]:
        """标准化 payload 中的非 JSON 类型。"""
        normalized: dict[str, Any] = {}
        for key, value in payload.items():
            if is_dataclass(value):
                normalized[key] = asdict(value)
            elif isinstance(value, Path):
                normalized[key] = str(value)
            else:
                normalized[key] = value
        return normalized


# ── Milvus 向量存储 ─────────────────────────────────────────────

class MilvusMemoryProvider:
    """Milvus 向量数据库 — 反思记录的语义检索存储。

    实现 MemoryProvider 协议 (remember + search)。
    pymilvus 为可选依赖，不可用时所有操作优雅降级为无操作。

    用法::

        provider = MilvusMemoryProvider(host="127.0.0.1", port=19530)
        provider.remember("reflection", {"step_name": "t1", "decision": "abort"})
        results = provider.search("窗口丢失", limit=5)
    """

    def __init__(
            self,
            host: str = "127.0.0.1",
            port: int = 19530,
            collection_name: str = "jingmai_reflections",
            *,
            dim: int = 768,
    ) -> None:
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.dim = dim
        self._client: Any = None
        self._available = False
        self._error: str | None = None

        self._init_client()

    def _init_client(self) -> None:
        """初始化 Milvus 客户端，不可用时优雅降级。"""
        try:
            from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections, utility
            connections.connect(host=self.host, port=self.port, timeout=10)

            if not utility.has_collection(self.collection_name):
                schema = CollectionSchema([
                    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                    FieldSchema(name="memory_type", dtype=DataType.VARCHAR, max_length=64),
                    FieldSchema(name="payload_json", dtype=DataType.VARCHAR, max_length=4096),
                    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dim),
                ])
                Collection(name=self.collection_name, schema=schema)
                # 创建 IVF_FLAT 索引
                collection = Collection(name=self.collection_name)
                collection.create_index(
                    field_name="embedding",
                    index_params={
                        "metric_type": "IP",
                        "index_type": "IVF_FLAT",
                        "params": {"nlist": 128},
                    },
                )

            self._client = Collection(name=self.collection_name)
            self._available = True
        except ImportError:
            self._error = "pymilvus 未安装，Milvus 向量存储不可用"
        except Exception as exc:
            self._error = f"Milvus 连接失败: {exc}"

    # ── MemoryProvider 协议 ──

    def remember(self, memory_type: str, payload: dict[str, Any]) -> None:
        """存储反思记录到 Milvus。

        memory_type: "reflection" 或 "failure_signature"
        payload: 反思记录 dict 或 ReflectionRecord.to_dict()
        """
        if not self._available or self._client is None:
            return

        try:
            payload_json = json.dumps(payload, ensure_ascii=False, default=str)
            embedding = self._text_to_embedding(payload_json)
            self._client.insert([{
                "memory_type": memory_type,
                "payload_json": payload_json,
                "embedding": embedding,
            }])
        except Exception:
            pass  # 写入失败不阻塞主流程

    def search(
            self, query: str, limit: int = 5
    ) -> list[dict[str, Any]]:
        """语义搜索反思记录。

        query: 自然语言查询（如 "窗口丢失"、"重试耗尽"）
        limit: 返回数量上限
        """
        if not self._available or self._client is None:
            return []

        try:
            self._client.load()
            embedding = self._text_to_embedding(query)
            results = self._client.search(
                data=[embedding],
                anns_field="embedding",
                param={"metric_type": "IP", "params": {"nprobe": 16}},
                limit=limit,
            )
            matched: list[dict[str, Any]] = []
            for hits in results:
                for hit in hits:
                    try:
                        matched.append(json.loads(hit.entity.get("payload_json", "{}")))
                    except json.JSONDecodeError:
                        matched.append({"raw": hit.entity.get("payload_json", "")})
            return matched
        except Exception:
            return []  # 搜索失败不阻塞

    # ── 内部方法 ──

    def _text_to_embedding(self, text: str) -> list[float]:
        """将文本转为向量嵌入。

        使用简单 TF-IDF 风格词袋向量作为降级方案。
        生产环境应替换为 Sentence-BERT / text2vec 等模型。
        """
        # 简单词袋向量：基于字符 unigram 频率
        # 生产环境需接入 text2vec-large-chinese 等
        chars = list(set(text))
        vector = [0.0] * self.dim
        for i, ch in enumerate(chars):
            if i >= self.dim:
                break
            vector[i] = float(text.count(ch)) / max(len(text), 1)
        # 归一化
        norm = max(sum(v * v for v in vector) ** 0.5, 1e-8)
        return [v / norm for v in vector]

    @property
    def is_available(self) -> bool:
        return self._available

    @property
    def status_message(self) -> str:
        if self._available:
            return "Milvus 已连接"
        return self._error or "未初始化"
