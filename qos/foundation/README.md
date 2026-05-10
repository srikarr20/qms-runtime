# Foundation Layer

Owns pre-measurement field formation, imprint dynamics, persistent field
features, kappa maps, regimes, modes, topology, and prediction signals.

Input: physical or simulated field configuration.

Output: `ImprintFieldState`.

This layer must not import detector, DAQ, diagnostics, or control modules.

Stable APIs:

- `qos.foundation.FieldTensor`: canonical runtime tensor wrapper.
- `qos.foundation.load_legacy_field_data`: compatibility adapter for recovered
  `Foundations/ImprintField/ImprintFieldOutputs/field_data.pkl`.
- `qos.foundation.dynamic_field_engine`: reusable kappa, signature, regime,
  mode, interaction, and predictive-signal primitives.
- `qos.foundation.evolve_tensor`: persistent tensor evolution summary.
- `qos.foundation.ImprintFoundationRuntime`: foundation runtime used by the
  canonical orchestrator.

Executable handoff examples:

- `python3 -m qos.examples.canonical_foundation_handoff`
- `python3 -m qos.examples.legacy_field_data_handoff`
