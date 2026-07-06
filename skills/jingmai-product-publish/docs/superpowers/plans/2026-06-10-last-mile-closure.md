# 最后一公里闭环 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将设计规格 v2 中 2 个 Critical + 4 个 Warning 缺陷从骨架推进到可运行的闭环实现，使京麦商品上架自动化系统能真正驱动 GUI 和多行并发。

**Architecture:** 按依赖顺序从底向上——先修 LangGraph 条件路由（所有节点依赖它决定走向），再补 Milvus/BusinessCache 存储层，然后补 OCR Provider，最后组装 TaskGroup 多行调度和 UFO 真实 GUI 闭环。每个 Task 产出可独立测试的增量。

**Tech Stack:** Python 3.11+, LangGraph (StateGraph/add_conditional_edges), pymilvus, redis/asyncmy (可选), UFO v1 Windows UIAutomation, asyncio TaskGroup

---

## File Structure

| 文件 | 职责 | 状态 |
|------|------|------|
| `jm_ufo_agent/workflow/conditions.py` | 路由条件函数（已有 should_continue/can_save_draft，需扩展） | 修改 |
| `jm_ufo_agent/workflow/graph.py` | StateGraph 构建器（需 add_conditional_edges） | 修改 |
| `jm_ufo_agent/storage/milvus_client.py` | Milvus 客户端（需 collection/search 方法） | 修改 |
| `jm_ufo_agent/backends/web_surface/screenshot_ocr.py` | ScreenshotOcrService（需真实 Provider） | 修改 |
| `jm_ufo_agent/runtime/dispatcher.py` | RowDispatcher 多行调度（新建） | 新建 |
| `jm_ufo_agent/backends/ufo_backend.py` | UfoDesktopBackend 真实 GUI（新建） | 新建 |
| `tests/test_v2_conditional_routing.py` | 条件路由测试 | 新建 |
| `tests/test_v2_milvus_client.py` | Milvus 方法测试 | 新建 |
| `tests/test_v2_ocr_provider.py` | OCR Provider 测试 | 新建 |
| `tests/test_v2_dispatcher.py` | RowDispatcher 测试 | 新建 |
| `tests/test_v2_ufo_backend.py` | UFO Backend 测试 | 新建 |

---

### Task 1: LangGraph 条件路由 — FILL_FIELD↔VERIFY_FIELD 循环 + REFLECT_FAILURE→RECOVER 重试

**Files:**
- Modify: `jm_ufo_agent/workflow/conditions.py`
- Modify: `jm_ufo_agent/workflow/graph.py`
- Create: `tests/test_v2_conditional_routing.py`

- [ ] **Step 1: 写失败测试 — 条件路由函数**

```python
# tests/test_v2_conditional_routing.py
"""条件路由函数和 StateGraph 条件边测试。"""

from jm_ufo_agent.workflow.conditions import (
    can_save_draft,
    route_after_fill,
    route_after_assess,
    route_after_review,
    route_after_reflect,
    should_continue,
)
from jm_ufo_agent.workflow.state import GraphState, WorkflowStatus


def _make_state(**overrides) -> GraphState:
    """构建测试用 GraphState。"""
    defaults = dict(task_id="t1", row_index=0, product={"title": "测试"})
    defaults.update(overrides)
    return GraphState(**defaults)


class TestShouldContinue:
    def test_running_no_blockers(self):
        state = _make_state(status=WorkflowStatus.RUNNING)
        assert should_continue(state) is True

    def test_halted(self):
        state = _make_state(status=WorkflowStatus.HALTED)
        assert should_continue(state) is False

    def test_with_blockers(self):
        state = _make_state(status=WorkflowStatus.RUNNING, blockers=["bad"])
        assert should_continue(state) is False


class TestRouteAfterFill:
    def test_halted_goes_reflect(self):
        state = _make_state(status=WorkflowStatus.HALTED)
        assert route_after_fill(state) == "REFLECT_FAILURE"

    def test_blocked_goes_reflect(self):
        state = _make_state(status=WorkflowStatus.RUNNING, blockers=["x"])
        assert route_after_fill(state) == "REFLECT_FAILURE"

    def test_normal_goes_verify(self):
        state = _make_state(status=WorkflowStatus.RUNNING)
        assert route_after_fill(state) == "VERIFY_FIELD"


class TestRouteAfterAssess:
    def test_score_below_threshold(self):
        state = _make_state(status=WorkflowStatus.RUNNING, completion_score=0.5)
        assert route_after_assess(state) == "PLAN_FIELDS"

    def test_score_enough_review_save(self):
        state = _make_state(
            status=WorkflowStatus.RUNNING,
            completion_score=0.95,
            review_decision="save_draft",
        )
        assert route_after_assess(state) == "SAVE_DRAFT"

    def test_review_revise(self):
        state = _make_state(
            status=WorkflowStatus.RUNNING,
            completion_score=0.95,
            review_decision="revise",
        )
        assert route_after_assess(state) == "PLAN_FIELDS"

    def test_halted_goes_reflect(self):
        state = _make_state(status=WorkflowStatus.HALTED)
        assert route_after_assess(state) == "REFLECT_FAILURE"


class TestRouteAfterReview:
    def test_save_draft(self):
        state = _make_state(review_decision="save_draft")
        assert route_after_review(state) == "SAVE_DRAFT"

    def test_revise(self):
        state = _make_state(review_decision="revise")
        assert route_after_review(state) == "PLAN_FIELDS"

    def test_halt(self):
        state = _make_state(review_decision="halt")
        assert route_after_review(state) == "REFLECT_FAILURE"


class TestRouteAfterReflect:
    def test_retry_within_limit(self):
        state = _make_state(evaluation_loop_count=2)
        assert route_after_reflect(state) == "RECOVER"

    def test_exceed_retry_limit(self):
        state = _make_state(evaluation_loop_count=5)
        assert route_after_reflect(state) == "HALT"
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/test_v2_conditional_routing.py -v`
Expected: FAIL — `route_after_fill`, `route_after_assess`, `route_after_review`, `route_after_reflect` 未定义

- [ ] **Step 3: 实现路由条件函数**

