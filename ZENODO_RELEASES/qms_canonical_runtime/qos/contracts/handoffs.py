"""Immutable handoff objects for strict QMS causal layer separation.

These objects are the only canonical payloads that should cross layer
boundaries. They intentionally avoid references to lower-layer mutable runtime
objects so information loss remains explicit and irreversible.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional, Tuple

ArrayShape = Tuple[int, ...]
Metadata = Mapping[str, Any]


def _freeze_metadata(metadata: Optional[Metadata]) -> Metadata:
    return MappingProxyType(dict(metadata or {}))


@dataclass(frozen=True)
class ImprintFieldState:
    """Foundation output: pre-measurement field state and public descriptors."""

    state_id: str
    shape: ArrayShape
    coordinates: Metadata = field(default_factory=dict)
    parameters: Metadata = field(default_factory=dict)
    lineage: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "coordinates", _freeze_metadata(self.coordinates))
        object.__setattr__(self, "parameters", _freeze_metadata(self.parameters))


@dataclass(frozen=True)
class DetectorSignal:
    """Measurement output: detector-formed signal after correlation selection."""

    signal_id: str
    source_state_id: str
    detector_model: str
    shape: ArrayShape
    preserved_correlations: Tuple[str, ...] = ()
    destroyed_correlations: Tuple[str, ...] = ()
    irreversible_loss: bool = True
    metadata: Metadata = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", _freeze_metadata(self.metadata))


@dataclass(frozen=True)
class DigitalRecord:
    """Acquisition output: sampled, digitized, and stored measurement record."""

    record_id: str
    source_signal_id: str
    sampling_rate_hz: Optional[float]
    bit_depth: Optional[int]
    shape: ArrayShape
    transforms: Tuple[str, ...] = ()
    metadata: Metadata = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", _freeze_metadata(self.metadata))


@dataclass(frozen=True)
class DiagnosticReport:
    """Diagnostics output: validated metrics and confidence over records."""

    report_id: str
    source_record_id: str
    metrics: Metadata
    confidence: Metadata = field(default_factory=dict)
    limitations: Tuple[str, ...] = ()
    metadata: Metadata = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "metrics", _freeze_metadata(self.metrics))
        object.__setattr__(self, "confidence", _freeze_metadata(self.confidence))
        object.__setattr__(self, "metadata", _freeze_metadata(self.metadata))


@dataclass(frozen=True)
class ControlDecision:
    """Control output: auditable action for future runs only."""

    decision_id: str
    source_report_id: str
    action: str
    applies_to_future_run: bool = True
    parameters: Metadata = field(default_factory=dict)
    rationale: str = ""
    metadata: Metadata = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.applies_to_future_run:
            raise ValueError("ControlDecision must apply only to future runs.")
        object.__setattr__(self, "parameters", _freeze_metadata(self.parameters))
        object.__setattr__(self, "metadata", _freeze_metadata(self.metadata))

