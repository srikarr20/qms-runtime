# CURRENT RUNTIME STATUS

## Canonical QMS Runtime
STATUS: OPERATIONAL

## Verified Runtime Layers
- Foundation Runtime
- Detector Plane Runtime
- Acquisition Runtime
- Diagnostics Runtime
- QCS Stub Runtime

## Canonical Handoff Chain
ImprintFieldState
→ DetectorSignal
→ DigitalRecord
→ DiagnosticReport
→ ControlDecision

## Verified Commands

### Runtime
python3 -m qos.runtime.orchestrator

### Boundary Enforcement
python3 tools/check_qms_import_boundaries.py

### Compile Validation
PYTHONPYCACHEPREFIX=/private/tmp/qos_pycache python3 -m compileall qos

## Frozen Compatibility Targets
- QMCTB-01
- QMCTB-02
- QMCTB-03
- v257 adaptive orchestration systems

## Current Runtime Characteristics
- Detector-plane irreversibility enforced
- No upstream reconstruction
- Geometry-neutral DPI semantics
- Acquisition-limited observability
- Runtime provenance attached to all handoffs

## Remaining Major Work
- Full adaptive QCS promotion
- v257 runtime integration
- Controlled decoherence orchestration
- Adaptive detector policy runtime
- Distributed detector topology runtime

## Architecture State
Governed executable coherence-engineering runtime operational.

## Runtime Digest

Orchestrator SHA256:
681a35144aa612044de3c1fce7ad3ce3ae4672f2278abf5b349e4c81110c7b2a

Runtime Output SHA256:
6d21ccb8c1945478f0bf600aac3859425dcfbf66af945562982384209ba4355c

## Archive Digest

qos_runtime_stage_alpha.tar.gz SHA256:
a434a5650371d782bf70a1311e245f85cdcce28c57178f86cdc03f13f02e535c  ARCHIVE/runtime_snapshots/qos_runtime_stage_alpha.tar.gz

## Stage Beta Archive Digest

qos_runtime_stage_beta.tar.gz SHA256:
78c6586c637bd74bddf35d33a475448c4ec5d7e3c53f8abfb1b7038e49f65448  ARCHIVE/runtime_snapshots/qos_runtime_stage_beta.tar.gz
