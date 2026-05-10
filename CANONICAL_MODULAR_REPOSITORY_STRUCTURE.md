# Canonical Modular Repository Structure

This document defines the target package structure for QOS while preserving the
Quantum Measurement Stack causal ordering:

```text
foundation -> measurement -> acquisition -> diagnostics -> control
```

Information may flow upward only. A higher layer may consume the immutable
handoff object emitted by the layer immediately below it, but it must not reach
back into lower-layer internals.

## Target Layout

```text
qos/
  contracts/
    handoffs.py
    README.md

  foundation/
    README.md
    fields/
    imprint/
    dynamic_field_engine/
      v07_regimes/
      v08_modes/
      v09_topology/
      v10_prediction/
      v11_decision_signals/
    persistent_dynamics/

  measurement/
    README.md
    detector_plane/
    dpi/
      v01_frozen/
      v02_reconstruction/
      v03_observability/
      v04_detector_resolution/
      v05_manifold_tracking/
    detector_models/
    irreversibility/

  acquisition/
    README.md
    daq/
    sampling/
    binning/
    records/

  diagnostics/
    README.md
    visibility/
    coherence_transfer/
    confidence/
    witnesses/
    ultrasound/

  control/
    README.md
    qcs/
    policies/
    budgets/
    adaptive_orchestration/
      experimental/

  benchmarks/
    README.md
    frozen/
      qmctb01/
        spec/
        simulation/
        diagnostics/
        runner/
        artifacts_manifest/
    evolving/
      qmctb02/
      qmctb03/
      qmctb04/

  experiments/
    README.md
    imprint_field/
      phase_xxiv/
      phase_xxv/
    detector_plane_imaging/
      v011_v028_4d_reconstruction/
      v074_v115_state_space/
      v116_v132_oscillons/
      v134_v184_phase_retrieval/
      v185_v215_observability/
      v216_v249_operator_control/
      v250_v277_attractor_manifold/
      v300_v311_ultrasound/
    adaptive_systems/
    ventures/

  artifacts/
    README.md
    manifests/
    generated/
    releases/

docs/
  architecture/
  migration/
```

## Canonical Handoff Objects

Canonical handoffs are defined in `qos/contracts/handoffs.py`:

- `ImprintFieldState`: output of foundation only.
- `DetectorSignal`: output of measurement only.
- `DigitalRecord`: output of acquisition only.
- `DiagnosticReport`: output of diagnostics only.
- `ControlDecision`: output of control only.

Each handoff is immutable and must contain only the public payload needed by the
next layer. It must not retain hidden references to lower-layer runtime objects.

## Boundary Rules

Allowed imports:

```text
qos.foundation    -> qos.contracts
qos.measurement   -> qos.contracts, qos.foundation public APIs
qos.acquisition   -> qos.contracts
qos.diagnostics   -> qos.contracts
qos.control       -> qos.contracts
qos.benchmarks    -> qos.contracts and layer public APIs
qos.experiments   -> any public layer API, but no canonical APIs live here
```

Disallowed imports:

- `qos.diagnostics` importing `qos.foundation` or `qos.measurement` internals.
- `qos.control` importing raw detector, DAQ, or field modules.
- `qos.acquisition` reconstructing field state from detector output.
- Frozen benchmark modules importing experimental orchestration.
- Experimental adaptive systems modifying frozen benchmark logic.

## Frozen vs Experimental

Frozen benchmarks are immutable protocol references. Only errata and manifests
belong under `qos/benchmarks/frozen`. New algorithmic work belongs under
`qos/benchmarks/evolving` or `qos/experiments`.

Adaptive systems are control research and stay outside frozen benchmarks unless
a specific benchmark version explicitly defines them.

## Migration Mapping