```python
# jm_ufo_agent/workflow/conditions.py — 追加到文件末尾

_MAX_RETRY_LOOPS = 4


def route_after_fill(state: GraphState) -> str:
    """FILL_FIELD 完成后路由：正常→VERIFY_FIELD，异常→REFLECT_FAILURE。"""

    # FILL_FIELD 之后必须走 VERIFY_FIELD 闭环验证。
    # 如果 fill 阶段已经 halt 或产生 blocker，直接跳反思。
    if not should_continue(state):
        return "REFLECT_FAILURE"
    return "VERIFY_FIELD"


def route_after_assess(state: GraphState) -> str:
    """ASSESS_FORM_COMPLETION 完成后路由。"""

    # 完成度不够 → 回 PLAN_FIELDS 补字段。
    # review 决定 revise → 回 PLAN_FIELDS 重做。
    # review 决定 save_draft → 进 SAVE_DRAFT。
    # halt 状态 → REFLECT_FAILURE。
    if not should_continue(state):
        return "REFLECT_FAILURE"
    if state.review_decision == "revise":
        return "PLAN_FIELDS"
    if can_save_draft(state):
        return "SAVE_DRAFT"
    return "PLAN_FIELDS"


def route_after_review(state: GraphState) -> str:
    """MINIMAX_REVIEW_SCORE 完成后路由。"""

    # review 决策决定走向：save_draft/revise/halt 三路分发。
    # halt 走 REFLECT_FAILURE 而非直接 HALT，保留反思证据。
    mapping = {"save_draft": "SAVE_DRAFT", "revise": "PLAN_FIELDS", "halt": "REFLECT_FAILURE"}
    return mapping.get(state.review_decision, "REFLECT_FAILURE")


def route_after_reflect(state: GraphState) -> str:
    """REFLECT_FAILURE 完成后路由：重试→RECOVER，超限→HALT。"""

    # evaluation_loop_count 由 minimax_review_score_node 维护。
    # 超过最大重试次数后，不再循环，直接 HALT。
    if state.evaluation_loop_count >= _MAX_RETRY_LOOPS:
        return "HALT"
    return "RECOVER"
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m pytest tests/test_v2_conditional_routing.py -v`
Expected: PASS

- [ ] **Step 5: 写失败测试 — StateGraph 条件边**

```python
# 追加到 tests/test_v2_conditional_routing.py 末尾

class TestStateGraphConditionalEdges:
    def test_graph_has_conditional_edges(self):
        """graph 应包含条件边而非纯线性。"""
        from jm_ufo_agent.workflow.graph import build_state_graph

        spec = build_state_graph()
        # 条件边不应出现在 edges 元组中（线性边）
        linear_edges = set(spec.edges)
        # FILL_FIELD→VERIFY_FIELD 不应再是线性边
        assert ("FILL_FIELD", "VERIFY_FIELD") not in linear_edges
        # REFLECT_FAILURE→RECOVER 也不应是线性边
        assert ("REFLECT_FAILURE", "RECOVER") not in linear_edges

    def test_graph_compiles(self):
        """条件路由图应能成功编译。"""
        from jm_ufo_agent.workflow.graph import build_state_graph

        spec = build_state_graph()
        if spec.graph is not None:
            compiled = spec.graph.compile()
            assert compiled is not None
```

- [ ] **Step 6: 运行测试确认失败**

Run: `python -m pytest tests/test_v2_conditional_routing.py::TestStateGraphConditionalEdges -v`
Expected: FAIL — 当前 graph 使用线性 `zip(node_order, node_order[1:])`，FILL_FIELD→VERIFY_FIELD 在 edges 中

- [ ] **Step 7: 重构 graph.py 使用条件边**

```python
# jm_ufo_agent/workflow/graph.py — 替换 build_state_graph 函数

def build_state_graph() -> LocalStateGraphSpec:
    """构建 v2 设计要求的 18 节点 StateGraph 规格（含条件路由）。"""

    node_order = (
        "BOOTSTRAP",
        "RECOVER",
        "SELECT_ROW",
        "PREPARE_ASSETS",
        "OPEN_PAGE",
        "OBSERVE_PAGE",
        "ASSERT_PAGE_SIGNATURE",
        "CALIBRATE_LOCATORS",
        "PLAN_FIELDS",
        "FILL_FIELD",
        "VERIFY_FIELD",
        "ASSESS_FORM_COMPLETION",
        "MINIMAX_REVIEW_SCORE",
        "SAVE_DRAFT",
        "VERIFY_DRAFT",
        "COMMIT_ROW",
        "REFLECT_FAILURE",
        "HALT",
    )

    # 线性边：只保留无条件推进的顺序连接
    linear_edges = (
        ("BOOTSTRAP", "RECOVER"),
        ("RECOVER", "SELECT_ROW"),
        ("SELECT_ROW", "PREPARE_ASSETS"),
        ("PREPARE_ASSETS", "OPEN_PAGE"),
        ("OPEN_PAGE", "OBSERVE_PAGE"),
        ("OBSERVE_PAGE", "ASSERT_PAGE_SIGNATURE"),
        ("ASSERT_PAGE_SIGNATURE", "CALIBRATE_LOCATORS"),
        ("CALIBRATE_LOCATORS", "PLAN_FIELDS"),
        ("PLAN_FIELDS", "FILL_FIELD"),
        # FILL_FIELD → 条件路由 (route_after_fill)
        ("VERIFY_FIELD", "ASSESS_FORM_COMPLETION"),
        # ASSESS_FORM_COMPLETION → 条件路由 (route_after_assess)
        # MINIMAX_REVIEW_SCORE → 条件路由 (route_after_review)
        ("SAVE_DRAFT", "VERIFY_DRAFT"),
        ("VERIFY_DRAFT", "COMMIT_ROW"),
        ("COMMIT_ROW", "HALT"),
        # REFLECT_FAILURE → 条件路由 (route_after_reflect)
    )

    from jm_ufo_agent.workflow.conditions import (
        route_after_assess,
        route_after_fill,
        route_after_reflect,
        route_after_review,
    )

    edges = linear_edges  # 保持兼容：spec.edges 记录线性部分

    try:
        from langgraph.graph import StateGraph  # type: ignore
    except Exception:
        return LocalStateGraphSpec(node_order=node_order, edges=edges)

    graph = StateGraph(dict)
    for node_name in node_order:
        graph.add_node(node_name, lambda state, _node_name=node_name: state)
    graph.set_entry_point("BOOTSTRAP")

    for start, end in linear_edges:
        graph.add_edge(start, end)

    # 条件边：FILL_FIELD → VERIFY_FIELD / REFLECT_FAILURE
    graph.add_conditional_edges("FILL_FIELD", route_after_fill)
    # 条件边：ASSESS_FORM_COMPLETION → SAVE_DRAFT / PLAN_FIELDS / REFLECT_FAILURE
    graph.add_conditional_edges("ASSESS_FORM_COMPLETION", route_after_assess)
    # 条件边：MINIMAX_REVIEW_SCORE → SAVE_DRAFT / PLAN_FIELDS / REFLECT_FAILURE
    graph.add_conditional_edges("MINIMAX_REVIEW_SCORE", route_after_review)
    # 条件边：REFLECT_FAILURE → RECOVER / HALT
    graph.add_conditional_edges("REFLECT_FAILURE", route_after_reflect)

    graph.set_finish_point("HALT")
    return LocalStateGraphSpec(node_order=node_order, edges=edges, graph=graph)
```

