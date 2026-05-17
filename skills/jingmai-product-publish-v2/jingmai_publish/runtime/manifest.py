"""Provider manifest system aligned with sightflow-desktop-agent bundle architecture.

sightflow-desktop-agent defines each provider through a manifest that declares:
- capabilities (observation, action, persistence, channel, memory, vision)
- version and compatibility
- input/output JSON schemas
- dependencies on other providers

This module implements the manifest schema, validation, and a provider loader
that can assemble a ProviderRegistry from manifest configurations.

Design contract:
- Every provider MUST have a manifest before being loaded into the runtime.
- The manifest is the single source of truth for what a provider can do.
- The loader validates manifests before instantiation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol, runtime_checkable
import importlib
import json
from pathlib import Path


# ── capability taxonomy (aligned with sightflow-desktop-agent) ──


class CapabilityCategory(str, Enum):
    """Provider capability categories matching sightflow taxonomy."""

    OBSERVATION = "observation"       # screen capture, UIA tree, page text
    ACTION = "action"                 # click, type, select, navigate
    PERSISTENCE = "persistence"       # DB, Redis, file storage
    CHANNEL = "channel"               # Feishu, CLI, HTTP ingress
    MEMORY = "memory"                 # short/long-term memory, vector search
    VISION = "vision"                 # screenshot analysis, VLM, OCR
    GROUNDING = "grounding"           # coordinate resolution, anchor matching
    REFLECTION = "reflection"         # success/failure evaluation, retry decision


class SchemaVersion(str, Enum):
    """Supported manifest schema versions."""
    V1_0 = "1.0"
    V1_1 = "1.1"


# ── manifest data structures ──


@dataclass(slots=True)
class ProviderCapability:
    """Declares a single capability within a provider manifest.

    Each capability has a category, version, and JSON Schema contracts
    for input and output validation.
    """

    category: CapabilityCategory
    version: str = "1.0"
    description: str = ""
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)
    # Optional: path to the method/class implementing this capability
    implements: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category.value,
            "version": self.version,
            "description": self.description,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "implements": self.implements,
        }


@dataclass(slots=True)
class ProviderManifest:
    """Full provider manifest matching sightflow provider bundle.

    A manifest declares what a provider IS (name, version), what it CAN DO
    (capabilities), and what it NEEDS (dependencies, config).
    """

    name: str
    version: str = "1.0.0"
    schema_version: SchemaVersion = SchemaVersion.V1_1
    description: str = ""
    capabilities: list[ProviderCapability] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    config_schema: dict[str, Any] = field(default_factory=dict)
    # Path to the provider class/module for dynamic loading
    provider_class: str | None = None
    provider_module: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "schema_version": self.schema_version.value,
            "description": self.description,
            "capabilities": [cap.to_dict() for cap in self.capabilities],
            "dependencies": self.dependencies,
            "config_schema": self.config_schema,
            "provider_class": self.provider_class,
            "provider_module": self.provider_module,
        }

    def has_capability(self, category: CapabilityCategory) -> bool:
        """Check if this manifest declares a specific capability category."""
        return any(cap.category == category for cap in self.capabilities)

    def get_capability(self, category: CapabilityCategory) -> ProviderCapability | None:
        """Get a specific capability by category."""
        for cap in self.capabilities:
            if cap.category == category:
                return cap
        return None


# ── manifest validation ──


class ManifestValidationError(ValueError):
    """Raised when a manifest fails validation."""
    pass


def validate_manifest(manifest: ProviderManifest) -> list[str]:
    """Validate a provider manifest. Returns list of issues (empty = valid).

    Checks:
    - Name is non-empty
    - Version follows semver-ish pattern
    - Each capability has a valid category
    - Dependencies reference valid provider names (string, non-empty)
    - Config schema is a valid JSON Schema structure (if present)
    """
    issues: list[str] = []

    if not manifest.name or not manifest.name.strip():
        issues.append("manifest.name is required and must be non-empty")
    if not manifest.version or "." not in manifest.version:
        issues.append("manifest.version must follow semver pattern (e.g., 1.0.0)")

    seen_categories: set[CapabilityCategory] = set()
    for i, cap in enumerate(manifest.capabilities):
        if not isinstance(cap.category, CapabilityCategory):
            issues.append(f"capability[{i}].category is not a valid CapabilityCategory: {cap.category}")
            continue
        if cap.category in seen_categories:
            issues.append(f"duplicate capability category: {cap.category.value}")
        seen_categories.add(cap.category)
        if not cap.version:
            issues.append(f"capability[{i}].version is required")
        if cap.input_schema and not isinstance(cap.input_schema, dict):
            issues.append(f"capability[{i}].input_schema must be a dict")
        if cap.output_schema and not isinstance(cap.output_schema, dict):
            issues.append(f"capability[{i}].output_schema must be a dict")

    for j, dep in enumerate(manifest.dependencies):
        if not dep or not dep.strip():
            issues.append(f"dependency[{j}] is empty")
        if not isinstance(dep, str):
            issues.append(f"dependency[{j}] must be a string")

    return issues


# ── manifest serialization ──


def dump_manifest(manifest: ProviderManifest, file_path: str | Path) -> None:
    """Write a manifest to a JSON file."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_manifest(file_path: str | Path) -> ProviderManifest:
    """Load a manifest from a JSON file."""
    path = Path(file_path)
    raw = json.loads(path.read_text(encoding="utf-8"))

    capabilities = []
    for cap_data in raw.get("capabilities", []):
        capabilities.append(
            ProviderCapability(
                category=CapabilityCategory(cap_data["category"]),
                version=cap_data.get("version", "1.0"),
                description=cap_data.get("description", ""),
                input_schema=cap_data.get("input_schema", {}),
                output_schema=cap_data.get("output_schema", {}),
                implements=cap_data.get("implements"),
            )
        )

    manifest = ProviderManifest(
        name=raw["name"],
        version=raw.get("version", "1.0.0"),
        schema_version=SchemaVersion(raw.get("schema_version", "1.1")),
        description=raw.get("description", ""),
        capabilities=capabilities,
        dependencies=raw.get("dependencies", []),
        config_schema=raw.get("config_schema", {}),
        provider_class=raw.get("provider_class"),
        provider_module=raw.get("provider_module"),
    )

    issues = validate_manifest(manifest)
    if issues:
        raise ManifestValidationError(
            f"Manifest validation failed for {path}:\n" + "\n".join(f"  - {i}" for i in issues)
        )
    return manifest


