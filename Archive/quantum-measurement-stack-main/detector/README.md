# Detector Plane Imaging

Detector Plane Imaging defines the measurement-interface layer of the
Quantum Measurement Stack. It characterizes how detector architecture and
internal signal-formation physics determine which correlations present in an
incoming imprint field are preserved, transformed, or irreversibly destroyed
during measurement.

This layer localizes measurement causality: the transition from physically
present information to physically accessible information occurs here, at the
detector plane.

---

## Operational Definition

A **detector** is an active physical system that couples an incoming field to
internal degrees of freedom, producing a measurable signal.

Detector Plane Imaging concerns:
- how detector architecture couples to the imprint field,
- which correlations are preserved during that coupling,
- which correlations are irreversibly lost at the point of detection.

Detectors are not treated as passive or neutral observers.

---

## Core Function

Given a **coherent imprint field** as input, this layer determines:

- whether phase correlations remain accessible,
- whether multi-mode or multi-particle correlations survive,
- whether interference or entanglement can be expressed in the detector output.

Different detector architectures interacting with the same imprint field may
produce qualitatively different observable patterns. This variability
originates here.

---

## Correlation Access Classes

Detector architectures can be operationally classified by their ability to
access correlations present in the imprint field.

### Correlation-Preserving Detection

Correlation-preserving detectors maintain phase, timing, or mode correlations
during signal formation, allowing interference or entanglement present in the
imprint field to be expressed in the output signal.

Such detectors preserve coherence internally long enough for correlations to
remain accessible.

### Correlation-Destroying Detection

Correlation-destroying detectors locally square, threshold, average, or
independently register signals during detection, irreversibly discarding
phase or multi-mode correlations at the detector plane.

These detectors may accurately measure intensity or energy distributions while
rendering coherent correlations inaccessible.

---

## Measurement Causality

The loss of observable coherence is a **local, physical, and irreversible
process** occurring at the detector plane.

This layer formalizes that:
- the imprint field may remain physically coherent,
- observable coherence may nevertheless vanish,
- disappearance of interference or entanglement does not imply loss of
  upstream physical structure.

Collapse-like behavior is thus reframed as detector-local information loss,
not a nonlocal or observer-dependent event.

---

## Canonical Examples (Reference Only)

The following standard quantum systems illustrate how different detector
architectures interacting with the same imprint field yield different
accessible correlations. In all cases, differences arise strictly within
Detector Plane Imaging.

### Double-Slit Interference

A coherent imprint field formed by two path imprints contains spatial phase
correlations.

- Correlation-preserving detection expresses interference fringes.
- Correlation-destroying detection registers only local intensity, rendering
  phase correlations inaccessible.

### Hong–Ou–Mandel Interference

A two-photon imprint field contains precise timing and phase correlations at a
beam splitter.

- Correlation-preserving detection reveals photon bunching.
- Correlation-destroying detection smears timing correlations, reducing or
  eliminating the observed dip.

### Entangled Photon Pairs

An imprint field contains polarization or momentum entanglement.

- Correlation-preserving detection enables observation of nonclassical
  correlations.
- Correlation-destroying detection locally destroys entanglement, leaving only
  classical correlations.

### Matter-Wave Interferometry

A coherent atomic imprint field contains phase correlations accumulated along
separated paths.

- Correlation-preserving detection yields interference fringes.
- Correlation-destroying detection randomizes phase at measurement, reducing
  fringe visibility.

These examples demonstrate that detector architecture alone can determine
whether coherence present in the imprint field becomes observable.

---

## Separation from Higher Layers

This layer ends at the formation of an analog or pre-digitized detector signal.

It does **not** address:
- digitization or sampling,
- thresholding or binning,
- statistical convergence,
- post-processing or reconstruction.

Those responsibilities belong to the **DAQ Integrity Layer**.

---

## Relationship to Adjacent Layers

- **Input**: a coherent imprint field from Imprint Field Dynamics.
- **Output**: a detector-formed signal whose correlation content has already
  been selected or destroyed.

Once correlations are lost at this layer, no higher layer can recover them.

---

## Design Principles

- Measurement causality is localized.
- Detector architecture is physically consequential.
- Correlation loss is irreversible at the detector plane.
- Identical imprint fields may yield different outcomes under different
  detectors.

---

## Status

This layer defines the measurement boundary of the Quantum Measurement Stack.
It is conceptually complete and interface-stable.
Hardware-specific implementations and benchmarks may be added without altering
the layer’s responsibilities.

