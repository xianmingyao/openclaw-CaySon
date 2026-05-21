from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor

from jingmai_publish.runtime.defaults import JsonlMemoryProvider


def test_jsonl_memory_provider_concurrent_writes_are_valid_json_lines(tmp_path):
    target = tmp_path / "memory.jsonl"

    def write(index: int) -> None:
        provider = JsonlMemoryProvider(target)
        provider.remember("event", {"index": index, "text": f"payload-{index}"})

    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(write, range(40)))

    lines = target.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 40
    records = [json.loads(line) for line in lines]
    assert {record["payload"]["index"] for record in records} == set(range(40))
    assert not target.with_name("memory.jsonl.lock").exists()