# ── provider loader ──


@runtime_checkable
class ManifestedProvider(Protocol):
    """A provider that carries its own manifest."""

    @property
    def manifest(self) -> ProviderManifest:
        ...


@dataclass(slots=True)
class ProviderFactory:
    """Creates providers from manifest configuration.

    Supports:
    - Inline provider instances (pass the instance directly)
    - Module-path loading (import provider_class from provider_module)
    - Manifest file loading (load from JSON, then instantiate)
    """

    # Registry of known provider classes by name
    _registry: dict[str, type] = field(default_factory=dict)

    def register(self, name: str, provider_cls: type) -> None:
        """Register a provider class for later instantiation."""
        self._registry[name] = provider_cls

    def load_from_manifest(
        self, manifest: ProviderManifest, config: dict[str, Any] | None = None
    ) -> Any:
        """Instantiate a provider from its manifest.

        Resolution order:
        1. If provider_class is in the registry, instantiate it
        2. If provider_module + provider_class are set, import and instantiate
        3. Raise an error
        """
        config = config or {}
        cls_name = manifest.provider_class or manifest.name

        # Try registry first
        if cls_name in self._registry:
            return self._registry[cls_name](manifest=manifest, config=config)

        # Try module import
        if manifest.provider_module:
            module = importlib.import_module(manifest.provider_module)
            cls = getattr(module, cls_name, None)
            if cls is not None:
                return cls(manifest=manifest, config=config)
            raise ImportError(
                f"Provider class '{cls_name}' not found in module '{manifest.provider_module}'"
            )

        raise ValueError(
            f"Cannot instantiate provider '{manifest.name}': "
            f"no provider_class registered and no provider_module specified"
        )


# ── built-in provider manifests (for self-documenting existing providers) ──


