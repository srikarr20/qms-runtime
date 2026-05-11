QMCTB-01 Methods
Detector-Plane Causality Benchmark
1. Overview and Scope

QMCTB-01 is an instrumentation benchmark designed to evaluate detector-plane causality in quantum interference measurements. The benchmark uses a conventional double-slit optical geometry and standard wave-optics modeling, while explicitly decomposing the measurement process into causally ordered stages.

The objective of QMCTB-01 is to determine whether interference visibility is constrained by upstream field propagation or by local detector-plane coupling that preserves or destroys correlations.

No modifications are made to physical laws, source properties, or propagation dynamics. All deviations from textbook descriptions arise solely from the explicit separation of measurement into irreversible operational layers.


Instrument-Level Surrogate Validation

The simulations presented in QMCTB-01 are implemented as instrument-level surrogates, not illustrative numerical examples. Detector-plane operations, including correlation preservation or destruction, are explicitly enforced within the simulated measurement pipeline rather than applied via post-processing. In this role, the simulations serve the same epistemic function as laboratory instrumentation tests: they delineate operational regimes, identify irreversibility boundaries, and establish falsifiable constraints on detector-plane coherence fidelity. Experimental implementations may substitute hardware-specific detector parameters while preserving the benchmark’s causal structure, enabling direct mapping between simulated outcomes and realizable detector pipelines without modifying upstream


2. Physical Geometry (Unmodified)

The physical layout corresponds to a standard near-field double-slit configuration:

2.1 Field Excitation

A spatially coherent optical field is assumed (e.g., laser illumination). In simulation, this is modeled as a monochromatic scalar field.

2.2 Aperture Plane

Two narrow slits separated by a fixed distance define two spatially distinct propagation paths.

2.3 Free-Space Propagation

The field propagates from the aperture plane to the detection plane over a distance 
𝑧
z. Paraxial Fresnel propagation is used, including quadratic phase factors.

2.4 Detection Plane

A spatially resolved detection plane records the field-dependent detector response.

This geometry is intentionally conventional to avoid confounding measurement causality with apparatus novelty.

3. Causal Decomposition of the Measurement Process

QMCTB-01 explicitly separates the experiment into five irreversible stages. Each stage has a defined input and output, and information lost at any stage cannot be recovered by subsequent processing.

4. Stage 1: Imprint Field Dynamics (Pre-Measurement)

Input:
Coherent excitation and aperture geometry.

Process:
Field propagation, interference, and phase accumulation governed by paraxial wave optics.

Model:
Independent Fresnel propagation from each slit, followed by superposition at the detection plane.

Output:
A coherent imprint field at the detector plane.

At this stage, interference exists as a physical field structure independent of detection, digitization, or statistics. No detectors, observers, or measurement operations are involved.

5. Stage 2: Detector Plane Imaging (Measurement Coupling)

This stage defines how the detector couples to the incoming imprint field.

Two detector models are evaluated against the same imprint field:

5.1 Correlation-Preserving Detector (PRESERVE)

The detector response is proportional to:

∣ψ1​+ψ2​∣2

Phase correlations between propagation paths are retained, and interference fringes are expressed directly in the detector signal.

5.2 Correlation-Destroying Detector (DESTROY)

The detector response is proportional to:

∣ψ1​∣2+∣ψ2​∣2

Phase correlations are discarded locally at the detector plane, and no interference structure is present in the signal.

This distinction models differences between detector architectures rather than interpretive choices. Once correlations are destroyed at this stage, they cannot be recovered downstream.

6. Stage 3: Data Acquisition Integrity (DAQ)

Input:
Analog detector signals.

Process:

Poisson shot noise (photon counting statistics)

Frame-based accumulation

Output:
Discrete digital datasets.

Increasing the number of accumulated frames reduces statistical noise but does not generate interference if correlations were destroyed at the detector plane.

7. Stage 4: Quantum Diagnostics

Input:
Digitized datasets.

Metrics computed:

Fringe visibility

Statistical uncertainty

Output:
Validated diagnostic metrics.

This stage performs inference only and applies no control actions or interpretive assumptions.

8. Stage 5: Quantum Control System (QCS)

Input:
Diagnostic metrics and predefined thresholds.

Function:

Accept, reject, or continue benchmark runs

Adjust frame budget or detector mode for future runs

Constraint:
The QCS acts only forward in time and does not reinterpret previously acquired data.

In QMCTB-01 v1.0, parameters are locked and the benchmark is frozen upon acceptance.

9. Benchmark Acceptance Criteria

The benchmark is considered PASSED if:

Visibility in the PRESERVE path exceeds a predefined threshold

Visibility in the DESTROY path remains low after sufficient averaging

Results are stable across increasing frame counts

These criteria demonstrate that detector-plane coupling alone determines interference visibility for a fixed upstream field.

10. Scope and Non-Claims

QMCTB-01 makes no claims regarding:

New quantum mechanics

Wave-particle duality reinterpretation

Single-photon ontology

Collapse mechanisms

The benchmark is strictly operational and causal in scope.

11. Summary

QMCTB-01 demonstrates that, within a conventional double-slit geometry, the presence or absence of interference fringes is fully determined by local detector-plane correlation handling. The benchmark formalizes this result into a reproducible, diagnosable test suitable for integration into a Quantum Measurement & Control Test Bench.
