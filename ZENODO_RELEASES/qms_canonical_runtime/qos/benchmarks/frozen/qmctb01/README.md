# QMCTB-01 Frozen

Canonical target for the frozen QMCTB-01 v1.0 detector-plane causality
benchmark.

No semantic changes are allowed here after migration.

The frozen detector modes are represented in canonical measurement runtime as:

- `PRESERVE` -> `DetectorPlaneMeasurementRuntime.preserving()`
- `DESTROY` -> `DetectorPlaneMeasurementRuntime.destroying()`

The benchmark's diagnostic thresholds and QCS decisions remain outside
measurement so QMCTB-01 frozen semantics are preserved without importing
diagnostics or control into the detector-plane layer.