| Current Location | Target Location | Notes |
| --- | --- | --- |
| `Foundations/ImprintField` | `qos/experiments/imprint_field` plus stable field types in `qos/foundation/imprint` | Preserve Phase XXIV/XXV lineage and keep generated media in artifacts. |
| `Foundations/DYNAMIC_FIELD_ENGINE/core/kappa_engine.py` | `qos/foundation/dynamic_field_engine` | Promote core kappa/signature primitives first. |
| `Foundations/DYNAMIC_FIELD_ENGINE/experiments/v7_*` | `qos/foundation/dynamic_field_engine/v07_regimes` | Regime and phase-transition lineage. |
| `Foundations/DYNAMIC_FIELD_ENGINE/experiments/v8_*` | `qos/foundation/dynamic_field_engine/v08_modes` | Mode extraction, tracking, lifecycle, interactions. |
| `Foundations/DYNAMIC_FIELD_ENGINE/experiments/v9_*` | `qos/foundation/dynamic_field_engine/v09_topology` | Topology graph lineage. |
| `Foundations/DYNAMIC_FIELD_ENGINE/experiments/v10_*` | `qos/foundation/dynamic_field_engine/v10_prediction` | Prediction, confidence, bidirectional warnings. |
| `Foundations/DYNAMIC_FIELD_ENGINE/experiments/v11_*` | `qos/foundation/dynamic_field_engine/v11_decision_signals` | Foundation-level decision signals only, not QCS control. |
| `Diagnostics/detector-plane-imaging/simulations/dpi_final_v3.py` | `qos/measurement/dpi/v01_frozen` and `qos/benchmarks/frozen/qmctb01` | Keep publication result frozen. |
| `Diagnostics/detector-plane-imaging/simulations/v11-v28` | `qos/experiments/detector_plane_imaging/v011_v028_4d_reconstruction` | 4D, holography, phase reconstruction lineage. |
| `Diagnostics/detector-plane-imaging/simulations/v74-v115` | `qos/experiments/detector_plane_imaging/v074_v115_state_space` | State-space, attractor, memory lineage. |
| `Diagnostics/detector-plane-imaging/simulations/v116-v132` | `qos/experiments/detector_plane_imaging/v116_v132_oscillons` | Soliton and oscillon lineage. |
| `Diagnostics/detector-plane-imaging/simulations/v134-v184` | `qos/experiments/detector_plane_imaging/v134_v184_phase_retrieval` | Measurement completeness, quadrature, noise work. |
| `Diagnostics/detector-plane-imaging/simulations/v185-v215` | `qos/experiments/detector_plane_imaging/v185_v215_observability` | Detector resolution, scaling, observability, tomography. |
| `Diagnostics/detector-plane-imaging/simulations/v216-v249` | `qos/experiments/detector_plane_imaging/v216_v249_operator_control` | Operator/control experiments; stable policies move to `qos/control`. |
| `Diagnostics/detector-plane-imaging/simulations/v250-v277` | `qos/experiments/detector_plane_imaging/v250_v277_attractor_manifold` | Attractor, flux, energy, constraint, OCT manifold tracking. |
| `Diagnostics/detector-plane-imaging/simulations/ultrasound/v300-v311` | `qos/experiments/detector_plane_imaging/v300_v311_ultrasound` | Ultrasound diagnostics and adaptive decisions. |
| `Benchmarks/quantum-measurement-stack` | `qos/benchmarks/frozen/qmctb01` plus layer docs | Keep v1.0 immutable. |
| `Benchmarks/quantum-measurement-stack-demo/run_qmctb02_v3.py` | `qos/benchmarks/evolving/qmctb02` | Coherence transfer function. |
| `Benchmarks/quantum-measurement-stack-demo/qmctb03_v*.py` | `qos/benchmarks/evolving/qmctb03` | Preserve version lineage before freezing a canonical revision. |
| `Releases`, `Renders`, `Visualizations`, `Diagnostics/*/results*` | `qos/artifacts` or external artifact storage | Runtime outputs must not be imported as source. |
| `Archive` | `qos/artifacts/releases/archive` or read-only archival root | Historical custody only. |
| `Ventures` | `qos/experiments/ventures` | Product/application explorations. |

## Canonical Runtime Flow

```text
ImprintFieldState
  -> DetectorSignal
  -> DigitalRecord
  -> DiagnosticReport
  -> ControlDecision
```

Control decisions are forward-only. They may schedule, retry, abort, recalibrate,
or change future run parameters, but they must not alter past measurements,
diagnostics, or records.