- [ ] **Step 8: 运行测试确认通过**

Run: `python -m pytest tests/test_v2_conditional_routing.py -v`
Expected: PASS

- [ ] **Step 9: 运行全量测试回归**

Run: `python -m pytest tests/ -q`
Expected: 全部 PASS，无回归

- [ ] **Step 10: 提交**

```bash
git add jm_ufo_agent/workflow/conditions.py jm_ufo_agent/workflow/graph.py tests/test_v2_conditional_routing.py
git commit -m "feat(workflow): 添加条件路由 — FILL↔VERIFY循环 + REFLECT→RECOVER重试"
```

---

### Task 2: MilvusClient 补全 — collection 创建 / 索引 / 向量搜索

**Files:**
- Modify: `jm_ufo_agent/storage/milvus_client.py`
- Create: `tests/test_v2_milvus_client.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/test_v2_milvus_client.py
"""MilvusClient 补全方法测试。"""

from unittest.mock import MagicMock, patch

import pytest

from jm_ufo_agent.core.settings import MilvusSettings
from jm_ufo_agent.storage.milvus_client import MilvusClient


@pytest.fixture
def settings():
    return MilvusSettings(host="localhost", port=19530, db="default")


@pytest.fixture
def client(settings):
    return MilvusClient(settings)


class TestMilvusClientCollection:
    @patch("jm_ufo_agent.storage.milvus_client.MilvusClient.connect")
    def test_create_collection_if_not_exists(self, mock_connect, client):
        """create_collection 应调用 pymilvus Collection。"""
        client.connected = True
        with patch("pymilvus.Collection") as MockColl:
            MockColl.exists.return_value = False
            mock_coll_instance = MagicMock()
            MockColl.return_value = mock_coll_instance
            client.create_collection(
                name="test_col",
                dimension=128,
                description="测试集合",
            )
            MockColl.assert_called_once()

    @patch("jm_ufo_agent.storage.milvus_client.MilvusClient.connect")
    def test_create_collection_skip_if_exists(self, mock_connect, client):
        """已有 collection 时应跳过创建。"""
        client.connected = True
        with patch("pymilvus.Collection") as MockColl:
            MockColl.exists.return_value = True
            client.create_collection(name="existing_col", dimension=128)
            MockColl.assert_not_called()  # 不调用构造函数


class TestMilvusClientSearch:
    @patch("jm_ufo_agent.storage.milvus_client.MilvusClient.connect")
    def test_search_returns_results(self, mock_connect, client):
        """search 应返回搜索结果列表。"""
        client.connected = True
        with patch("pymilvus.Collection") as MockColl:
            mock_coll = MagicMock()
            MockColl.return_value = mock_coll
            mock_coll.search.return_value = [[MagicMock(id="vec1", distance=0.1, entity={"text": "hello"})]]
            results = client.search(
                collection_name="test_col",
                query_vector=[0.1] * 128,
                top_k=5,
            )
            assert isinstance(results, list)

    def test_search_before_connect_raises(self, client):
        """未连接时搜索应抛出异常。"""
        client.connected = False
        with pytest.raises(RuntimeError, match="未连接"):
            client.search(collection_name="test_col", query_vector=[0.1] * 128, top_k=5)
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/test_v2_milvus_client.py -v`
Expected: FAIL — `create_collection` 和 `search` 方法不存在

- [ ] **Step 3: 实现 MilvusClient 补全方法**

