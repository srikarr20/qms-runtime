# Diagnostics Layer

Owns metric extraction, statistical validation, confidence estimation, and
constraint-aware interpretation of acquired records.

Input: `DigitalRecord`.

Output: `DiagnosticReport`.

Diagnostics must not configure experiments or issue control actions.

## Canonical Runtime

`qos.diagnostics.CanonicalDiagnosticsRuntime` promotes QMCTB diagnostics into a
reusable runtime API. It consumes only `DigitalRecord` and emits immutable
`DiagnosticReport` objects with runtime provenance metadata.

Promoted diagnostic families:

- visibility metrics compatible with QMCTB-01
- coherence transfer functions compatible with QMCTB-02
- geometry-neutral observability metrics compatible with QMCTB-03
- spatial decoherence diagnostics
- detector fidelity metrics

The runtime preserves QMS causal ordering:

`ImprintFieldState -> DetectorSignal -> DigitalRecord -> DiagnosticReport`.

Destroyed upstream correlations are reported as unavailable; diagnostics never
reconstruct field states or detector signals from records. Extension hooks are
reserved for adaptive coherence metrics, distributed detector diagnostics, and
streaming observability analysis.
