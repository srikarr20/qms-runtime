

# Measurement Layer Definition (Non-Negotiable)

In this framework, the “detector” refers to the *entire measurement pipeline*:
the detector material, any screens or conversion stages, amplification,
electronics, firmware, digitization, software processing, and the final output
image or data stream.

All of these components together constitute a single irreversible measurement
layer. Once information is lost anywhere within this layer, it cannot be
recovered by downstream processing.

The operator or observer is not part of the measurement layer and has no causal
influence on the physical outcome.

---

# Definition of the Quantum Measurement Stack

This document provides the formal definition and governing rules of the
Quantum Measurement Stack (QMS). It is intended to be read before any
layer-specific documentation.

The definitions in this file are normative. Layer READMEs specify behavior;
this document specifies structure and constraints.

---

## Formal Definition

The Quantum Measurement Stack is a **strictly ordered causal decomposition** of
a quantum experiment from physical state formation to system-level control.

Each layer represents a **distinct physical or operational process** with a
well-defined input and output. Transitions between layers are **irreversible**:
information lost at a given layer is not accessible to any higher layer.

The stack is not a conceptual hierarchy, taxonomy, or abstraction model.
It is a **measurement pipeline** whose ordering reflects physical causality and
engineering constraints.

---

## Scope and Intent

The purpose of this decomposition is to ensure that claims about coherence,
interference, decoherence, or entanglement are traceable to **specific physical
or operational stages**, rather than being conflated across:

- physical dynamics,
- detector coupling,
- data acquisition,
- statistical inference,
- system control.

The stack does not introduce new quantum mechanics. It provides a framework
for organizing, diagnosing, and controlling quantum experiments with clear
causal boundaries.

---

## Governing Rules

The Quantum Measurement Stack enforces the following rules:

1. Each layer operates only on the output of the layer immediately below it.
2. Each layer introduces irreversible information loss.
3. No layer may assume access to information destroyed at a lower layer.
4. Statistical inference and system control are strictly separated.
5. Feedback is permitted only at the top layer and applies only to future runs.
6. Post-processing cannot substitute for measurement or acquisition fidelity.

Violations of these rules result in category errors, not recoverable artifacts.

---

## Relationship to Layer Documentation

Layer-specific READMEs define:
- responsibilities,
- boundaries,
- inputs and outputs,
- failure modes.

They must be interpreted in accordance with the constraints defined here.

This document is authoritative with respect to stack ordering, causality,
and irreversibility.

### Canonical Benchmark

The Quantum Measurement Stack is operationally instantiated by the
**QMCTB-01: Detector-Plane Causality Benchmark** (`qmctb/QMCTB-01.md`),
which provides a concrete experimental test of the causal ordering and
irreversibility defined in this document.

