"""Reusable detector-plane APIs for canonical measurement formation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Optional, Tuple

from qos.contracts import DetectorSignal, ImprintFieldState


class DetectorTransformKind(str, Enum):
    """Canonical detector-plane transform semantics."""

    CORRELATION_PRESERVING = "correlation-preserving"
    CORRELATION_DESTROYING = "correlation-destroying"


@dataclass(frozen=True)
class DetectorPlaneTransform:
    """Named irreversible detector-plane correlation selection transform."""

    name: str
    kind: DetectorTransformKind
    preserved_correlations: Tuple[str, ...]
    destroyed_correlations: Tuple[str, ...]
    operator: str
    qmctb01_mode: str
    dpi_semantics: Tuple[str, ...] = ()

    @property
    def irreversible_loss(self) -> bool:
        """Detector-plane handoffs are irreversible even when nothing is destroyed."""
        return True

    def metadata(self) -> Mapping[str, Any]:
        """Return JSON-safe transform metadata for DetectorSignal provenance."""
        return {
            "name": self.name,
            "kind": self.kind.value,
            "operator": self.operator,
            "qmctb01_mode": self.qmctb01_mode,
            "dpi_semantics": self.dpi_semantics,
            "irreversibility": (
                "DetectorSignal is a post-detector handoff; destroyed "
                "correlations cannot be reconstructed by downstream layers."
            ),
        }


@dataclass(frozen=True)
class DetectorArrayTopology:
    """Geometry-neutral detector-plane topology descriptor.

    The descriptor can represent a single plane, a tiled array, or a future
    distributed detector array without assuming double-slit geometry.
    """

    topology_id: str = "single-plane"
    plane_axes: Tuple[str, ...] = ("detector-u", "detector-v")
    elements: Optional[int] = None
    distributed: bool = False
    bandwidth_hz: Optional[float] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def descriptor(self) -> Mapping[str, Any]:
        return {
            "topology_id": self.topology_id,
            "plane_axes": self.plane_axes,
            "elements": self.elements,
            "distributed": self.distributed,
            "bandwidth_hz": self.bandwidth_hz,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class DetectorPlanePolicy:
    """Extensible detector policy selected before measurement occurs."""

    policy_id: str = "static-detector-plane-policy"
    transform: DetectorPlaneTransform = field(
        default_factory=lambda: CORRELATION_PRESERVING_TRANSFORM
    )
    topology: DetectorArrayTopology = field(default_factory=DetectorArrayTopology)
    adaptive_policy_hook: Optional[str] = None
    bandwidth_conditioning: Optional[Mapping[str, Any]] = None

    def descriptor(self) -> Mapping[str, Any]:
        return {
            "policy_id": self.policy_id,
            "transform": self.transform.metadata(),
            "topology": self.topology.descriptor(),
            "adaptive_policy_hook": self.adaptive_policy_hook,
            "bandwidth_conditioning": dict(self.bandwidth_conditioning or {}),
            "future_extensibility": (
                "adaptive detector policies",
                "distributed detector arrays",
                "bandwidth-conditioned observability",
            ),
        }


CORRELATION_PRESERVING_TRANSFORM = DetectorPlaneTransform(
    name="detector-plane:preserve-correlations",
    kind=DetectorTransformKind.CORRELATION_PRESERVING,
    preserved_correlations=(
        "detector_intensity",
        "relative_phase",
        "spatial_coherence",
        "coherence_transfer",
    ),
    destroyed_correlations=(),
    operator="identity-coherence-transfer",
    qmctb01_mode="PRESERVE",
    dpi_semantics=(
        "complex detector-plane field remains mutually coherent",
        "ensemble accumulation preserves interference-bearing correlations",
    ),
)

CORRELATION_DESTROYING_TRANSFORM = DetectorPlaneTransform(
    name="detector-plane:destroy-correlations",
    kind=DetectorTransformKind.CORRELATION_DESTROYING,
    preserved_correlations=("detector_intensity", "coarse_detector_support"),
    destroyed_correlations=(
        "relative_phase",
        "spatial_coherence",
        "coherence_transfer",
        "sub-threshold_modes",
    ),
    operator="phase-scramble-coarse-grain",
    qmctb01_mode="DESTROY",
    dpi_semantics=(
        "per-frame detector-plane phase relation is randomized before accumulation",
        "coherence-bearing correlations are absent from the emitted DetectorSignal",
    ),
)


def preserve_correlations() -> DetectorPlaneTransform:
    """Return the canonical QMCTB-01/DPI coherence-preserving transform."""
    return CORRELATION_PRESERVING_TRANSFORM


def destroy_correlations() -> DetectorPlaneTransform:
    """Return the canonical QMCTB-01/DPI coherence-destroying transform."""
    return CORRELATION_DESTROYING_TRANSFORM


@dataclass(frozen=True)
class DetectorPlaneMeasurementRuntime:
    """Generate canonical DetectorSignal objects from ImprintFieldState."""

    detector_model: str = "canonical-detector-plane"
    policy: DetectorPlanePolicy = field(default_factory=DetectorPlanePolicy)
    detector_plane_version: str = "v1"

    @classmethod
    def preserving(
        cls,
        *,
        detector_model: str = "canonical-detector-plane",
        topology: Optional[DetectorArrayTopology] = None,
    ) -> "DetectorPlaneMeasurementRuntime":
        """Build a runtime using the canonical preserving transform."""
        return cls(
            detector_model=detector_model,
            policy=DetectorPlanePolicy(
                policy_id="static-preserve",
                transform=preserve_correlations(),
                topology=topology or DetectorArrayTopology(),
            ),
        )

    @classmethod
    def destroying(
        cls,
        *,
        detector_model: str = "canonical-detector-plane",
        topology: Optional[DetectorArrayTopology] = None,
    ) -> "DetectorPlaneMeasurementRuntime":
        """Build a runtime using the canonical destroying transform."""
        return cls(
            detector_model=detector_model,
            policy=DetectorPlanePolicy(
                policy_id="static-destroy",
                transform=destroy_correlations(),
                topology=topology or DetectorArrayTopology(),
            ),
        )

    def measure(
        self, state: ImprintFieldState, provenance: Mapping[str, Any]
    ) -> DetectorSignal:
        return detector_signal_from_imprint_state(
            state,
            detector_model=self.detector_model,
            policy=self.policy,
            detector_plane_version=self.detector_plane_version,
            provenance=provenance,
        )


def detector_signal_from_imprint_state(
    state: ImprintFieldState,
    *,
    detector_model: str = "canonical-detector-plane",
    policy: Optional[DetectorPlanePolicy] = None,
    detector_plane_version: str = "v1",
    provenance: Optional[Mapping[str, Any]] = None,
) -> DetectorSignal:
    """Apply detector-plane semantics to an ImprintFieldState.

    This function intentionally consumes only the immutable foundation handoff.
    Foundation may feed measurement, but measurement never imports diagnostics
    or control and never reaches back into mutable field runtimes.
    """
    selected_policy = policy or DetectorPlanePolicy()
    transform = selected_policy.transform
    detector_signal_id = (
        f"ds-{state.state_id}-{transform.kind.value.replace('-', '_')}"
    )
    return DetectorSignal(
        signal_id=detector_signal_id,
        source_state_id=state.state_id,
        detector_model=detector_model,
        shape=state.shape,
        preserved_correlations=transform.preserved_correlations,
        destroyed_correlations=transform.destroyed_correlations,
        irreversible_loss=transform.irreversible_loss,
        metadata={
            "provenance": dict(provenance or {}),
            "runtime": "qos.measurement.detector_plane.DetectorPlaneMeasurementRuntime",
            "detector_plane_version": detector_plane_version,
            "source_lineage": state.lineage,
            "source_coordinates": dict(state.coordinates),
            "policy": selected_policy.descriptor(),
            "transform": transform.metadata(),
            "causal_order": "ImprintFieldState -> DetectorSignal",
            "imports_boundary": "measurement depends only on qos.contracts",
        },
    )
