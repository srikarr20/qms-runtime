
**Archival reference:**  
QMCTB-01 v1.0 is archived on Zenodo under DOI
https://doi.org/10.5281/zenodo.17966568.

This document reflects the protocol structure corresponding to that release.



# QMCTB-01 — Detector-Plane Causality Benchmark

**Status:** 🔒 Frozen (Baseline Benchmark)

QMCTB-01 is validated and considered complete.  
It serves as the canonical baseline for demonstrating detector-plane causality
and visibility-based certification in the Quantum Measurement & Control Test Bench (QMCTB).

No further modifications to logic, thresholds, or control flow are permitted.
Future QMCTB experiments must reference this benchmark without altering it.



# QMCTB-01 — Detector-Plane Causality Benchmark

**Status:** FROZEN (v1.0)  
**Purpose:** Reference benchmark for detector-plane causality  
**Last modified:** Do not edit experimental logic without version bump

QMCTB-01 is a frozen benchmark. All future detector-plane experiments
must reference this test bench without modification.


# QMCTB-01  
## Detector-Plane Causality Benchmark

### Classification  
Quantum Measurement & Control Test Bench — Foundational Benchmark

---

## 1. Purpose

QMCTB-01 empirically localizes measurement causality within the detector–DAQ
subsystem by demonstrating that identical coherent optical fields yield
distinct measurement outcomes solely due to detector architecture and data
acquisition strategy.

---

## 2. Scientific Question

Does interference visibility depend on photon accumulation in time, or on
detector-plane access to correlations?

---

## 3. QMCTB Layer Coverage

| Layer | Role |
|------|------|
| Imprint Field Dynamics | Generation of coherent superposition via two paths |
| Detector Plane Imaging | Selection or destruction of phase correlations |
| DAQ Integrity | Preservation or loss of correlations during digitization |
| Quantum Diagnostics | Visibility and correlation metrics |
| QCS | Control decisions based on diagnostics |

---

## 4. Fixed Experimental Configuration

The following parameters remain invariant:

- Optical source and wavelength
- Double-slit geometry
- Source–slit distance
- Slit–detector distance
- Detection plane position
- Ambient conditions

This ensures an identical imprint field across all runs.

---

## 5. Controlled Variables

### 5.1 Detector Architecture

**Correlation-destroying detectors**
- CMOS / sCMOS cameras
- Intensity-integrating CCDs

**Correlation-preserving detectors**
- EMCCD or ICCD (photon-counting mode)
- SPAD arrays with event timing
- Phase-sensitive detection (optional)

---

### 5.2 DAQ Configuration

- Integration time
- Frame averaging
- Event-based vs integrated acquisition
- Thresholding and binning
- Timing resolution (if applicable)

---

## 6. Measurement Protocol

1. Align and stabilize optics.
2. Record near-field images to verify slit geometry.
3. Record far-field data for each detector–DAQ configuration.
4. Sweep integration time at fixed photon flux.
5. Record raw detector output prior to post-processing.

---

## 7. Observables

- Fringe visibility
- Contrast
- Signal-to-noise ratio
- Correlation statistics (where applicable)

---

## 8. Expected Outcomes

| Configuration | Outcome |
|--------------|--------|
| Correlation-destroying detector | Smooth diffraction envelope |
| Correlation-preserving detector | High-visibility interference |
| Longer integration (destroying detector) | No fringe emergence |
| Longer integration (preserving detector) | Improved SNR only |

---

## 9. Falsification Criteria

The benchmark fails if:

- Fringes emerge solely via longer integration on a destroying detector
- Detector swap does not alter outcome
- DAQ rescues correlations destroyed at detection

---

## 10. Interpretation Constraints

- Statistical convergence ≠ physical state evolution
- Absence of fringes ≠ absence of field coherence
- Interpretations must map to a specific QMCTB layer

---

## 11. QCS Implications

Diagnostics may trigger:

- Detector or DAQ reconfiguration
- Measurement veto
- Controlled decoherence injection (future benchmarks)

Control actions apply only to future runs.

---

## 12. Outcome

Successful execution establishes detector-plane causality and validates the
Quantum Measurement & Control Test Bench architecture.

---

## 13.  Acceptance Criteria (v1.0)

A QMCTB-01 run is considered **PASS** if and only if:

1. Correlation-preserving mode yields:
   - Visibility ≥ 0.8
   - Stable under frame increase (N ≥ 100)

2. Correlation-destroying mode yields:
   - Visibility → 0 as N increases
   - No emergent fringes under averaging

3. Artifact image is generated and stored in:
   - `qmctb/artifacts/qmctb_01_<frames>_<tag>.png`

4. QCS returns:
   - `RunStatus.ACCEPT`
   - `FailureClass.NONE`

Any violation constitutes a **FAIL**.



