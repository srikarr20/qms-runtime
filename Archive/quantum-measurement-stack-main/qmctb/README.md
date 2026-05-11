
## Benchmark Status

- **QMCTB-01**: Frozen baseline benchmark (detector-plane causality)


# Quantum Measurement & Control Test Bench (QMCTB)

The Quantum Measurement & Control Test Bench (QMCTB) defines a set of **canonical,
frozen experimental benchmarks** used to diagnose, validate, and stress-test
quantum measurement systems.

Each QMCTB benchmark is designed to isolate *where* and *how* quantum
information is created, preserved, destroyed, measured, and acted upon across
the full measurement pipeline.

QMCTB benchmarks are **not interpretations**, simulations, or theoretical
models. They are operational tests intended to be run on real experimental
hardware or faithfully reproduced in validated simulations.

---

## Purpose of QMCTB

QMCTB exists to answer a single class of questions:

> *Given a claimed quantum effect, where in the measurement and control pipeline
does it originate, and where can it fail?*

To do this, QMCTB benchmarks:
- Hold physical propagation fixed
- Vary only measurement, acquisition, and control parameters
- Enforce strict causal ordering between layers
- Provide explicit pass/fail criteria

---

## Structure of a QMCTB Benchmark

Each benchmark (e.g. `QMCTB-01`) specifies:

- **Purpose**: What causal claim is being tested
- **Fixed configuration**: What must not change
- **Controlled variables**: Detector, DAQ, or control knobs
- **Observables**: What is measured
- **Expected outcomes**: What success looks like
- **Falsification criteria**: What would invalidate the claim

Benchmarks are written to be:
- Reproducible across labs
- Independent of interpretation
- Traceable to specific physical or operational layers

---

## Freezing and Versioning

Once added, a QMCTB benchmark is considered **frozen**.

- Benchmarks are **not edited** after publication
- Clarifications require a new benchmark version
- Extensions are introduced as new benchmarks (e.g. `QMCTB-02`)

This ensures that QMCTB benchmarks act as **stable reference points** for
comparison, diagnostics, and standards development.

---

## Relationship to the Quantum Measurement Stack

Each QMCTB benchmark explicitly maps onto the layers of the Quantum Measurement
Stack:

1. Imprint Field Dynamics  
2. Detector Plane Imaging  
3. DAQ Integrity  
4. Quantum Diagnostics  
5. Quantum Control System (QCS)

A benchmark failure must be attributable to a specific layer or interface
between layers. Higher layers may not reinterpret or repair failures originating
below them.

---

## Current Benchmarks

- **QMCTB-01 — Detector-Plane Causality Benchmark**  
  Establishes that interference visibility is selected locally by detector
  architecture and data acquisition, not by propagation history or photon
  accumulation.

Additional benchmarks will extend this framework to multi-photon interference,
entanglement, timing jitter, and closed-loop control.

---

## Intended Use

QMCTB benchmarks may be used to:
- Audit experimental claims
- Compare detector and DAQ architectures
- Diagnose measurement-limited experiments
- Validate quantum control policies
- Support metrology and standardization efforts

They are explicitly **not** intended to propose new quantum mechanics or replace
theoretical modeling.

---

## Status

QMCTB is an active test-bench specification.
Benchmarks are added incrementally as stable, standalone references.

