# Detector-Plane Imaging

Canonical home for detector-plane imaging implementations.

Frozen/public DPI implementations belong in `v01_frozen`. Experimental
reconstruction and observability branches remain in `qos/experiments` until
their layer responsibilities are cleanly separated.

The canonical detector-plane runtime promotes DPI concepts through
`qos.measurement.detector_plane`:

- phase/coherence preserving detector-plane transfer
- phase/coherence destroying detector-plane transfer
- geometry-neutral detector topology metadata
- irreversible `DetectorSignal` provenance

Double-slit simulations remain valid benchmark or publication references, but
canonical measurement APIs do not require double-slit-specific geometry.
