# Detector Plane

Canonical home for detector-plane semantics.

This package owns the causal transition from physically present imprint
information to detector-formed signal information. It is where detector
architecture may preserve, transform, or irreversibly destroy correlations.

Input: `ImprintFieldState`.

Output: `DetectorSignal`.

This package must not perform DAQ sampling, statistical diagnostics, or QCS
control. Detector-plane loss is represented on `DetectorSignal` and cannot be
recovered by higher layers.

Canonical APIs:

- `DetectorPlaneMeasurementRuntime.preserving()` maps
  `ImprintFieldState -> DetectorSignal` with QMCTB-01 `PRESERVE` semantics.
- `DetectorPlaneMeasurementRuntime.destroying()` maps
  `ImprintFieldState -> DetectorSignal` with QMCTB-01 `DESTROY` semantics.
- `DetectorArrayTopology` describes detector planes without assuming
  double-slit geometry, leaving room for distributed arrays and
  bandwidth-conditioned observability.

Executable examples:

- `python -m qos.examples.detector_plane_preserving`
- `python -m qos.examples.detector_plane_destroying`
