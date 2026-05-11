# True Entanglement Recorder — Specification

## 1. Purpose

The True Entanglement Recorder (TER) is a detector-plane recording
system designed to capture quantum-accessible electromagnetic
observables **without instantiating measurement at acquisition time**.

All basis selection, coincidence logic, and Bell analysis are deferred
to offline replay.

---

## 2. Core Principle

Measurement causality is localized at the **detector plane**, not at
observation or analysis.

Post-processing can only extract correlations that were physically
preserved in the recorded signal. It cannot create them.

---

## 3. What Is Recorded

The recorder must capture:

- Raw electromagnetic observables (e.g. polarization amplitudes,
  waveforms, or mode-resolved signals)
- Absolute timestamps (ps-scale resolution)
- Channel identity (spatial mode / polarization / detector index)

These quantities must be recorded **without thresholding or projection**.

---

## 4. What Is Explicitly NOT Done at Acquisition

The following operations are forbidden during recording:

- Basis selection
- Hard thresholding (binary clicks only)
- Coincidence windows or logic
- Event rejection or filtering

Any of these irreversibly destroy Bell-accessible information.

---

## 5. Quantum–Classical Boundary

The quantum–classical boundary occurs when continuous EM information
is discretized or averaged such that non-Gaussian, basis-resolvable
structure is lost.

Once crossed, Bell violation becomes mathematically inaccessible,
even in offline replay.

---

## 6. Role of Bell Tests

Bell inequalities are used here as **diagnostic tools**, not as
foundational claims.

- Bell success indicates sufficient recording fidelity
- Bell failure diagnoses which layer of the measurement stack
  destroyed quantum-accessible information

Bell violation is therefore a property of **recording**, not of
post-processing.

---

## 7. Summary Statement

> A True Entanglement Recorder preserves non-Gaussian,
> basis-resolvable electromagnetic observables at the detector plane,
> enabling Bell-accessible correlations to be extracted offline.

