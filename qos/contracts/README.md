# Contracts

`qos.contracts` contains immutable handoff objects shared across QMS layers.

Only these objects should cross canonical layer boundaries:

```text
ImprintFieldState -> DetectorSignal -> DigitalRecord -> DiagnosticReport -> ControlDecision
```

Do not attach lower-layer runtime arrays or mutable state to a higher-layer
handoff. If a layer destroys phase, timing, mode, or correlation information,
that loss must be represented as metadata on the handoff rather than bypassed
through hidden references.