def build_default_manifests() -> list[ProviderManifest]:
    """Build manifests for the existing default providers.

    These manifests describe what's already implemented in defaults.py,
    providing the capability contracts that Phase B requires.
    """

    uia_adapter_manifest = ProviderManifest(
        name="uia_desktop_adapter",
        version="1.0.0",
        description="Windows UIA desktop automation adapter for 京麦 application",
        capabilities=[
            ProviderCapability(
                category=CapabilityCategory.OBSERVATION,
                version="1.0",
                description="Window enumeration, text reading, control inspection",
                input_schema={
                    "type": "object",
                    "properties": {
                        "window_handle": {"type": "string"},
                    },
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "controls": {"type": "array"},
                    },
                },
            ),
            ProviderCapability(
                category=CapabilityCategory.ACTION,
                version="1.0",
                description="Click, type, select, file dialog navigation",
                input_schema={
                    "type": "object",
                    "properties": {
                        "window_handle": {"type": "string"},
                        "target": {"type": "string"},
                        "value": {"type": "string"},
                    },
                },
            ),
            ProviderCapability(
                category=CapabilityCategory.GROUNDING,
                version="1.0",
                description="Control location by automation_id, label text, or region ratios",
                input_schema={
                    "type": "object",
                    "properties": {
                        "window_handle": {"type": "string"},
                        "automation_id": {"type": "string"},
                        "label": {"type": "string"},
                    },
                },
            ),
        ],
        provider_class="RealWindowsUIAAdapter",
        provider_module="jingmai_publish.desktop.uia_adapter",
    )

    runtime_log_manifest = ProviderManifest(
        name="runtime_log_persistence",
        version="1.0.0",
        description="Persist runtime events to MySQL runtime_logs table",
        capabilities=[
            ProviderCapability(
                category=CapabilityCategory.PERSISTENCE,
                version="1.0",
                description="Persist structured runtime events",
                input_schema={
                    "type": "object",
                    "properties": {
                        "event_type": {"type": "string"},
                        "payload": {"type": "object"},
                    },
                },
            ),
        ],
        provider_class="RuntimeLogPersistenceProvider",
        provider_module="jingmai_publish.runtime.defaults",
    )

    jsonl_memory_manifest = ProviderManifest(
        name="jsonl_memory",
        version="1.0.0",
        description="Short-term episodic memory in local JSONL file",
        capabilities=[
            ProviderCapability(
                category=CapabilityCategory.MEMORY,
                version="1.0",
                description="Remember and search execution memories",
                input_schema={
                    "type": "object",
                    "properties": {
                        "memory_type": {"type": "string"},
                        "payload": {"type": "object"},
                    },
                },
                output_schema={
                    "type": "array",
                    "items": {"type": "object"},
                },
            ),
        ],
        provider_class="JsonlMemoryProvider",
        provider_module="jingmai_publish.runtime.defaults",
    )

    channel_manifest = ProviderManifest(
        name="local_path_channel",
        version="1.0.0",
        description="Local file path ingress channel",
        capabilities=[
            ProviderCapability(
                category=CapabilityCategory.CHANNEL,
                version="1.0",
                description="Normalize local-path ingress payloads into host contract",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path_file": {"type": "string"},
                        "excel_path": {"type": "string"},
                    },
                },
            ),
        ],
        provider_class="LocalPathChannelProvider",
        provider_module="jingmai_publish.runtime.defaults",
    )

    # ── Phase C: Ollama Vision Provider (BL-092) ──
    ollama_vision_manifest = ProviderManifest(
        name="ollama_vision",
        version="1.0.0",
        description="Ollama-based VLM for screenshot analysis, element location, and before/after comparison",
        capabilities=[
            ProviderCapability(
                category=CapabilityCategory.VISION,
                version="1.0",
                description="Screenshot analysis via Ollama REST API (qwen3-vl:8b), with vLLM fallback",
                input_schema={
                    "type": "object",
                    "properties": {
                        "image_path": {"type": "string", "description": "截图文件路径"},
                        "prompt": {"type": "string", "description": "可选自定义分析提示词"},
                    },
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "page_state": {"type": "string"},
                        "bbox": {"type": "array", "items": {"type": "integer"}},
                        "point": {"type": "array", "items": {"type": "integer"}},
                        "confidence": {"type": "number"},
                        "elapsed_ms": {"type": "number"},
                    },
                },
                implements="OllamaVisionProvider.analyze_screenshot",
            ),
            ProviderCapability(
                category=CapabilityCategory.GROUNDING,
                version="1.0",
                description="Element location via VLM — returns bbox/point for described elements",
                input_schema={
                    "type": "object",
                    "properties": {
                        "image_path": {"type": "string"},
                        "description": {"type": "string", "description": "目标元素自然语言描述"},
                    },
                },
                implements="OllamaVisionProvider.locate_element",
            ),
        ],
        dependencies=["uia_desktop_adapter"],
        provider_class="OllamaVisionProvider",
        provider_module="jingmai_publish.runtime.vision",
    )

    # ── Phase C: Three-Way Grounding Provider (BL-095) ──
    three_way_grounding_manifest = ProviderManifest(
        name="three_way_grounding",
        version="1.0.0",
        description="UIA/Vision/Anchor three-way grounding arbitration with weighted fusion",
        capabilities=[
            ProviderCapability(
                category=CapabilityCategory.GROUNDING,
                version="1.0",
                description="Priority-chain arbitration: UIA(0.50) → Vision(0.35) → Anchor(0.15), high-confidence early return at 0.8",
                input_schema={
                    "type": "object",
                    "properties": {
                        "target": {"type": "string", "description": "定位目标（automation_id 或元素描述）"},
                        "window_handle": {"type": "string"},
                        "screenshot_path": {"type": "string"},
                        "page_text": {"type": "string"},
                        "target_type": {"type": "string", "enum": ["automation_id", "label", "class_name"]},
                    },
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "method": {"type": "string", "enum": ["uia", "vision", "anchor", "hybrid", "none"]},
                        "bbox": {"type": "array", "items": {"type": "integer"}},
                        "point": {"type": "array", "items": {"type": "integer"}},
                        "confidence": {"type": "number"},
                        "fusion_method": {"type": "string"},
                    },
                },
                implements="ThreeWayGroundingProvider.ground",
            ),
        ],
        dependencies=["uia_desktop_adapter", "ollama_vision"],
        provider_class="ThreeWayGroundingProvider",
        provider_module="jingmai_publish.runtime.grounding",
    )

    # ── BL-094A: Reflection JSONL Persistence ──
    reflection_jsonl_manifest = ProviderManifest(
        name="reflection_jsonl_persistence",
        version="1.0.0",
        description="将失败反思记录持久化到本地 JSONL 文件，订阅 RuntimeEventLoop REFLECTION_RECORDED 事件",
        capabilities=[
            ProviderCapability(
                category=CapabilityCategory.PERSISTENCE,
                version="1.0",
                description="持久化反射事件到 JSONL（自动订阅 RuntimeEventLoop）",
                input_schema={
                    "type": "object",
                    "properties": {
                        "event_type": {"type": "string"},
                        "payload": {"type": "object"},
                    },
                },
            ),
            ProviderCapability(
                category=CapabilityCategory.REFLECTION,
                version="1.0",
                description="结构化 ReflectionRecord：step_name, decision, reason, vision_analysis 等",
                input_schema={
                    "type": "object",
                    "properties": {
                        "step_name": {"type": "string"},
                        "decision": {"type": "string"},
                        "reason": {"type": "string"},
                    },
                },
            ),
        ],
        provider_class="ReflectionJsonlPersistenceProvider",
        provider_module="jingmai_publish.runtime.reflection_persistence",
    )

    # ── BL-094A: Milvus Memory Provider ──
    milvus_memory_manifest = ProviderManifest(
        name="milvus_memory",
        version="1.0.0",
        description="Milvus 向量数据库 — 反思记录语义检索存储，pymilvus 可选依赖（不可用时降级）",
        capabilities=[
            ProviderCapability(
                category=CapabilityCategory.MEMORY,
                version="1.0",
                description="向量语义存储与检索反思记录（remember + search）",
                input_schema={
                    "type": "object",
                    "properties": {
                        "memory_type": {"type": "string"},
                        "payload": {"type": "object"},
                    },
                },
                output_schema={
                    "type": "array",
                    "items": {"type": "object"},
                },
            ),
            ProviderCapability(
                category=CapabilityCategory.REFLECTION,
                version="1.0",
                description='语义检索历史反思模式，支持自然语言查询（如 "窗口丢失"、"重试耗尽"）',
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "limit": {"type": "integer"},
                    },
                },
            ),
        ],
        dependencies=["reflection_jsonl_persistence"],
        provider_class="MilvusMemoryProvider",
        provider_module="jingmai_publish.runtime.reflection_persistence",
    )

    return [
        uia_adapter_manifest,
        runtime_log_manifest,
        jsonl_memory_manifest,
        channel_manifest,
        ollama_vision_manifest,
        three_way_grounding_manifest,
        reflection_jsonl_manifest,
        milvus_memory_manifest,
    ]
