import asyncio

from jm_ufo_agent.runtime.workers.data_fetch import DataFetchJob, DataFetchWorker
from jm_ufo_agent.runtime.workers.gui_loop import GuiJob, GuiWorker
from jm_ufo_agent.runtime.workers.image_process import ImageProcessJob, ImageProcessWorker
from jm_ufo_agent.storage.checkpointer import AsyncMySQLSaver
from jm_ufo_agent.storage.redis_lock import RedisRowLock
from jm_ufo_agent.workflow.state import GraphState, WorkflowStatus


class FakeTaskRepository:
    def __init__(self):
        self.records = {}

    async def upsert(self, record):
        self.records[record.task_id] = record

    async def get(self, task_id):
        return self.records.get(task_id)


class FakeRedis:
    def __init__(self):
        self.values = {}

    async def set(self, key, value, nx=False, ex=None):
        if nx and key in self.values:
            return False
        self.values[key] = value
        return True

    async def get(self, key):
        return self.values.get(key)

    async def delete(self, key):
        return 1 if self.values.pop(key, None) is not None else 0


async def test_async_mysql_saver_roundtrips_graph_state():
    repo = FakeTaskRepository()
    saver = AsyncMySQLSaver(repo)
    state = GraphState(task_id="task-1", row_index=82, product={"title": "测试"})
    state.status = WorkflowStatus.RUNNING
    state.verify_field("title")

    await saver.aput(state)
    snapshot = await saver.aget("task-1")

    assert snapshot is not None
    assert snapshot["row_index"] == 82
    assert snapshot["verified_fields"] == ["title"]


async def test_redis_row_lock_respects_owner():
    fake = FakeRedis()
    lock = RedisRowLock(fake, ttl_sec=30)

    first = await lock.acquire("task-1", 82, "worker-a")
    second = await lock.acquire("task-1", 82, "worker-b")
    released_wrong = await lock.release(type(first)(first.task_id, first.row_index, "worker-b", first.acquired))
    released = await lock.release(first)

    assert first.acquired is True
    assert second.acquired is False
    assert released_wrong is False
    assert released is True


async def test_data_fetch_worker_processes_jobs_with_handler():
    async def handler(job):
        return {"product_id": job.product_id}

    worker = DataFetchWorker(handler=handler, concurrency=2)
    results = await worker.process([DataFetchJob("sku-1"), DataFetchJob("sku-2")])

    assert results == [{"product_id": "sku-1"}, {"product_id": "sku-2"}]


async def test_image_process_worker_consumes_until_stop():
    async def handler(job):
        return {"product_id": job.product_id, "count": len(job.assets)}

    worker = ImageProcessWorker(handler=handler)
    task = asyncio.create_task(worker.run())
    await worker.enqueue(ImageProcessJob("sku-1", ["a.png"]))
    await worker.stop()
    results = await task

    assert results == [{"product_id": "sku-1", "count": 1}]


async def test_gui_worker_serializes_handler_calls():
    calls = []

    async def handler(job):
        calls.append(job.name)
        return {"name": job.name}

    worker = GuiWorker(handler=handler)
    result = await worker.process(GuiJob("fill-title"))

    assert result == {"name": "fill-title"}
    assert calls == ["fill-title"]
