"""Tests for BL-101 Provider Manifest."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from jingmai_publish.runtime.manifest import (
    CapabilityCategory,
    ManifestValidationError,
    ProviderCapability,
    ProviderFactory,
    ProviderManifest,
    SchemaVersion,
    build_default_manifests,
    dump_manifest,
    load_manifest,
    validate_manifest,
)


class TestProviderCapability:
    """ProviderCapability dataclass tests."""

    def test_create_capability(self):
        cap = ProviderCapability(
            category=CapabilityCategory.OBSERVATION,
            version="1.0",
            description="Screen capture and text reading",
            input_schema={"type": "object", "properties": {"window_handle": {"type": "string"}}},
            output_schema={"type": "object", "properties": {"text": {"type": "string"}}},
        )
        assert cap.category == CapabilityCategory.OBSERVATION
        assert cap.version == "1.0"

    def test_capability_to_dict(self):
        cap = ProviderCapability(
            category=CapabilityCategory.ACTION,
            version="1.0",
            implements="click_text",
        )
        d = cap.to_dict()
        assert d["category"] == "action"
        assert d["version"] == "1.0"
        assert d["implements"] == "click_text"

    def test_all_capability_categories(self):
        """Verify all sightflow capability categories are defined."""
        categories = {c.value for c in CapabilityCategory}
        expected = {"observation", "action", "persistence", "channel", "memory", "vision", "grounding", "reflection"}
        assert categories == expected


class TestProviderManifest:
    """ProviderManifest tests."""

    def test_create_minimal_manifest(self):
        manifest = ProviderManifest(name="test-provider")
        assert manifest.name == "test-provider"
        assert manifest.version == "1.0.0"
        assert manifest.schema_version == SchemaVersion.V1_1
        assert manifest.capabilities == []
        assert manifest.dependencies == []

    def test_create_full_manifest(self):
        manifest = ProviderManifest(
            name="vision-provider",
            version="2.0.0",
            description="Ollama vision provider for screenshot analysis",
            capabilities=[
                ProviderCapability(
                    category=CapabilityCategory.VISION,
                    version="1.0",
                    description="Analyze screenshots with VLM",
                ),
            ],
            dependencies=["uia_desktop_adapter"],
            provider_class="OllamaVisionProvider",
            provider_module="jingmai_publish.providers.vision",
        )
        assert manifest.has_capability(CapabilityCategory.VISION)
        assert not manifest.has_capability(CapabilityCategory.ACTION)
        assert manifest.has_capability(CapabilityCategory.VISION) is True

    def test_get_capability(self):
        manifest = ProviderManifest(
            name="test",
            capabilities=[
                ProviderCapability(category=CapabilityCategory.VISION, version="1.0"),
            ],
        )
        cap = manifest.get_capability(CapabilityCategory.VISION)
        assert cap is not None
        assert cap.category == CapabilityCategory.VISION

        cap = manifest.get_capability(CapabilityCategory.ACTION)
        assert cap is None

    def test_to_dict(self):
        manifest = ProviderManifest(
            name="test",
            version="1.0.0",
            capabilities=[
                ProviderCapability(category=CapabilityCategory.OBSERVATION, version="1.0"),
            ],
        )
        d = manifest.to_dict()
        assert d["name"] == "test"
        assert d["version"] == "1.0.0"
        assert len(d["capabilities"]) == 1
        assert d["capabilities"][0]["category"] == "observation"


class TestManifestValidation:
    """Manifest validation tests."""

    def test_valid_manifest_passes(self):
        manifest = ProviderManifest(
            name="valid-provider",
            version="1.0.0",
            capabilities=[
                ProviderCapability(category=CapabilityCategory.OBSERVATION, version="1.0"),
            ],
        )
        issues = validate_manifest(manifest)
        assert issues == []

    def test_empty_name_fails(self):
        manifest = ProviderManifest(name="", version="1.0.0")
        issues = validate_manifest(manifest)
        assert any("name" in issue for issue in issues)

    def test_whitespace_name_fails(self):
        manifest = ProviderManifest(name="   ", version="1.0.0")
        issues = validate_manifest(manifest)
        assert any("name" in issue for issue in issues)

    def test_invalid_version_fails(self):
        manifest = ProviderManifest(name="test", version="bad")
        issues = validate_manifest(manifest)
        assert any("version" in issue for issue in issues)

    def test_duplicate_capabilities_flag(self):
        manifest = ProviderManifest(
            name="test",
            version="1.0.0",
            capabilities=[
                ProviderCapability(category=CapabilityCategory.OBSERVATION, version="1.0"),
                ProviderCapability(category=CapabilityCategory.OBSERVATION, version="1.0"),
            ],
        )
        issues = validate_manifest(manifest)
        assert any("duplicate" in issue for issue in issues)

    def test_empty_dependency_fails(self):
        manifest = ProviderManifest(
            name="test",
            version="1.0.0",
            dependencies=[""],
        )
        issues = validate_manifest(manifest)
        assert any("dependency" in issue for issue in issues)

    def test_missing_capability_version(self):
        manifest = ProviderManifest(
            name="test",
            version="1.0.0",
            capabilities=[
                ProviderCapability(category=CapabilityCategory.ACTION, version=""),
            ],
        )
        issues = validate_manifest(manifest)
        assert any("version" in issue.lower() for issue in issues)


class TestManifestSerialization:
    """Manifest dump/load round-trip tests."""

    def test_round_trip(self):
        manifest = ProviderManifest(
            name="round-trip-provider",
            version="2.1.0",
            description="Test round-trip serialization",
            capabilities=[
                ProviderCapability(
                    category=CapabilityCategory.OBSERVATION,
                    version="1.0",
                    description="observe",
                    input_schema={"type": "object"},
                ),
            ],
            dependencies=["dep-a", "dep-b"],
            provider_class="MyProvider",
            provider_module="my.module",
        )

        with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            tmp_path = f.name

        try:
            dump_manifest(manifest, tmp_path)
            loaded = load_manifest(tmp_path)

            assert loaded.name == manifest.name
            assert loaded.version == manifest.version
            assert loaded.description == manifest.description
            assert len(loaded.capabilities) == 1
            assert loaded.capabilities[0].category == CapabilityCategory.OBSERVATION
            assert loaded.dependencies == ["dep-a", "dep-b"]
            assert loaded.provider_class == "MyProvider"
            assert loaded.provider_module == "my.module"
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_load_invalid_manifest_raises(self):
        with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump({"name": "", "version": "bad"}, f)
            tmp_path = f.name

        try:
            with pytest.raises(ManifestValidationError):
                load_manifest(tmp_path)
        finally:
            Path(tmp_path).unlink(missing_ok=True)


class TestProviderFactory:
    """ProviderFactory tests."""

    def test_register_and_load(self):
        class FakeProvider:
            def __init__(self, manifest=None, config=None):
                self.manifest = manifest
                self.config = config or {}

        factory = ProviderFactory()
        factory.register("fake-provider", FakeProvider)

        manifest = ProviderManifest(
            name="fake-provider",
            version="1.0.0",
            provider_class="fake-provider",
        )
        instance = factory.load_from_manifest(manifest, {"key": "value"})
        assert isinstance(instance, FakeProvider)
        assert instance.manifest is manifest
        assert instance.config == {"key": "value"}

    def test_load_unregistered_raises(self):
        factory = ProviderFactory()
        manifest = ProviderManifest(
            name="unknown-provider",
            version="1.0.0",
        )
        with pytest.raises(ValueError, match="Cannot instantiate"):
            factory.load_from_manifest(manifest)


class TestBuildDefaultManifests:
    """Default manifests cover existing providers."""

    def test_builds_eight_manifests(self):
        manifests = build_default_manifests()
        assert len(manifests) == 8

    def test_manifests_are_valid(self):
        for manifest in build_default_manifests():
            issues = validate_manifest(manifest)
            assert issues == [], f"Manifest {manifest.name} has issues: {issues}"

    def test_manifests_have_unique_names(self):
        manifests = build_default_manifests()
        names = [m.name for m in manifests]
        assert len(names) == len(set(names))

    def test_uia_adapter_has_observation_action_grounding(self):
        manifests = build_default_manifests()
        uia = next(m for m in manifests if m.name == "uia_desktop_adapter")
        assert uia.has_capability(CapabilityCategory.OBSERVATION)
        assert uia.has_capability(CapabilityCategory.ACTION)
        assert uia.has_capability(CapabilityCategory.GROUNDING)

    def test_runtime_log_has_persistence(self):
        manifests = build_default_manifests()
        log_manifest = next(m for m in manifests if m.name == "runtime_log_persistence")
        assert log_manifest.has_capability(CapabilityCategory.PERSISTENCE)

    def test_jsonl_memory_has_memory(self):
        manifests = build_default_manifests()
        mem = next(m for m in manifests if m.name == "jsonl_memory")
        assert mem.has_capability(CapabilityCategory.MEMORY)

    def test_channel_manifest_has_channel(self):
        manifests = build_default_manifests()
        ch = next(m for m in manifests if m.name == "local_path_channel")
        assert ch.has_capability(CapabilityCategory.CHANNEL)


class TestManifestValidationEdgeCases:
    """Edge case tests for manifest validation."""

    def test_manifest_without_capabilities_is_valid(self):
        manifest = ProviderManifest(name="no-cap", version="1.0.0")
        issues = validate_manifest(manifest)
        assert issues == []

    def test_manifest_with_config_schema(self):
        manifest = ProviderManifest(
            name="with-config",
            version="1.0.0",
            config_schema={
                "type": "object",
                "properties": {
                    "api_key": {"type": "string"},
                },
                "required": ["api_key"],
            },
        )
        issues = validate_manifest(manifest)
        assert issues == []

    def test_version_with_build_metadata(self):
        manifest = ProviderManifest(name="test", version="1.2.3+build456")
        issues = validate_manifest(manifest)
        # build metadata should be fine since it contains dots
        assert issues == []
