"""Evidence archive checks for desktop screenshot artifacts."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ScreenshotEvidenceArtifact:
    path: str
    exists: bool
    source_file: str
    source_line: int
    absolute_path: str


class ScreenshotEvidenceService:
    """Collect and verify screenshot paths referenced by runtime evidence files."""

    def __init__(self, root: str | Path = ".") -> None:
        self.root = Path(root).resolve()

    def collect(self) -> dict[str, Any]:
        artifacts = self._collect_artifacts()
        present_count = sum(1 for artifact in artifacts if artifact.exists)
        missing_count = sum(1 for artifact in artifacts if not artifact.exists)
        return {
            "success": bool(artifacts) and missing_count == 0,
            "artifact_count": len(artifacts),
            "present_count": present_count,
            "missing_count": missing_count,
            "artifacts": [artifact.__dict__ for artifact in artifacts],
        }

    def _collect_artifacts(self) -> list[ScreenshotEvidenceArtifact]:
        seen: set[str] = set()
        artifacts: list[ScreenshotEvidenceArtifact] = []
        for runtime_file in self._runtime_files():
            if not runtime_file.exists():
                continue
            with runtime_file.open("r", encoding="utf-8", errors="replace") as handle:
                for line_number, line in enumerate(handle, start=1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        payload = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    for raw_path in self._find_screenshot_paths(payload):
                        normalized = raw_path.replace("\\", "/")
                        if normalized in seen:
                            continue
                        seen.add(normalized)
                        absolute_path = self._resolve_path(normalized)
                        artifacts.append(
                            ScreenshotEvidenceArtifact(
                                path=normalized,
                                exists=absolute_path.exists(),
                                source_file=str(runtime_file.relative_to(self.root)),
                                source_line=line_number,
                                absolute_path=str(absolute_path),
                            )
                        )
        return artifacts

    def _runtime_files(self) -> tuple[Path, ...]:
        return (
            self.root / "resources" / "memory" / "runtime-memory.jsonl",
            self.root / "logs" / "memory" / "runtime-memory.jsonl",
        )

    def _resolve_path(self, screenshot_path: str) -> Path:
        path = Path(screenshot_path)
        if path.is_absolute():
            return path
        return self.root / path

    def _find_screenshot_paths(self, value: Any) -> list[str]:
        paths: list[str] = []
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "screenshot_path" and isinstance(item, str) and item.strip():
                    paths.append(item.strip())
                else:
                    paths.extend(self._find_screenshot_paths(item))
        elif isinstance(value, list):
            for item in value:
                paths.extend(self._find_screenshot_paths(item))
        return paths
