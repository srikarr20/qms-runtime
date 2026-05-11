# Acquisition Layer

Owns sampling, timing, digitization, thresholding, binning, aggregation, and
storage of detector-formed signals.

Input: `DetectorSignal`.

Output: `DigitalRecord`.

This layer must not access imprint fields directly.

Canonical runtime APIs live in `qos.acquisition.runtime`.

- `CanonicalAcquisitionRuntime` consumes `DetectorSignal` only.
- `AcquisitionPolicy` configures sampling, bit depth, coarse graining, pixel
  binning, detector bandwidth limits, observability scaling, and spatial
  measurement decoherence.
- The output is always a canonical immutable `DigitalRecord`.
- Runtime metadata records QMCTB-03-compatible observability scaling semantics,
  geometry-neutral DPI axes, irreversible acquisition limits, and future hooks
  for adaptive bandwidth, distributed detector arrays, and streaming windows.