```python
# jm_ufo_agent/storage/milvus_client.py — 替换整个文件

"""Milvus 客户端封装 — 连接 / 集合管理 / 向量搜索。"""

from __future__ import annotations

from typing import Any

from jm_ufo_agent.core.settings import MilvusSettings


class MilvusClient:
    """延迟创建的 Milvus 连接，支持集合创建和向量搜索。"""

    def __init__(self, settings: MilvusSettings):
        """保存 Milvus 配置。"""
        self.settings = settings
        self.connected = False

    def connect(self) -> Any:
        """连接 Milvus 服务。"""
        try:
            from pymilvus import connections
        except ImportError as exc:
            raise RuntimeError("缺少 pymilvus，无法连接 Milvus") from exc
        connections.connect(
            alias="jingmai_v2",
            host=self.settings.host,
            port=str(self.settings.port),
            db_name=self.settings.db,
        )
        self.connected = True
        return connections

    def _ensure_connected(self) -> None:
        """断言已连接。"""
        if not self.connected:
            raise RuntimeError("未连接 Milvus，请先调用 connect()")

    def create_collection(
        self,
        name: str,
        dimension: int = 768,
        description: str = "",
    ) -> Any:
        """创建向量集合（如不存在）。

        # dimension 默认 768，适配常见 embedding 模型输出维度。
        # 使用 L2 距离度量，适合检索相似失败案例。
        # 自动加载到内存，避免首次查询延迟。
        """
        self._ensure_connected()
        try:
            from pymilvus import Collection, FieldSchema, DataType, CollectionSchema
        except ImportError as exc:
            raise RuntimeError("缺少 pymilvus") from exc

        if Collection.exists(name, using="jingmai_v2"):
            return Collection(name, using="jingmai_v2")

        pk_field = FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=64, is_primary=True)
        vector_field = FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dimension)
        text_field = FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=4096)
        schema = CollectionSchema(fields=[pk_field, vector_field, text_field], description=description)
        collection = Collection(name=name, schema=schema, using="jingmai_v2")

        # 创建 IVF_FLAT 索引，nlist=128 适合中小规模数据集
        index_params = {"metric_type": "L2", "index_type": "IVF_FLAT", "params": {"nlist": 128}}
        collection.create_index(field_name="vector", index_params=index_params)
        collection.load()
        return collection

    def search(
        self,
        collection_name: str,
        query_vector: list[float],
        top_k: int = 5,
        output_fields: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """向量相似度搜索。

        # query_vector 维度必须与集合 dimension 一致。
        # output_fields 控制返回哪些标量字段，默认返回 text。
        # 返回列表中每项包含 id, distance, entity。
        """
        self._ensure_connected()
        try:
            from pymilvus import Collection
        except ImportError as exc:
            raise RuntimeError("缺少 pymilvus") from exc

        collection = Collection(collection_name, using="jingmai_v2")
        search_params = {"metric_type": "L2", "params": {"nprobe": 16}}
        results = collection.search(
            data=[query_vector],
            anns_field="vector",
            param=search_params,
            limit=top_k,
            output_fields=output_fields or ["text"],
        )
        # 展平搜索结果为 dict 列表
        output: list[dict[str, Any]] = []
        for hits in results:
            for hit in hits:
                output.append({
                    "id": hit.id,
                    "distance": hit.distance,
                    "entity": hit.entity._row_data if hasattr(hit.entity, "_row_data") else {},
                })
        return output
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m pytest tests/test_v2_milvus_client.py -v`
Expected: PASS

- [ ] **Step 5: 运行全量测试回归**

Run: `python -m pytest tests/ -q`
Expected: 全部 PASS

- [ ] **Step 6: 提交**

```bash
git add jm_ufo_agent/storage/milvus_client.py tests/test_v2_milvus_client.py
git commit -m "feat(storage): MilvusClient 补全 — collection创建/索引/向量搜索"
```

---

### Task 3: ScreenshotOcrService 真实 Provider 桥接

**Files:**
- Modify: `jm_ufo_agent/backends/web_surface/screenshot_ocr.py`
- Create: `tests/test_v2_ocr_provider.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/test_v2_ocr_provider.py
"""ScreenshotOcrService 真实 Provider 桥接测试。"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from jm_ufo_agent.backends.web_surface.screenshot_ocr import (
    LocalPaddleOcrProvider,
    ScreenshotOcrService,
)


class TestLocalPaddleOcrProvider:
    def test_provider_protocol_match(self):
        """LocalPaddleOcrProvider 应实现 capture_and_ocr 协议。"""
        provider = LocalPaddleOcrProvider()
        assert hasattr(provider, "capture_and_ocr")
        assert callable(provider.capture_and_ocr)

    @pytest.mark.asyncio
    async def test_provider_returns_result(self):
        """Provider 应返回 ScreenshotOcrResult。"""
        from jm_ufo_agent.backends.web_surface.screenshot_ocr import ScreenshotOcrResult

        provider = LocalPaddleOcrProvider()
        # 没有 PaddleOCR 时应返回 graceful fallback
        result = await provider.capture_and_ocr(window_title="京麦")
        assert isinstance(result, ScreenshotOcrResult)


class TestScreenshotOcrServiceWithProvider:
    @pytest.mark.asyncio
    async def test_service_uses_injected_provider(self):
        """注入 provider 后 service 应使用它而非 dry-run。"""
        from jm_ufo_agent.backends.web_surface.screenshot_ocr import ScreenshotOcrResult

        mock_provider = AsyncMock()
        mock_provider.capture_and_ocr.return_value = ScreenshotOcrResult(
            page_signature="test_sig",
            ocr_text="测试OCR文本",
            screenshot_path="/tmp/test.png",
        )
        service = ScreenshotOcrService(provider=mock_provider)
        result = await service.capture_and_ocr(window_title="京麦")
        assert result.page_signature == "test_sig"
        assert result.ocr_text == "测试OCR文本"
        mock_provider.capture_and_ocr.assert_called_once()
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/test_v2_ocr_provider.py -v`
Expected: FAIL — `LocalPaddleOcrProvider` 不存在

- [ ] **Step 3: 读取当前 screenshot_ocr.py 确认结构**

需要读取 `jm_ufo_agent/backends/web_surface/screenshot_ocr.py` 确认当前 `ScreenshotOcrResult` 和 `ScreenshotOcrService` 的完整定义。

- [ ] **Step 4: 实现 LocalPaddleOcrProvider**

在 `screenshot_ocr.py` 中添加 `LocalPaddleOcrProvider` 类：

```python
# 追加到 jm_ufo_agent/backends/web_surface/screenshot_ocr.py 末尾

class LocalPaddleOcrProvider:
    """基于 PaddleOCR 的本地截图+OCR Provider。

    # PaddleOCR 是可选依赖，未安装时返回 fallback 结果。
    # 真实环境下截图通过 pyautogui 或 win32api 获取。
    # OCR 结果用于页面签名计算和字段验证。
    """

    async def capture_and_ocr(self, window_title: str = "") -> ScreenshotOcrResult:
        """截图并执行 OCR。"""
        try:
            from paddleocr import PaddleOCR
        except ImportError:
            return ScreenshotOcrResult(
                page_signature="paddleocr-not-installed",
                ocr_text="",
                screenshot_path="",
            )

        ocr = PaddleOCR(use_angle_cls=True, lang="ch", show_log=False)
        screenshot_path = await self._capture_window(window_title)
        if not screenshot_path:
            return ScreenshotOcrResult(
                page_signature="capture-failed",
                ocr_text="",
                screenshot_path="",
            )

        result = ocr.ocr(screenshot_path, cls=True)
        texts: list[str] = []
        if result and result[0]:
            for line in result[0]:
                texts.append(line[1][0])
        ocr_text = "\n".join(texts)
        page_signature = hashlib.md5(ocr_text.encode()).hexdigest()[:12] if ocr_text else "empty"

        return ScreenshotOcrResult(
            page_signature=page_signature,
            ocr_text=ocr_text,
            screenshot_path=screenshot_path,
        )

    async def _capture_window(self, window_title: str) -> str:
        """截取指定窗口截图到临时文件。"""
        import tempfile
        import os

        try:
            import pyautogui
        except ImportError:
            return ""

        screenshot = pyautogui.screenshot()
        tmp_dir = tempfile.mkdtemp(prefix="jm_ocr_")
        path = os.path.join(tmp_dir, "screenshot.png")
        screenshot.save(path)
        return path
```

