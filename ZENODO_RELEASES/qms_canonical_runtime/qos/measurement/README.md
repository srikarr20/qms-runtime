# Measurement Layer

Owns detector-plane coupling, detector models, detector phase preservation or
loss, and detector-formed signals.

Input: `ImprintFieldState`.

Output: `DetectorSignal`.

This layer may select or destroy correlations. Once destroyed, higher layers
must not recover them.

