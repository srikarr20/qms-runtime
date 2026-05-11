
# QMCTB-01 v1.0 — FROZEN BENCHMARK
# Do not modify without incrementing benchmark version


from pathlib import Path

ARTIFACT_DIR = Path("qmctb/artifacts")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

"""
QMCTB-01 — Detector Plane Causality Simulation

Simulates near-field double-slit interference with:
- correlation-preserving detection
- correlation-destroying detection

Outputs data suitable for diagnostics and QCS control.
"""

import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# Physical parameters
# -----------------------------
λ = 532e-9          # wavelength (m)
z = 1.0             # propagation distance (m)
d = 200e-6          # slit separation (m)
k = 2 * np.pi / λ

# Detector grid
Nx = 800
x = np.linspace(-5e-3, 5e-3, Nx)

# -----------------------------
# Field definitions
# -----------------------------
def slit_field(x, x0):
    phase = np.exp(1j * k * (x - x0) ** 2 / (2 * z))
    return phase

ψ1 = slit_field(x, -d / 2)
ψ2 = slit_field(x, +d / 2)

# -----------------------------
# Core simulation
# -----------------------------
def run_simulation(frames=100, save_image=False, tag=""):
    """
    Returns:
        preserve_data : np.ndarray
        destroy_data  : np.ndarray
    """

    preserve = np.zeros_like(x)
    destroy = np.zeros_like(x)

    for _ in range(frames):
        # coherent (preserve)
        I_preserve = np.abs(ψ1 + ψ2) ** 2

        # incoherent (destroy)
        I_destroy = np.abs(ψ1) ** 2 + np.abs(ψ2) ** 2

        # shot noise
        preserve += np.random.poisson(I_preserve)
        destroy += np.random.poisson(I_destroy)

    preserve /= frames
    destroy /= frames

    if save_image:
        _save_plot(x, preserve, destroy, frames, tag)

    return preserve, destroy


# -----------------------------
# Visualization (optional)
# -----------------------------
def _save_plot(x, preserve, destroy, frames, tag):
    plt.figure(figsize=(10, 4))
    plt.plot(x * 1e3, destroy, label="Destroy (Intensity-only)")
    plt.plot(x * 1e3, preserve, label="Preserve (Coherent)")
    plt.xlabel("Position (mm)")
    plt.ylabel("Intensity (a.u.)")
    plt.title(f"QMCTB-01 | Frames = {frames}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"qmctb_01_{frames}_{tag}.png", dpi=150)
    plt.savefig(
    ARTIFACT_DIR / f"qmctb_01_{frames}_{tag}.png", dpi=150)
    plt.close()

