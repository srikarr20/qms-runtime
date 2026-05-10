# PyOCT ↔ QMS Semantic Mapping

## Purpose

This document maps PyOCT coherence-imaging semantics
to the Quantum Measurement Stack (QMS) runtime architecture.

Goal:
- identify operational overlap,
- compare acquisition semantics,
- validate detector-conditioned observability,
- and establish experimental coherence benchmarks.

---

# PyOCT Reconstruction Pipeline

PyOCT reconstruction:

1. Reading Data
2. Background Subtraction
3. Spectral Resampling
4. Aberration Correction
5. Dispersion Correction
6. Fourier Reconstruction
7. OCT Image Formation

---

# QMS Runtime Pipeline

QMS runtime:

ImprintFieldState
→ DetectorSignal
→ DigitalRecord
→ DiagnosticReport
→ ControlDecision

---

# Semantic Correspondence

| PyOCT | QMS |
|---|---|
| Raw spectral acquisition | ImprintFieldState |
| InterferencePattern | DetectorSignal |
| OCT reconstruction | Acquisition |
| OCTData | DigitalRecord |
| PhaseRegistration | coherence transfer |
| CAO adaptive optics | adaptive observability |
| dispersion correction | detector-conditioned reconstruction |
| spectral sampling | acquisition bandwidth |
| reconstruction degradation | observability loss |

---

# Key Alignment Areas

## 1. Coherence-Sensitive Acquisition

PyOCT explicitly preserves and processes interference patterns:

- self.InterferencePattern
- spectral-domain reconstruction
- phase-sensitive processing

This aligns with QMS detector-plane semantics.

---

## 2. Acquisition-Limited Observability

PyOCT reconstruction quality depends on:

- spectral sampling,
- detector calibration,
- dispersion correction,
- phase stability,
- reconstruction fidelity.

This aligns strongly with QMCTB-03 observability semantics.

---

## 3. Adaptive Correction

PyOCT CAO modules perform adaptive correction of imaging degradation.

Potential QMS analogue:
- adaptive detector policy,
- future-run optimization,
- coherence restoration strategies.

---

# Immediate Validation Targets

## Planned Comparative Tests

1. Spectral downsampling
2. Detector bandwidth reduction
3. Phase instability injection
4. Blur/decoherence simulation
5. Reconstruction fidelity comparison

Metrics:
- visibility
- observability index
- coherence transfer
- recoverability
- reconstruction degradation

---

# Scientific Positioning

PyOCT does NOT prove QMS.

However:

PyOCT provides a real-world coherence-sensitive acquisition
and reconstruction system whose operational semantics align
strongly with detector-conditioned observability principles
used in QMS.

---

# Next Steps

- integrate PyOCT outputs into QMS DigitalRecord
- compare observability degradation trends
- validate detector-plane causality under acquisition degradation
- compare adaptive reconstruction behaviors