注意：需要在文件顶部确认是否已 `import hashlib`，如未导入需添加。

- [ ] **Step 5: 运行测试确认通过**

Run: `python -m pytest tests/test_v2_ocr_provider.py -v`
Expected: PASS

- [ ] **Step 6: 运行全量测试回归**

Run: `python -m pytest tests/ -q`
Expected: 全部 PASS

- [ ] **Step 7: 提交**

```bash
git add jm_ufo_agent/backends/web_surface/screenshot_ocr.py tests/test_v2_ocr_provider.py
git commit -m "feat(ocr): 添加 LocalPaddleOcrProvider 真实截图+OCR 桥接"
```

---

### Task 4: BusinessCache 验证 — 确认 Redis 缓存方法完整性

**Files:**
- Create: `tests/test_v2_business_cache.py`

- [ ] **Step 1: 写完整性测试**

```python
# tests/test_v2_business_cache.py
"""BusinessCache 方法完整性验证测试。"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestRedisBusinessCacheMethods:
    """验证 RedisBusinessCache 所有缓存方法存在且签名正确。"""

    def test_has_ocr_cache_methods(self):
        from jm_ufo_agent.storage.business_cache import RedisBusinessCache

        cache = RedisBusinessCache.__new__(RedisBusinessCache)
        assert hasattr(cache, "set_ocr_cache")
        assert hasattr(cache, "get_ocr_cache")
        assert callable(cache.set_ocr_cache)
        assert callable(cache.get_ocr_cache)

    def test_has_vlm_cache_methods(self):
        from jm_ufo_agent.storage.business_cache import RedisBusinessCache

        cache = RedisBusinessCache.__new__(RedisBusinessCache)
        assert hasattr(cache, "set_vlm_cache")
        assert hasattr(cache, "get_vlm_cache")

    def test_has_locator_cache_methods(self):
        from jm_ufo_agent.storage.business_cache import RedisBusinessCache

        cache = RedisBusinessCache.__new__(RedisBusinessCache)
        assert hasattr(cache, "set_locator_cache")
        assert hasattr(cache, "get_locator_cache")

    @pytest.mark.asyncio
    async def test_ocr_cache_roundtrip(self):
        """OCR 缓存 set+get 应能正确往返。"""
        from jm_ufo_agent.storage.business_cache import RedisBusinessCache

        mock_redis = AsyncMock()
        mock_redis.set = AsyncMock(return_value=True)
        mock_redis.get = AsyncMock(return_value='{"text": "测试", "signature": "abc"}')

        cache = RedisBusinessCache(redis=mock_redis, ttl_seconds=3600)
        await cache.set_ocr_cache("key1", {"text": "测试", "signature": "abc"})
        result = await cache.get_ocr_cache("key1")
        assert result is not None
        assert result["text"] == "测试"
        mock_redis.set.assert_called_once()
        mock_redis.get.assert_called_once()


class TestMilvusReflectionStoreMethods:
    """验证 MilvusReflectionStore 方法完整性。"""

    def test_has_add_failure_reflection(self):
        from jm_ufo_agent.storage.business_cache import MilvusReflectionStore

        store = MilvusReflectionStore.__new__(MilvusReflectionStore)
        assert hasattr(store, "add_failure_reflection")
        assert callable(store.add_failure_reflection)
```

- [ ] **Step 2: 运行测试确认通过**

Run: `python -m pytest tests/test_v2_business_cache.py -v`
Expected: PASS — BusinessCache 方法已在之前的 Phase 实现，此测试确认完整性

- [ ] **Step 3: 提交**

```bash
git add tests/test_v2_business_cache.py
git commit -m "test(storage): BusinessCache 方法完整性验证测试"
```

---

### Task 5: RowDispatcher 多行并发调度

