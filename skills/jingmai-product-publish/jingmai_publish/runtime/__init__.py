"""Runtime host/provider abstractions.

Phase B: added RuntimeEventLoop (BL-100) and ProviderManifest (BL-101).
Phase C: added OllamaVisionProvider (BL-092) and ThreeWayGroundingProvider (BL-095).
Phase C: added ReflectionJsonlPersistenceProvider + MilvusMemoryProvider (BL-094A).
"""

from .defaults import (
    FeishuChannelProvider,
    JsonlMemoryProvider,
    LocalPathChannelProvider,
    RuntimeLogPersistenceProvider,
)
from .event_loop import (
    EventStatus,
    EventType,
    LoopSessionState,
    RuntimeEvent,
    RuntimeEventLoop,
)
from .grounding import (
    AnchorGroundingAdapter,
    GroundingCandidate,
    GroundingResult,
    ThreeWayGroundingProvider,
    UIAGroundingAdapter,
)
from .kernel import HostRuntime
from .manifest import (
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
from .providers import (
    ActionProvider,
    ChannelProvider,
    GroundingProvider,
    MemoryProvider,
    ObservationProvider,
    PersistenceProvider,
    ProviderRegistry,
    VisionProvider,
)
from .reflection_persistence import (
    MilvusMemoryProvider,
    ReflectionJsonlPersistenceProvider,
)
from .vision import (
    OllamaVisionProvider,
    VisionAnalysis,
    create_vision_provider_from_env,
)

__all__ = [
    # kernel
    "HostRuntime",
    # providers
    "ActionProvider",
    "ChannelProvider",
    "GroundingProvider",
    "MemoryProvider",
    "ObservationProvider",
    "PersistenceProvider",
    "ProviderRegistry",
    "VisionProvider",
    # defaults
    "FeishuChannelProvider",
    "JsonlMemoryProvider",
    "LocalPathChannelProvider",
    "RuntimeLogPersistenceProvider",
    # event loop (BL-100)
    "EventStatus",
    "EventType",
    "LoopSessionState",
    "RuntimeEvent",
    "RuntimeEventLoop",
    # manifest (BL-101)
    "CapabilityCategory",
    "ManifestValidationError",
    "ProviderCapability",
    "ProviderFactory",
    "ProviderManifest",
    "SchemaVersion",
    "build_default_manifests",
    "dump_manifest",
    "load_manifest",
    "validate_manifest",
    # vision (BL-092)
    "OllamaVisionProvider",
    "VisionAnalysis",
    "create_vision_provider_from_env",
    # grounding (BL-095)
    "AnchorGroundingAdapter",
    "GroundingCandidate",
    "GroundingResult",
    "ThreeWayGroundingProvider",
    "UIAGroundingAdapter",
    # reflection persistence (BL-094A)
    "MilvusMemoryProvider",
    "ReflectionJsonlPersistenceProvider",
]
