# QMS Boundary Rules

Canonical causal ordering:

```text
foundation -> measurement -> acquisition -> diagnostics -> control
```

## Layer Contracts

| Layer | Input | Output | Owns | Must Not Own |
| --- | --- | --- | --- | --- |
| `qos.foundation` | physical/simulated field parameters | `ImprintFieldState` | imprint dynamics, kappa, modes, persistence | detector response, DAQ, diagnostics, control |
| `qos.measurement` | `ImprintFieldState` | `DetectorSignal` | detector-plane coupling and irreversible correlation loss | sampling, binning, inference, control |
| `qos.acquisition` | `DetectorSignal` | `DigitalRecord` | DAQ, sampling, digitization, thresholding, binning, records | field reconstruction, detector physics, diagnostics, control |
| `qos.diagnostics` | `DigitalRecord` | `DiagnosticReport` | metrics, uncertainty, confidence, witnesses | detector access, DAQ mutation, control |
| `qos.control` | `DiagnosticReport` | `ControlDecision` | future-run policy, budgets, retry, abort, recalibration | changing past records, post-selection, metric calculation |

## Non-Negotiable Semantics

- Detector-plane loss is local, physical, and irreversible.
- DAQ loss is also irreversible and must be recorded as acquisition limitation.
- Diagnostics can only claim what survived measurement and acquisition.
- Control can act only on future runs.
- Frozen benchmarks must not import experimental orchestration.
- Adaptive orchestration must remain outside frozen benchmark definitions.

## Import Direction

Allowed layer composition:

```text
contracts
foundation -> contracts
measurement -> contracts, foundation
acquisition -> contracts
diagnostics -> contracts
control -> contracts
benchmarks -> contracts, public layer APIs
experiments -> public layer APIs
```

The canonical runtime handoff chain is:

```text
ImprintFieldState -> DetectorSignal -> DigitalRecord -> DiagnosticReport -> ControlDecision
```