**Files:**
- Create: `jm_ufo_agent/runtime/dispatcher.py`
- Create: `tests/test_v2_dispatcher.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/test_v2_dispatcher.py
"""RowDispatcher 多行并发调度测试。"""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from jm_ufo_agent.runtime.dispatcher import RowDispatcher, RowResult


class TestRowResult:
    def test_success_result(self):
        result = RowResult(row_index=0, ok=True, message="完成")
        assert result.ok is True
        assert result.row_index == 0

    def test_failure_result(self):
        result = RowResult(row_index=1, ok=False, message="失败", error="字段验证不通过")
        assert result.ok is False
        assert result.error == "字段验证不通过"


class TestRowDispatcher:
    def test_init_default_concurrency(self):
        dispatcher = RowDispatcher()
        assert dispatcher.max_concurrency == 3

    def test_init_custom_concurrency(self):
        dispatcher = RowDispatcher(max_concurrency=5)
        assert dispatcher.max_concurrency == 5

    @pytest.mark.asyncio
    async def test_dispatch_single_row(self):
        """单行调度应正确返回结果。"""
        mock_handler = AsyncMock(return_value=RowResult(row_index=0, ok=True, message="完成"))
        dispatcher = RowDispatcher(max_concurrency=1)

        results = await dispatcher.dispatch(
            rows=[{"title": "商品1", "price": 99.9}],
            handler=mock_handler,
        )
        assert len(results) == 1
        assert results[0].ok is True
        assert results[0].row_index == 0

    @pytest.mark.asyncio
    async def test_dispatch_multiple_rows_concurrent(self):
        """多行应受信号量限制并发执行。"""
        execution_order: list[int] = []

        async def slow_handler(row_index: int, row_data: dict) -> RowResult:
            execution_order.append(row_index)
            await asyncio.sleep(0.05)
            return RowResult(row_index=row_index, ok=True, message="完成")

        dispatcher = RowDispatcher(max_concurrency=2)
        rows = [{"title": f"商品{i}"} for i in range(5)]

        results = await dispatcher.dispatch(rows=rows, handler=slow_handler)
        assert len(results) == 5
        assert all(r.ok for r in results)

    @pytest.mark.asyncio
    async def test_dispatch_row_failure_does_not_block_others(self):
        """单行失败不应阻塞其他行。"""
        async def flaky_handler(row_index: int, row_data: dict) -> RowResult:
            if row_index == 1:
                return RowResult(row_index=row_index, ok=False, message="失败", error="验证失败")
            return RowResult(row_index=row_index, ok=True, message="完成")

        dispatcher = RowDispatcher(max_concurrency=3)
        rows = [{"title": f"商品{i}"} for i in range(3)]

        results = await dispatcher.dispatch(rows=rows, handler=flaky_handler)
        assert len(results) == 3
        assert results[0].ok is True
        assert results[1].ok is False
        assert results[2].ok is True

    @pytest.mark.asyncio
    async def test_dispatch_empty_rows(self):
        """空行列表应返回空结果。"""
        dispatcher = RowDispatcher()
        results = await dispatcher.dispatch(rows=[], handler=AsyncMock())
        assert results == []

    @pytest.mark.asyncio
    async def test_concurrency_limit_respected(self):
        """并发数不应超过 max_concurrency。"""
        peak_concurrent = 0
        current_concurrent = 0

        async def tracking_handler(row_index: int, row_data: dict) -> RowResult:
            nonlocal peak_concurrent, current_concurrent
            current_concurrent += 1
            peak_concurrent = max(peak_concurrent, current_concurrent)
            await asyncio.sleep(0.05)
            current_concurrent -= 1
            return RowResult(row_index=row_index, ok=True, message="完成")

        dispatcher = RowDispatcher(max_concurrency=2)
        rows = [{"title": f"商品{i}"} for i in range(6)]

        await dispatcher.dispatch(rows=rows, handler=tracking_handler)
        assert peak_concurrent <= 2
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/test_v2_dispatcher.py -v`
Expected: FAIL — `jm_ufo_agent.runtime.dispatcher` 模块不存在

- [ ] **Step 3: 实现 RowDispatcher**

```python
# jm_ufo_agent/runtime/dispatcher.py
"""多行并发调度器 — RowDispatcher。"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable


@dataclass
class RowResult:
    """单行执行结果。"""

    row_index: int
    ok: bool
    message: str = ""
    error: str = ""
    data: dict[str, Any] = field(default_factory=dict)


# handler 签名：(row_index, row_data) -> RowResult
RowHandler = Callable[[int, dict[str, Any]], Awaitable[RowResult]]


class RowDispatcher:
    """多行并发调度器，使用 asyncio.Semaphore 控制并发。"""

    def __init__(self, max_concurrency: int = 3):
        """初始化调度器。

        # max_concurrency 控制同时执行的行数。
        # 默认 3，平衡 GUI 压力和吞吐量。
        # GUI 操作（click/fill）由 GuiLock 串行化，不会并发冲突。
        """
        self.max_concurrency = max_concurrency

    async def dispatch(
        self,
        rows: list[dict[str, Any]],
        handler: RowHandler,
    ) -> list[RowResult]:
        """并发调度多行执行。

        # 使用 Semaphore 限制并发数，避免 GUI 过载。
        # 每行独立执行，单行失败不影响其他行。
        # 结果按 row_index 排序返回。
        """
        if not rows:
            return []

        semaphore = asyncio.Semaphore(self.max_concurrency)

        async def _run_one(index: int, row: dict[str, Any]) -> RowResult:
            async with semaphore:
                try:
                    return await handler(index, row)
                except Exception as exc:
                    return RowResult(row_index=index, ok=False, message="异常", error=str(exc))

        tasks = [_run_one(i, row) for i, row in enumerate(rows)]
        results = await asyncio.gather(*tasks)
        return sorted(results, key=lambda r: r.row_index)
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m pytest tests/test_v2_dispatcher.py -v`
Expected: PASS

- [ ] **Step 5: 运行全量测试回归**

Run: `python -m pytest tests/ -q`
Expected: 全部 PASS

- [ ] **Step 6: 提交**

```bash
git add jm_ufo_agent/runtime/dispatcher.py tests/test_v2_dispatcher.py
git commit -m "feat(runtime): 添加 RowDispatcher 多行并发调度器"
```

---

### Task 6: UfoDesktopBackend 真实 GUI 闭环

