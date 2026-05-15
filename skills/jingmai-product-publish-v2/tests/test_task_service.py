import json

from jingmai_publish.services.task_service import PublishTaskService


class DummyTask:
    def __init__(self, task_id, session_id, job_id, job_item_id, mode, store_id):
        self.task_id = task_id
        self.session_id = session_id
        self.job_id = job_id
        self.job_item_id = job_item_id
        self.mode = mode
        self.store_id = store_id
        self.status = "pending"
        self.current_step = None
        self.page_state = None


class DummyTaskRepo:
    def __init__(self):
        self.created = []
        self.updated = []

    def create_task(self, **kwargs):
        task = DummyTask(**kwargs)
        self.created.append(task)
        return task

    def update_task_status(self, task_id, status, **kwargs):
        self.updated.append((task_id, status, kwargs))


class DummyStepRepo:
    def __init__(self):
        self.steps = []
        self.updated = []

    def create_step(self, **kwargs):
        self.steps.append(kwargs)
        return kwargs

    def update_step_status(self, task_id, step_id, sequence_no, **kwargs):
        self.updated.append((task_id, step_id, sequence_no, kwargs))
        return kwargs


class DummyUploadJobRepo:
    def list_job_items(self, job_id):
        return [type("JobItem", (), {"id": 1, "row_no": 1})]


class DummyRuntimeLogRepo:
    def __init__(self):
        self.logs = []

    def append_log(self, **kwargs):
        self.logs.append(kwargs)
        return kwargs


def test_create_task_for_job_item_records_initial_audit_step():
    task_repo = DummyTaskRepo()
    step_repo = DummyStepRepo()
    service = PublishTaskService(
        task_repo=task_repo,
        upload_job_repo=DummyUploadJobRepo(),
        runtime_log_repo=DummyRuntimeLogRepo(),
        task_step_repo=step_repo,
    )

    task = service.create_task_for_job_item("job-1", 99, "draft", "store-a")

    assert task.task_id.startswith("task-")
    assert len(step_repo.steps) == 1
    assert step_repo.steps[0]["step_id"] == "TASK_CREATED"
    payload = json.loads(step_repo.steps[0]["action_payload_json"])
    assert payload["job_item_id"] == 99
    assert step_repo.updated[0][3]["status"] == "succeeded"
    assert task_repo.updated[0][1] == "pending"
    assert task_repo.updated[0][2]["current_step"] == "TASK_CREATED"


def test_create_tasks_for_job_writes_runtime_log():
    task_repo = DummyTaskRepo()
    step_repo = DummyStepRepo()
    log_repo = DummyRuntimeLogRepo()
    service = PublishTaskService(
        task_repo=task_repo,
        upload_job_repo=DummyUploadJobRepo(),
        runtime_log_repo=log_repo,
        task_step_repo=step_repo,
    )

    task_ids = service.create_tasks_for_job("job-1", mode="draft", store_id="store-a")

    assert len(task_ids) == 1
    assert len(log_repo.logs) == 1
    assert log_repo.logs[0]["task_id"] == task_ids[0]
    assert len(step_repo.steps) == 1
