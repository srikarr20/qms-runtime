"""Canonical detector-plane measurement runtime.

This package owns the irreversible transition from ``ImprintFieldState`` to
``DetectorSignal``. It has no dependency on diagnostics, acquisition, or
control layers.
"""

from .runtime import (
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