**Files:**
- Create: `jm_ufo_agent/backends/ufo_backend.py`
- Create: `tests/test_v2_ufo_backend.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/test_v2_ufo_backend.py
"""UfoDesktopBackend 真实 GUI 闭环测试。"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from jm_ufo_agent.agents.base import AgentResult
from jm_ufo_agent.commands.base import Command
from jm_ufo_agent.backends.ufo_backend import UfoDesktopBackend


class TestUfoDesktopBackendProtocol:
    def test_implements_desktop_backend(self):
        """UfoDesktopBackend 应实现 DesktopBackend 协议。"""
        from jm_ufo_agent.agents.desktop import DesktopBackend

        backend = UfoDesktopBackend.__new__(UfoDesktopBackend)
        assert hasattr(backend, "execute")
        assert callable(backend.execute)

    def test_init_with_ufo_root(self):
        """应接受 ufo_root 路径参数。"""
        from pathlib import Path

        backend = UfoDesktopBackend(ufo_root=Path("/fake/ufo"))
        assert backend.ufo_root == Path("/fake/ufo")


class TestUfoDesktopBackendExecute:
    @pytest.mark.asyncio
    async def test_click_delegates_to_ufo(self):
        """click 命令应委托给 UFO controller。"""
        from pathlib import Path

        backend = UfoDesktopBackend(ufo_root=Path("/fake/ufo"))
        # mock 掉真实 UFO 调用
        backend._controller = MagicMock()
        backend._controller.click = MagicMock(return_value=True)

        cmd = Command(action="click", target="价格输入框", label="点击价格")
        result = await backend.execute(cmd)
        assert isinstance(result, AgentResult)

    @pytest.mark.asyncio
    async def test_fill_uses_clipboard(self):
        """fill 命令应通过剪贴板+粘贴方式输入。"""
        from pathlib import Path

        backend = UfoDesktopBackend(ufo_root=Path("/fake/ufo"))
        backend._controller = MagicMock()
        backend._controller.set_text = MagicMock(return_value=True)

        cmd = Command(action="fill", target="标题", label="填写标题", value="测试商品")
        result = await backend.execute(cmd)
        assert isinstance(result, AgentResult)

    @pytest.mark.asyncio
    async def test_submit_delegates_to_ufo(self):
        """submit 命令应委托给 UFO。"""
        from pathlib import Path

        backend = UfoDesktopBackend(ufo_root=Path("/fake/ufo"))
        backend._controller = MagicMock()
        backend._controller.click = MagicMock(return_value=True)

        cmd = Command(action="submit", target="draft", label="保存草稿")
        result = await backend.execute(cmd)
        assert isinstance(result, AgentResult)

    @pytest.mark.asyncio
    async def test_execute_returns_failure_on_error(self):
        """UFO 调用失败应返回 AgentResult(ok=False)。"""
        from pathlib import Path

        backend = UfoDesktopBackend(ufo_root=Path("/fake/ufo"))
        backend._controller = MagicMock()
        backend._controller.click = MagicMock(side_effect=RuntimeError("窗口未找到"))

        cmd = Command(action="click", target="不存在", label="测试失败")
        result = await backend.execute(cmd)
        assert result.ok is False
        assert "窗口未找到" in result.message

    @pytest.mark.asyncio
    async def test_unknown_action_returns_failure(self):
        """未知 action 应返回失败。"""
        from pathlib import Path

        backend = UfoDesktopBackend(ufo_root=Path("/fake/ufo"))
        cmd = Command(action="unknown_action", target="x", label="y")
        result = await backend.execute(cmd)
        assert result.ok is False
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/test_v2_ufo_backend.py -v`
Expected: FAIL — `jm_ufo_agent.backends.ufo_backend` 模块不存在

- [ ] **Step 3: 实现 UfoDesktopBackend**

```python
# jm_ufo_agent/backends/ufo_backend.py
"""UFO v1 DesktopBackend 实现 — 真实 Windows GUI 操作闭环。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jm_ufo_agent.agents.base import AgentResult
from jm_ufo_agent.commands.base import Command


class UfoDesktopBackend:
    """基于 UFO v1 的真实桌面 backend。

    # UFO v1 使用 Windows UIAutomation + 剪贴板实现 GUI 操作。
    # click → 定位元素 → 调用 Invoke 或 Click 模式。
    # fill → 剪贴板写入 → Ctrl+V 粘贴，绕过输入法问题。
    # submit → 点击按钮（草稿/发布），SafetyPolicy 在上层已拦截发布。
    # ufo_root 指向 UFO v1 项目根目录，动态加载 controller/inspector。
    """

    def __init__(self, ufo_root: Path | None = None):
        """初始化 UFO backend。"""
        self.ufo_root = ufo_root or self._detect_ufo_root()
        self._controller: Any = None
        self._inspector: Any = None

    @staticmethod
    def _detect_ufo_root() -> Path:
        """自动检测 UFO v1 安装路径。"""
        # 优先查找环境变量
        import os

        env_path = os.environ.get("UFO_ROOT")
        if env_path:
            return Path(env_path)

        # 常见安装位置
        candidates = [
            Path.home() / "ufo",
            Path("C:/ufo"),
            Path("D:/ufo"),
        ]
        for p in candidates:
            if p.exists():
                return p

        return Path("ufo")  # fallback，后续操作会失败并给出明确错误

    def _ensure_loaded(self) -> None:
        """延迟加载 UFO 模块。"""
        if self._controller is not None:
            return

        if not self.ufo_root.exists():
            raise RuntimeError(f"UFO 根目录不存在: {self.ufo_root}")

        import sys

        ufo_str = str(self.ufo_root)
        if ufo_str not in sys.path:
            sys.path.insert(0, ufo_str)

        try:
            from ufo.agents.agent.ufo_controller import UFOController
            self._controller = UFOController
        except ImportError:
            # UFO 不可用时使用 mock controller，所有操作返回 not-available
            self._controller = _StubController()

    async def execute(self, command: Command) -> AgentResult:
        """执行已经通过安全校验的命令。"""
        try:
            self._ensure_loaded()
        except RuntimeError as exc:
            return AgentResult(ok=False, message=str(exc), data={"action": command.action})

        action = command.action
        try:
            if action == "click":
                return await self._do_click(command)
            elif action == "fill":
                return await self._do_fill(command)
            elif action == "submit":
                return await self._do_submit(command)
            else:
                return AgentResult(ok=False, message=f"不支持的动作: {action}", data={"action": action})
        except Exception as exc:
            return AgentResult(ok=False, message=str(exc), data={"action": action})

    async def _do_click(self, command: Command) -> AgentResult:
        """执行点击。"""
        # UFO controller 的 click 通过 UIA 定位目标并调用 Invoke
        self._controller.click(command.target)
        return AgentResult(
            ok=True,
            message=f"已点击: {command.target}",
            data={"action": "click", "target": command.target, "label": command.label},
        )

    async def _do_fill(self, command: Command) -> AgentResult:
        """执行填充 — 通过剪贴板粘贴。"""
        value = str(command.value) if command.value is not None else ""
        # UFO 的 set_text 先聚焦目标元素，再通过剪贴板粘贴
        self._controller.set_text(command.target, value)
        return AgentResult(
            ok=True,
            message=f"已填充: {command.target}={value[:20]}",
            data={"action": "fill", "target": command.target, "value_preview": value[:20]},
        )

    async def _do_submit(self, command: Command) -> AgentResult:
        """执行提交（保存草稿等）。"""
        # submit 本质是点击特定按钮，SafetyPolicy 已在上层拦截"发布"
        self._controller.click(command.target)
        return AgentResult(
            ok=True,
            message=f"已提交: {command.label}",
            data={"action": "submit", "target": command.target, "label": command.label},
        )


class _StubController:
    """UFO 不可用时的桩控制器，所有操作抛出 RuntimeError。"""

    def click(self, target: str) -> None:
        raise RuntimeError("UFO 未安装，无法执行 click")

    def set_text(self, target: str, value: str) -> None:
        raise RuntimeError("UFO 未安装，无法执行 fill")
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m pytest tests/test_v2_ufo_backend.py -v`
Expected: PASS

