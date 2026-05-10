"""Acquisition layer: DAQ, sampling, thresholding, binning, and records."""

from .runtime import (
    AcquisitionPolicy,
    CanonicalAcquisitionRuntime,
    CoarseGraining,
    DetectorBandwidthLimit,
    ObservabilityScaling,
    PixelBinning,
    SpatialMeasurementDecoherence,
    acquire_detector_signal,
)

__all__ = [
    "AcquisitionPolicy",
    "CanonicalAcquisitionRuntime",
    "CoarseGraining",
    "DetectorBandwidthLimit",
    "ObservabilityScaling",
    "PixelBinning",
    "SpatialMeasurementDecoherence",
    "acquire_detector_signal",
]
