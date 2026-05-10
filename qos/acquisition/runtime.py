"""Canonical acquisition runtime APIs.

The acquisition layer consumes only ``DetectorSignal`` and emits immutable
``DigitalRecord`` handoffs. It models detector bandwidth, coarse graining,
pixel binning, observability scaling, and spatial measurement decoherence as
irreversible record formation effects.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Optional, Tuple

from qos.contracts import DetectorSignal, DigitalRecord


ACQUISITION_API_VERSION = "qos.acquisition.runtime.v1"
QMCTB03_VISIBILITY_THRESHOLD = 0.75


def _positive_int(value: int, name: str) -> int:
    if int(value) < 1:
        raise ValueError(f"{name} must be >= 1.")
    return int(value)


def _positive_float(value: float, name: str) -> float:
    if float(value) <= 0.0:
        raise ValueError(f"{name} must be > 0.")
    return float(value)


@dataclass(frozen=True)
class PixelBinning:
    """Geometry-neutral binning over detector sample axes."""

    factor: int = 1
    mode: str = "mean"

    def __post_init__(self) -> None:
        _positive_int(self.factor, "PixelBinning.factor")

    def apply_shape(self, shape: Tuple[int, ...]) -> Tuple[int, ...]:
        return _coarsen_detector_axes(shape, self.factor)

    def descriptor(self) -> Mapping[str, Any]:
        return {
            "factor": self.factor,
            "mode": self.mode,
            "irreversible": self.factor > 1,
            "semantics": "pixel groups are aggregated before the DigitalRecord handoff",
        }


@dataclass(frozen=True)
class CoarseGraining:
    """Irreversible detector-plane coarse graining."""

    factor: int = 1
    operator: str = "support-average"

    def __post_init__(self) -> None:
        _positive_int(self.factor, "CoarseGraining.factor")

    def apply_shape(self, shape: Tuple[int, ...]) -> Tuple[int, ...]:
        return _coarsen_detector_axes(shape, self.factor)

    def descriptor(self) -> Mapping[str, Any]:
        return {
            "factor": self.factor,
            "operator": self.operator,
            "irreversible": self.factor > 1,
            "semantics": "sub-cell detector structure is not recoverable downstream",
        }


@dataclass(frozen=True)
class DetectorBandwidthLimit:
    """Classical bandwidth limit applied during digitization."""

    bandwidth_hz: Optional[float] = None
    nominal_signal_bandwidth_hz: Optional[float] = None
    rolloff: str = "hard-nyquist"

    def __post_init__(self) -> None:
        if self.bandwidth_hz is not None:
            _positive_float(self.bandwidth_hz, "DetectorBandwidthLimit.bandwidth_hz")
        if self.nominal_signal_bandwidth_hz is not None:
            _positive_float(
                self.nominal_signal_bandwidth_hz,
                "DetectorBandwidthLimit.nominal_signal_bandwidth_hz",
            )

    def effective_bandwidth_hz(
        self, sampling_rate_hz: float, signal: DetectorSignal
    ) -> float:
        candidates = [sampling_rate_hz / 2.0]
        if self.bandwidth_hz is not None:
            candidates.append(self.bandwidth_hz)
        topology_bandwidth = (
            signal.metadata.get("policy", {})
            .get("topology", {})
            .get("bandwidth_hz")
            if isinstance(signal.metadata.get("policy", {}), Mapping)
            else None
        )
        if topology_bandwidth is not None:
            candidates.append(float(topology_bandwidth))
        return min(candidates)

    def bandwidth_ratio(self, sampling_rate_hz: float, signal: DetectorSignal) -> float:
        nominal = self.nominal_signal_bandwidth_hz or sampling_rate_hz / 2.0
        return min(1.0, self.effective_bandwidth_hz(sampling_rate_hz, signal) / nominal)

    def descriptor(self, sampling_rate_hz: float, signal: DetectorSignal) -> Mapping[str, Any]:
        return {
            "bandwidth_hz": self.bandwidth_hz,
            "nominal_signal_bandwidth_hz": self.nominal_signal_bandwidth_hz,
            "effective_bandwidth_hz": self.effective_bandwidth_hz(sampling_rate_hz, signal),
            "bandwidth_ratio": self.bandwidth_ratio(sampling_rate_hz, signal),
            "rolloff": self.rolloff,
            "future_adaptive_bandwidth": "policy hook may replace this static limit",
        }


@dataclass(frozen=True)
class SpatialMeasurementDecoherence:
    """Acquisition-time spatial measurement decoherence descriptor."""

    sigma_radians: float = 0.0
    correlation_length_pixels: Optional[float] = None
    model: str = "gaussian-phase-diffusion"

    def __post_init__(self) -> None:
        if self.sigma_radians < 0.0:
            raise ValueError("SpatialMeasurementDecoherence.sigma_radians must be >= 0.")
        if self.correlation_length_pixels is not None:
            _positive_float(
                self.correlation_length_pixels,
                "SpatialMeasurementDecoherence.correlation_length_pixels",
            )

    @property
    def contrast_factor(self) -> float:
        return math.exp(-(self.sigma_radians**2))

    def descriptor(self) -> Mapping[str, Any]:
        return {
            "sigma_radians": self.sigma_radians,
            "correlation_length_pixels": self.correlation_length_pixels,
            "model": self.model,
            "contrast_factor": self.contrast_factor,
            "irreversible": self.sigma_radians > 0.0,
            "semantics": "spatial contrast lost during measurement storage is not reconstructed",
        }


@dataclass(frozen=True)
class ObservabilityScaling:
    """Geometry-neutral DPI/QMCTB-03 observability scaling semantics."""

    visibility_threshold: float = QMCTB03_VISIBILITY_THRESHOLD
    reference: str = "QMCTB-03-v6.6"
    dpi_axes: Tuple[str, str] = ("detector-u", "detector-v")

    def __post_init__(self) -> None:
        if not 0.0 < self.visibility_threshold <= 1.0:
            raise ValueError("ObservabilityScaling.visibility_threshold must be in (0, 1].")

    def estimate(
        self,
        *,
        source_shape: Tuple[int, ...],
        record_shape: Tuple[int, ...],
        binning_factor: int,
        coarse_graining_factor: int,
        bandwidth_ratio: float,
        decoherence_factor: float,
    ) -> Mapping[str, Any]:
        source_samples = _detector_sample_count(source_shape)
        record_samples = _detector_sample_count(record_shape)
        sampling_ratio = record_samples / source_samples if source_samples else 0.0
        scale = max(0.0, min(1.0, sampling_ratio * bandwidth_ratio * decoherence_factor))
        return {
            "reference": self.reference,
            "compatible_with_qmctb03": True,
            "visibility_threshold": self.visibility_threshold,
            "dpi_axes": self.dpi_axes,
            "geometry_neutral": True,
            "source_detector_samples": source_samples,
            "record_detector_samples": record_samples,
            "sampling_ratio": sampling_ratio,
            "bandwidth_ratio": bandwidth_ratio,
            "spatial_decoherence_factor": decoherence_factor,
            "observability_index": scale,
            "observability_degraded": scale < self.visibility_threshold,
            "effective_bin_scale": binning_factor * coarse_graining_factor,
            "scaling_semantics": (
                "observable DPI support decreases monotonically with pixel binning, "
                "coarse graining, detector bandwidth limits, and spatial decoherence"
            ),
        }


@dataclass(frozen=True)
class AcquisitionPolicy:
    """Reusable acquisition policy promoted from QMCTB-03 scaling scripts."""

    policy_id: str = "canonical-dpi-acquisition"
    sampling_rate_hz: float = 1.0
    bit_depth: int = 16
    pixel_binning: PixelBinning = field(default_factory=PixelBinning)
    coarse_graining: CoarseGraining = field(default_factory=CoarseGraining)
    bandwidth_limit: DetectorBandwidthLimit = field(default_factory=DetectorBandwidthLimit)
    spatial_decoherence: SpatialMeasurementDecoherence = field(
        default_factory=SpatialMeasurementDecoherence
    )
    observability: ObservabilityScaling = field(default_factory=ObservabilityScaling)
    storage_backend: str = "canonical-digital-record"
    adaptive_bandwidth_hook: Optional[str] = None
    detector_array_topology: str = "single-plane"
    streaming_window_samples: Optional[int] = None

    def __post_init__(self) -> None:
        _positive_float(self.sampling_rate_hz, "AcquisitionPolicy.sampling_rate_hz")
        _positive_int(self.bit_depth, "AcquisitionPolicy.bit_depth")
        if self.streaming_window_samples is not None:
            _positive_int(
                self.streaming_window_samples,
                "AcquisitionPolicy.streaming_window_samples",
            )

    def record_shape(self, signal: DetectorSignal) -> Tuple[int, ...]:
        shape = self.pixel_binning.apply_shape(signal.shape)
        return self.coarse_graining.apply_shape(shape)

    def transforms(self) -> Tuple[str, ...]:
        items = ["sample", "quantize"]
        if self.bandwidth_limit.bandwidth_hz is not None:
            items.append("bandwidth-limit")
        if self.pixel_binning.factor > 1:
            items.append("pixel-bin")
        if self.coarse_graining.factor > 1:
            items.append("coarse-grain")
        if self.spatial_decoherence.sigma_radians > 0.0:
            items.append("spatial-measurement-decoherence")
        items.append("record")
        return tuple(items)

    def descriptor(self, signal: DetectorSignal) -> Mapping[str, Any]:
        record_shape = self.record_shape(signal)
        bandwidth = self.bandwidth_limit.descriptor(self.sampling_rate_hz, signal)
        observability = self.observability.estimate(
            source_shape=signal.shape,
            record_shape=record_shape,
            binning_factor=self.pixel_binning.factor,
            coarse_graining_factor=self.coarse_graining.factor,
            bandwidth_ratio=float(bandwidth["bandwidth_ratio"]),
            decoherence_factor=self.spatial_decoherence.contrast_factor,
        )
        return {
            "policy_id": self.policy_id,
            "sampling_rate_hz": self.sampling_rate_hz,
            "bit_depth": self.bit_depth,
            "pixel_binning": self.pixel_binning.descriptor(),
            "coarse_graining": self.coarse_graining.descriptor(),
            "bandwidth_limit": bandwidth,
            "spatial_decoherence": self.spatial_decoherence.descriptor(),
            "observability_scaling": observability,
            "storage_backend": self.storage_backend,
            "detector_array_topology": self.detector_array_topology,
            "adaptive_bandwidth_hook": self.adaptive_bandwidth_hook,
            "streaming_window_samples": self.streaming_window_samples,
            "future_extensibility": (
                "adaptive detector bandwidth",
                "distributed detector arrays",
                "streaming acquisition systems",
            ),
        }


@dataclass(frozen=True)
class CanonicalAcquisitionRuntime:
    """Acquire DetectorSignal objects into canonical DigitalRecord objects."""

    policy: AcquisitionPolicy = field(default_factory=AcquisitionPolicy)

    @classmethod
    def high_bandwidth(cls) -> "CanonicalAcquisitionRuntime":
        return cls(
            AcquisitionPolicy(
                policy_id="high-bandwidth-dpi-acquisition",
                sampling_rate_hz=200_000.0,
                bit_depth=16,
                bandwidth_limit=DetectorBandwidthLimit(
                    bandwidth_hz=90_000.0,
                    nominal_signal_bandwidth_hz=80_000.0,
                ),
            )
        )

    @classmethod
    def low_bandwidth(cls) -> "CanonicalAcquisitionRuntime":
        return cls(
            AcquisitionPolicy(
                policy_id="low-bandwidth-dpi-acquisition",
                sampling_rate_hz=20_000.0,
                bit_depth=12,
                pixel_binning=PixelBinning(factor=2),
                coarse_graining=CoarseGraining(factor=2),
                bandwidth_limit=DetectorBandwidthLimit(
                    bandwidth_hz=2_000.0,
                    nominal_signal_bandwidth_hz=10_000.0,
                ),
            )
        )

    @classmethod
    def degraded_observability(cls) -> "CanonicalAcquisitionRuntime":
        return cls(
            AcquisitionPolicy(
                policy_id="degraded-observability-dpi-acquisition",
                sampling_rate_hz=30_000.0,
                bit_depth=10,
                pixel_binning=PixelBinning(factor=4),
                coarse_graining=CoarseGraining(factor=2),
                bandwidth_limit=DetectorBandwidthLimit(
                    bandwidth_hz=3_000.0,
                    nominal_signal_bandwidth_hz=15_000.0,
                ),
                spatial_decoherence=SpatialMeasurementDecoherence(
                    sigma_radians=0.8,
                    correlation_length_pixels=3.0,
                ),
            )
        )

    def acquire(
        self, signal: DetectorSignal, provenance: Mapping[str, Any]
    ) -> DigitalRecord:
        if not isinstance(signal, DetectorSignal):
            raise TypeError("Canonical acquisition may consume DetectorSignal only.")
        if not signal.irreversible_loss:
            raise ValueError("Acquisition requires an irreversible DetectorSignal.")

        record_shape = self.policy.record_shape(signal)
        policy_metadata = self.policy.descriptor(signal)
        acquisition_id = _stable_record_id(signal, self.policy)
        return DigitalRecord(
            record_id=acquisition_id,
            source_signal_id=signal.signal_id,
            sampling_rate_hz=self.policy.sampling_rate_hz,
            bit_depth=self.policy.bit_depth,
            shape=record_shape,
            transforms=self.policy.transforms(),
            metadata={
                "provenance": dict(provenance),
                "runtime": ACQUISITION_API_VERSION,
                "causal_order": "DetectorSignal -> DigitalRecord",
                "input_contract": "DetectorSignal",
                "output_contract": "DigitalRecord",
                "source_detector_model": signal.detector_model,
                "source_signal_shape": signal.shape,
                "preserved_correlation_count": len(signal.preserved_correlations),
                "destroyed_upstream_correlation_count": len(signal.destroyed_correlations),
                "irreversible_loss_inherited": signal.irreversible_loss,
                "irreversible_acquisition": True,
                "policy": policy_metadata,
                "qmctb03_scaling_semantics": policy_metadata["observability_scaling"],
                "runtime_provenance": {
                    "api_version": ACQUISITION_API_VERSION,
                    "policy_digest": _policy_digest(self.policy),
                    "record_digest_input": {
                        "signal_id": signal.signal_id,
                        "policy_id": self.policy.policy_id,
                    },
                },
            },
        )


def acquire_detector_signal(
    signal: DetectorSignal,
    *,
    policy: Optional[AcquisitionPolicy] = None,
    provenance: Optional[Mapping[str, Any]] = None,
) -> DigitalRecord:
    """Reusable functional API for canonical acquisition."""
    return CanonicalAcquisitionRuntime(policy or AcquisitionPolicy()).acquire(
        signal,
        dict(provenance or {}),
    )


def _coarsen_detector_axes(shape: Tuple[int, ...], factor: int) -> Tuple[int, ...]:
    factor = _positive_int(factor, "factor")
    if factor == 1 or len(shape) == 0:
        return tuple(int(item) for item in shape)
    if len(shape) == 1:
        return (max(1, int(shape[0]) // factor),)
    prefix = tuple(int(item) for item in shape[:-2])
    detector_axes = tuple(max(1, int(item) // factor) for item in shape[-2:])
    return prefix + detector_axes


def _detector_sample_count(shape: Tuple[int, ...]) -> int:
    if not shape:
        return 0
    axes = shape[-2:] if len(shape) >= 2 else shape
    total = 1
    for item in axes:
        total *= max(0, int(item))
    return total


def _stable_record_id(signal: DetectorSignal, policy: AcquisitionPolicy) -> str:
    payload = f"{signal.signal_id}:{policy.policy_id}:{_policy_digest(policy)}"
    return "dr-" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _policy_digest(policy: AcquisitionPolicy) -> str:
    payload = repr(asdict(policy)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()

