# QOS Migration Plan

This plan migrates the current research workspace into the canonical `qos/`
package without flattening frozen benchmarks, adaptive orchestration, detector
systems, diagnostics, and runtime artifacts into one layer.

## Phase 0: Custody Lock

Do not move or edit frozen benchmark sources in place.

Preserve these as read-only source references:

- `Benchmarks/quantum-measurement-stack/DEFINITION.md`
- `Benchmarks/quantum-measurement-stack/QMCTB-01_v1.0_Freeze_and_Custody.md`
- `Benchmarks/quantum-measurement-stack/qmctb/QMCTB-01.md`
- `Archive/quantum-measurement-stack-main`
- DOI/release material under `Releases/`

Target:

```text
qos/benchmarks/frozen/qmctb01/
```

Only copy exact frozen protocol code, methods, and manifests. No semantic edits.

## Phase 1: Promote Contracts

Use `qos/contracts/handoffs.py` as the canonical boundary API:

```text
ImprintFieldState
DetectorSignal
DigitalRecord
DiagnosticReport
ControlDecision
```

Every migrated module should consume and emit one of these objects at layer
boundaries.

## Phase 2: Foundation Migration

Current:

```text
Foundations/ImprintField
Foundations/DYNAMIC_FIELD_ENGINE
Simulations/phase_xxv_simulation.py
```

Target:

```text
qos/foundation/imprint/
qos/foundation/dynamic_field_engine/
qos/foundation/persistent_dynamics/
qos/experiments/imprint_field/
```

Promote only stable, reusable field primitives into `qos.foundation`. Keep
phase-specific notebooks, generated arrays, videos, and exploratory scripts in
`qos.experiments` or `qos.artifacts`.

## Phase 3: Measurement Migration

Current:

```text
Diagnostics/detector-plane-imaging/simulations/dpi_final_v3.py
Diagnostics/detector-plane-imaging/simulations/v*.py
```

Target:

```text
qos/measurement/detector_plane/
qos/measurement/dpi/v01_frozen/
qos/measurement/detector_models/
qos/measurement/irreversibility/
qos/experiments/detector_plane_imaging/
```

Only detector coupling, detector phase preservation/loss, and detector-formed
signals belong in `qos.measurement`. Pixel binning, visibility, confidence, and
control policies must be extracted into their own layers.

## Phase 4: Acquisition Migration

Current acquisition-like logic is embedded inside DPI and QMCTB scripts:

- pixel binning
- shot/read noise
- sampling windows
- frame accumulation
- record generation

Target:

```text
qos/acquisition/daq/
qos/acquisition/sampling/
qos/acquisition/binning/
qos/acquisition/records/
```

DAQ code consumes `DetectorSignal` and emits `DigitalRecord`.

## Phase 5: Diagnostics Migration

Current:

```text
Benchmarks/quantum-measurement-stack/qmctb/diagnostics/
Diagnostics/detector-plane-imaging/simulations/*visibility*
Diagnostics/detector-plane-imaging/simulations/ultrasound/v309*
Diagnostics/detector-plane-imaging/simulations/ultrasound/v310*
```

Target:

```text
qos/diagnostics/visibility/
qos/diagnostics/coherence_transfer/
qos/diagnostics/confidence/
qos/diagnostics/witnesses/
qos/diagnostics/ultrasound/
```

Diagnostics consumes `DigitalRecord` and emits `DiagnosticReport`. It does not
issue decisions that affect future experiments; those move to `qos.control`.

## Phase 6: Control Migration

Current:

```text
Benchmarks/quantum-measurement-stack/qmctb/qcs/
Diagnostics/detector-plane-imaging/simulations/v229*
Diagnostics/detector-plane-imaging/simulations/v237*
Diagnostics/detector-plane-imaging/simulations/v240*
Diagnostics/detector-plane-imaging/simulations/v243*
Diagnostics/detector-plane-imaging/simulations/v257*
```

Target:

```text
qos/control/qcs/
qos/control/policies/
qos/control/budgets/
qos/control/adaptive_orchestration/
qos/experiments/adaptive_systems/
```

Control consumes `DiagnosticReport` and emits `ControlDecision`. It cannot
change previous data, diagnostics, or benchmark interpretation.

## Phase 7: Benchmark Separation

Target:

```text
qos/benchmarks/frozen/qmctb01/
qos/benchmarks/evolving/qmctb02/
qos/benchmarks/evolving/qmctb03/
qos/benchmarks/evolving/qmctb04/
```

Rules:

- QMCTB-01 remains frozen.
- QMCTB-02, QMCTB-03, and QMCTB-04 preserve version lineage until explicitly
  frozen.
- Benchmark runners may orchestrate layers, but benchmark layer logic remains
  in layer packages.
- Adaptive orchestration must not be folded into benchmark definitions unless a
  future benchmark explicitly freezes that behavior.

## Phase 8: Artifact Isolation

Current:

```text
Releases/
Renders/
Visualizations/
Diagnostics/**/results*/
Foundations/**/outputs*/
*.png, *.mp4, *.gif, *.npy, *.pkl, *.docx, *.pdf
```

Target:

```text
qos/artifacts/generated/
qos/artifacts/manifests/
qos/artifacts/releases/
```

Artifacts are never imported by source modules. Source code may write artifacts
through manifest utilities, but generated outputs remain outside canonical APIs.

## Migration Order

1. Copy frozen QMCTB-01 into `qos/benchmarks/frozen/qmctb01` as a read-only
   reference.
2. Promote `qos.contracts` everywhere new code crosses a layer boundary.
3. Extract pure foundation primitives.
4. Extract detector-plane-only measurement primitives.
5. Extract DAQ/binning/record primitives.
6. Extract diagnostics.
7. Extract future-only QCS control.
8. Move remaining versioned scripts into `qos/experiments` lineage buckets.
9. Move generated outputs into artifact manifests.