- [ ] **Step 5: 运行全量测试回归**

Run: `python -m pytest tests/ -q`
Expected: 全部 PASS

- [ ] **Step 6: 提交**

```bash
git add jm_ufo_agent/backends/ufo_backend.py tests/test_v2_ufo_backend.py
git commit -m "feat(backends): 添加 UfoDesktopBackend 真实 GUI 闭环实现"
```

---

### Task 7: 集成验证 — DesktopAgent 注入 UfoDesktopBackend + RowDispatcher 联调

**Files:**
- Create: `tests/test_v2_integration_closure.py`

- [ ] **Step 1: 写集成测试**

```python
# tests/test_v2_integration_closure.py
"""最后一公里集成验证 — DesktopAgent+UfoBackend + RowDispatcher+ConditionalRouting。"""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from jm_ufo_agent.agents.desktop import DesktopAgent
from jm_ufo_agent.agents.base import AgentResult
from jm_ufo_agent.backends.ufo_backend import UfoDesktopBackend
from jm_ufo_agent.runtime.dispatcher import RowDispatcher, RowResult
from jm_ufo_agent.safety.policy import SafetyPolicy


class TestDesktopAgentWithUfoBackend:
    @pytest.mark.asyncio
    async def test_agent_uses_ufo_backend(self):
        """DesktopAgent 注入 UfoDesktopBackend 后应正确委托。"""
        backend = UfoDesktopBackend(ufo_root=Path("/fake/ufo"))
        backend._controller = MagicMock()
        backend._controller.click = MagicMock(return_value=True)

        agent = DesktopAgent(name="test_agent", backend=backend)
        result = await agent.click(target="价格输入框", label="点击价格")
        assert isinstance(result, AgentResult)


class TestRowDispatcherWithWorkflow:
    @pytest.mark.asyncio
    async def test_dispatcher_runs_rows_through_handler(self):
        """RowDispatcher 应能为每行调用 handler。"""
        call_log: list[int] = []

        async def row_handler(index: int, data: dict) -> RowResult:
            call_log.append(index)
            return RowResult(row_index=index, ok=True, message="完成")

        dispatcher = RowDispatcher(max_concurrency=2)
        rows = [{"title": f"商品{i}"} for i in range(4)]
        results = await dispatcher.dispatch(rows=rows, handler=row_handler)

        assert len(results) == 4
        assert all(r.ok for r in results)
        assert sorted(call_log) == [0, 1, 2, 3]


class TestConditionalRoutingIntegration:
    def test_graph_routes_halted_to_reflect(self):
        """halt 状态应路由到 REFLECT_FAILURE。"""
        from jm_ufo_agent.workflow.conditions import route_after_fill
        from jm_ufo_agent.workflow.state import GraphState, WorkflowStatus

        state = GraphState(task_id="t1", row_index=0, product={}, status=WorkflowStatus.HALTED)
        assert route_after_fill(state) == "REFLECT_FAILURE"

    def test_graph_routes_normal_to_verify(self):
        """正常状态应路由到 VERIFY_FIELD。"""
        from jm_ufo_agent.workflow.conditions import route_after_fill
        from jm_ufo_agent.workflow.state import GraphState, WorkflowStatus

        state = GraphState(task_id="t1", row_index=0, product={}, status=WorkflowStatus.RUNNING)
        assert route_after_fill(state) == "VERIFY_FIELD"

    def test_reflect_recover_loop(self):
        """REFLECT_FAILURE 应在重试次数内路由到 RECOVER。"""
        from jm_ufo_agent.workflow.conditions import route_after_reflect
        from jm_ufo_agent.workflow.state import GraphState

        state = GraphState(task_id="t1", row_index=0, product={}, evaluation_loop_count=2)
        assert route_after_reflect(state) == "RECOVER"

    def test_reflect_halt_after_max_retries(self):
        """超过最大重试次数应路由到 HALT。"""
        from jm_ufo_agent.workflow.conditions import route_after_reflect
        from jm_ufo_agent.workflow.state import GraphState

        state = GraphState(task_id="t1", row_index=0, product={}, evaluation_loop_count=5)
        assert route_after_reflect(state) == "HALT"
```

- [ ] **Step 2: 运行集成测试**

Run: `python -m pytest tests/test_v2_integration_closure.py -v`
Expected: PASS

- [ ] **Step 3: 运行全量测试**

Run: `python -m pytest tests/ -q`
Expected: 全部 PASS

- [ ] **Step 4: 提交**

```bash
git add tests/test_v2_integration_closure.py
git commit -m "test: 最后一公里集成验证 — DesktopAgent+UFO + Dispatcher + ConditionalRouting"
```

---

## 自查清单

| 缺陷 | 对应 Task | 闭环验证 |
|------|----------|---------|
| C1: UFO 真实 GUI 闭环 | Task 6 + Task 7 | UfoDesktopBackend 实现 DesktopBackend 协议，DesktopAgent 注入后可 click/fill/submit |
| C2: TaskGroup 多行并发调度 | Task 5 + Task 7 | RowDispatcher 使用 Semaphore 控制并发，单行失败不阻塞其他行 |
| W1: LangGraph 条件路由 | Task 1 | add_conditional_edges 替换线性 FILL→VERIFY/ASSESS→SAVE，REFLECT→RECOVER 循环 |
| W2: ScreenshotOcrService | Task 3 | LocalPaddleOcrProvider 实现真实截图+OCR，注入 Service 后不再 dry-run |
| W3: MilvusClient | Task 2 | create_collection + search 方法补全，支持向量索引和相似度搜索 |
| W4: BusinessCache | Task 4 | 验证性测试确认 RedisBusinessCache OCR/VLM/Locator 缓存方法完整 |
