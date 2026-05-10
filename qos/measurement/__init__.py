"""Measurement layer: detector-plane coupling and irreversible signal formation."""

from .detector_plane import (
    CORRELATION_DESTROYING_TRANSFORM,
    CORRELATION_PRESERVING_TRANSFORM,
    DetectorArrayTopology,
    DetectorPlaneMeasurementRuntime,
    DetectorPlanePolicy,
    DetectorPlaneTransform,
    DetectorTransformKind,
    destroy_correlations,
    detector_signal_from_imprint_state,
    preserve_correlations,
)

__all__ = (
    "CORRELATION_DESTROYING_TRANSFORM",
    "CORRELATION_PRESERVING_TRANSFORM",
    "DetectorArrayTopology",
    "DetectorPlaneMeasurementRuntime",
    "DetectorPlanePolicy",
    "DetectorPlaneTransform",
    "DetectorTransformKind",
    "destroy_correlations",
    "detector_signal_from_imprint_state",
    "preserve_correlations",
)
