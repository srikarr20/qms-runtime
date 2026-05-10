"""Canonical diagnostics runtime for QOS DigitalRecord handoffs.

Diagnostics consume only ``DigitalRecord`` objects and emit canonical
``DiagnosticReport`` objects. Metrics here are record-level diagnostics: they
may use metadata already present on the record, but they never reconstruct
field states, detector signals, or destroyed correlations.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Optional, Tuple

from qos.contracts import DiagnosticReport, DigitalRecord


DIAGNOSTICS_API_VERSION = "qos.diagnostics.runtime.v1"
QMCTB_COMPATIBILITY = ("QMCTB-01", "QMCTB-02", "QMCTB-03")
RECONSTRUCTION_LIMITATIONS = (
    "diagnostics consume DigitalRecord only",
    "destroyed upstream correlations are unavailable and unreconstructed",
    "reported coherence metrics are record-level observability diagnostics",
)


def _clamp_unit(value: float) -> float:
    if math.isnan(value):
        return 0.0
    return max(0.0, min(1.0, float(value)))


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class VisibilityDiagnostic:
    """Record-level visibility diagnostic promoted from QMCTB visibility scripts."""

    threshold: float = 0.8
    metric_name: str = "visibility"

    def __post_init__(self) -> None:
        if not 0.0 < self.threshold <= 1.0:
            raise ValueError("VisibilityDiagnostic.threshold must be in (0, 1].")

    def evaluate(self, record: DigitalRecord) -> Mapping[str, Any]:
        metadata = _mapping(record.metadata)
        policy = _mapping(metadata.get("policy"))
        observability = _mapping(policy.get("observability_scaling"))
        spatial = _mapping(policy.get("spatial_decoherence"))
        preserved_count = int(metadata.get("preserved_correlation_count", 0))
        destroyed_count = int(metadata.get("destroyed_upstream_correlation_count", 0))
        total = max(1, preserved_count + destroyed_count)
        correlation_access = preserved_count / total
        observability_index = _float(observability.get("observability_index"), 1.0)
        spatial_factor = _float(spatial.get("contrast_factor"), 1.0)
        bit_depth_factor = _clamp_unit((record.bit_depth or 0) / 16.0)
        visibility_index = _clamp_unit(
            correlation_access * observability_index * spatial_factor * bit_depth_factor
        )
        uncertainty = math.sqrt(2.0 / max(_record_sample_count(record.shape), 1)) * visibility_index
        return {
            "visibility_index": visibility_index,
            "visibility_threshold": self.threshold,
            "high_visibility": visibility_index >= self.threshold,
            "visibility_uncertainty": uncertainty,
            "correlation_access": correlation_access,
            "record_level_metric": True,
            "source": "DigitalRecord.metadata",
        }


@dataclass(frozen=True)
class CoherenceTransferDiagnostic:
    """Coherence transfer function diagnostic compatible with QMCTB-02."""

    threshold: float = 0.8
    model: str = "gaussian-phase-transfer"

    def __post_init__(self) -> None:
        if not 0.0 < self.threshold <= 1.0:
            raise ValueError("CoherenceTransferDiagnostic.threshold must be in (0, 1].")

    def transfer(self, sigma_radians: float) -> float:
        return math.exp(-(float(sigma_radians) ** 2))

    def evaluate(self, record: DigitalRecord) -> Mapping[str, Any]:
        policy = _mapping(_mapping(record.metadata).get("policy"))
        spatial = _mapping(policy.get("spatial_decoherence"))
        bandwidth = _mapping(policy.get("bandwidth_limit"))
        sigma = _float(spatial.get("sigma_radians"), 0.0)
        phase_transfer = self.transfer(sigma)
        bandwidth_ratio = _float(bandwidth.get("bandwidth_ratio"), 1.0)
        transfer_gain = _clamp_unit(phase_transfer * bandwidth_ratio)
        return {
            "model": self.model,
            "sigma_radians": sigma,
            "phase_transfer": phase_transfer,
            "bandwidth_ratio": bandwidth_ratio,
            "transfer_gain": transfer_gain,
            "transfer_threshold": self.threshold,
            "coherence_preserved": transfer_gain >= self.threshold,
            "compatible_with_qmctb02": True,
            "future_adaptive_metric_hook": "adaptive coherence metrics may replace static transfer",
        }


@dataclass(frozen=True)
class ObservabilityDiagnostic:
    """Geometry-neutral DPI/QMCTB-03 observability diagnostic."""

    threshold: float = 0.75

    def __post_init__(self) -> None:
        if not 0.0 < self.threshold <= 1.0:
            raise ValueError("ObservabilityDiagnostic.threshold must be in (0, 1].")

    def evaluate(self, record: DigitalRecord) -> Mapping[str, Any]:
        policy = _mapping(_mapping(record.metadata).get("policy"))
        observability = _mapping(policy.get("observability_scaling"))
        index = _float(observability.get("observability_index"), 1.0)
        threshold = _float(observability.get("visibility_threshold"), self.threshold)
        return {
            "observability_index": index,
            "observability_threshold": threshold,
            "observability_degraded": bool(observability.get("observability_degraded", index < threshold)),
            "sampling_ratio": _float(observability.get("sampling_ratio"), 1.0),
            "effective_bin_scale": int(observability.get("effective_bin_scale", 1)),
            "geometry_neutral": bool(observability.get("geometry_neutral", True)),
            "dpi_axes": tuple(observability.get("dpi_axes", ())),
            "compatible_with_qmctb03": bool(observability.get("compatible_with_qmctb03", True)),
            "streaming_observability_hook": "streaming windows may supply incremental DigitalRecord reports",
        }


@dataclass(frozen=True)
class SpatialDecoherenceDiagnostic:
    """Spatial measurement decoherence diagnostic from acquisition metadata."""

    def evaluate(self, record: DigitalRecord) -> Mapping[str, Any]:
        policy = _mapping(_mapping(record.metadata).get("policy"))
        spatial = _mapping(policy.get("spatial_decoherence"))
        sigma = _float(spatial.get("sigma_radians"), 0.0)
        contrast = _float(spatial.get("contrast_factor"), math.exp(-(sigma**2)))
        return {
            "model": spatial.get("model", "none"),
            "sigma_radians": sigma,
            "correlation_length_pixels": spatial.get("correlation_length_pixels"),
            "contrast_factor": contrast,
            "spatial_decoherence_detected": sigma > 0.0 or contrast < 1.0,
            "irreversible": bool(spatial.get("irreversible", sigma > 0.0)),
        }


@dataclass(frozen=True)
class DetectorFidelityDiagnostic:
    """Detector fidelity proxy derived from record-visible causal metadata."""

    def evaluate(self, record: DigitalRecord) -> Mapping[str, Any]:
        metadata = _mapping(record.metadata)
        policy = _mapping(metadata.get("policy"))
        observability = _mapping(policy.get("observability_scaling"))
        preserved_count = int(metadata.get("preserved_correlation_count", 0))
        destroyed_count = int(metadata.get("destroyed_upstream_correlation_count", 0))
        total = max(1, preserved_count + destroyed_count)
        correlation_fidelity = preserved_count / total
        observability_index = _float(observability.get("observability_index"), 1.0)
        bit_depth_factor = _clamp_unit((record.bit_depth or 0) / 16.0)
        detector_fidelity = _clamp_unit(correlation_fidelity * observability_index * bit_depth_factor)
        return {
            "detector_fidelity_index": detector_fidelity,
            "correlation_fidelity": correlation_fidelity,
            "bit_depth_factor": bit_depth_factor,
            "distributed_detector_diagnostics_hook": "topology-aware fidelity can be added per detector array element",
            "record_level_only": True,
        }


@dataclass(frozen=True)
class CanonicalDiagnosticsRuntime:
    """Promoted QMCTB diagnostics runtime for canonical QOS execution."""

    runtime_id: str = "canonical-qmctb-diagnostics"
    visibility: VisibilityDiagnostic = field(default_factory=VisibilityDiagnostic)
    coherence_transfer: CoherenceTransferDiagnostic = field(
        default_factory=CoherenceTransferDiagnostic
    )
    observability: ObservabilityDiagnostic = field(default_factory=ObservabilityDiagnostic)
    spatial_decoherence: SpatialDecoherenceDiagnostic = field(
        default_factory=SpatialDecoherenceDiagnostic
    )
    detector_fidelity: DetectorFidelityDiagnostic = field(
        default_factory=DetectorFidelityDiagnostic
    )
    adaptive_coherence_metric_hook: Optional[str] = None
    distributed_detector_hook: Optional[str] = None
    streaming_observability_hook: Optional[str] = None

    def diagnose(
        self, record: DigitalRecord, provenance: Mapping[str, Any]
    ) -> DiagnosticReport:
        if not isinstance(record, DigitalRecord):
            raise TypeError("Canonical diagnostics may consume DigitalRecord only.")

        metrics = {
            "visibility": self.visibility.evaluate(record),
            "coherence_transfer": self.coherence_transfer.evaluate(record),
            "observability": self.observability.evaluate(record),
            "spatial_decoherence": self.spatial_decoherence.evaluate(record),
            "detector_fidelity": self.detector_fidelity.evaluate(record),
            "record": {
                "record_shape": record.shape,
                "sampling_rate_hz": record.sampling_rate_hz,
                "bit_depth": record.bit_depth,
                "transform_count": len(record.transforms),
                "transforms": record.transforms,
            },
        }
        confidence = _confidence(metrics)
        return DiagnosticReport(
            report_id=_stable_report_id(record, self.runtime_id),
            source_record_id=record.record_id,
            metrics=metrics,
            confidence=confidence,
            limitations=RECONSTRUCTION_LIMITATIONS,
            metadata={
                "provenance": dict(provenance),
                "runtime": DIAGNOSTICS_API_VERSION,
                "runtime_id": self.runtime_id,
                "causal_order": "DigitalRecord -> DiagnosticReport",
                "input_contract": "DigitalRecord",
                "output_contract": "DiagnosticReport",
                "compatibility_targets": QMCTB_COMPATIBILITY,
                "geometry_neutral_dpi_semantics": True,
                "reconstruction_policy": "no upstream reconstruction",
                "future_extensibility": {
                    "adaptive_coherence_metrics": self.adaptive_coherence_metric_hook
                    or "extension-point",
                    "distributed_detector_diagnostics": self.distributed_detector_hook
                    or "extension-point",
                    "streaming_observability_analysis": self.streaming_observability_hook
                    or "extension-point",
                },
                "runtime_provenance": {
                    "api_version": DIAGNOSTICS_API_VERSION,
                    "diagnostics_digest": _diagnostics_digest(self),
                    "record_id": record.record_id,
                },
            },
        )


def diagnose_digital_record(
    record: DigitalRecord,
    *,
    runtime: Optional[CanonicalDiagnosticsRuntime] = None,
    provenance: Optional[Mapping[str, Any]] = None,
) -> DiagnosticReport:
    """Reusable functional API for canonical diagnostics."""
    return (runtime or CanonicalDiagnosticsRuntime()).diagnose(
        record,
        dict(provenance or {}),
    )


def _confidence(metrics: Mapping[str, Any]) -> Mapping[str, Any]:
    visibility = _mapping(metrics.get("visibility"))
    observability = _mapping(metrics.get("observability"))
    detector_fidelity = _mapping(metrics.get("detector_fidelity"))
    visibility_uncertainty = _float(visibility.get("visibility_uncertainty"), 0.0)
    record_level_confidence = _clamp_unit(
        (
            _float(visibility.get("visibility_index"), 0.0)
            + _float(observability.get("observability_index"), 0.0)
            + _float(detector_fidelity.get("detector_fidelity_index"), 0.0)
        )
        / 3.0
    )
    return {
        "record_level_only": True,
        "upstream_irreversibility_respected": True,
        "no_reconstruction_attempted": True,
        "visibility_uncertainty": visibility_uncertainty,
        "diagnostic_confidence_index": record_level_confidence,
    }


def _record_sample_count(shape: Tuple[int, ...]) -> int:
    if not shape:
        return 0
    axes = shape[-2:] if len(shape) >= 2 else shape
    total = 1
    for item in axes:
        total *= max(0, int(item))
    return total


def _stable_report_id(record: DigitalRecord, runtime_id: str) -> str:
    payload = f"{record.record_id}:{runtime_id}:{DIAGNOSTICS_API_VERSION}"
    return "diag-" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _diagnostics_digest(runtime: CanonicalDiagnosticsRuntime) -> str:
    payload = repr(asdict(runtime)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
