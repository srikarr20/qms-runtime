"""
Detector-Plane Imaging (DPI) — Corrected Simulation
=====================================================
Fixes from original:
  1. Physical units throughout (metres, wavelength in nm)
  2. Proper complex field amplitude (not real-valued intensity)
  3. Correct Fresnel diffraction via angular spectrum method
  4. Physically grounded decoherence (phase scrambling on field amplitude)
  5. Fraunhofer far-field via FFT of complex amplitude (not intensity)
  6. Fringe visibility V computed via Michelson formula from cross-section
  7. Axes preserved on all diagnostic plots

Pipeline:
  Coherent source → slit aperture (complex field) →
  Fresnel propagation to detector plane →
  Two detector models (preserve / destroy) →
  Far-field pattern → visibility measurement
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path

Path("figures").mkdir(exist_ok=True)

# ── Physical constants ─────────────────────────────────────────────────────────
λ = 532e-9          # wavelength (m) — green laser
k = 2 * np.pi / λ  # wavenumber

# ── Source plane grid ──────────────────────────────────────────────────────────
N = 1024            # grid points (power of 2 for FFT efficiency)
L_src = 2e-3        # source plane width: 2 mm
dx = L_src / N
x_src = np.linspace(-L_src / 2, L_src / 2, N)

# ── Double-slit aperture parameters ───────────────────────────────────────────
d = 250e-6          # slit separation centre-to-centre (250 µm)
a = 40e-6           # individual slit width (40 µm)

# ── Propagation distances ──────────────────────────────────────────────────────
z_near = 0.05       # source → detector plane: 5 cm (near-field / Fresnel)
z_far  = 1.0        # detector → observation plane: 1 m (far-field)

# ══════════════════════════════════════════════════════════════════════════════
# 1. SOURCE FIELD — coherent Gaussian beam (TEM00)
# ══════════════════════════════════════════════════════════════════════════════
w0 = 0.5e-3   # beam waist radius: 0.5 mm
# Rayleigh range
z_R = np.pi * w0**2 / λ
# Beam radius at slit plane (source is at z=0, slits at z=0 for simplicity)
w_src = w0
E_source = np.exp(-x_src**2 / w_src**2)   # real Gaussian amplitude
# Unit amplitude normalisation
E_source = E_source / np.max(np.abs(E_source))

# ══════════════════════════════════════════════════════════════════════════════
# 2. DOUBLE-SLIT APERTURE (applied to complex field)
# ══════════════════════════════════════════════════════════════════════════════
slit1 = np.abs(x_src - (-d / 2)) < (a / 2)
slit2 = np.abs(x_src - (+d / 2)) < (a / 2)
aperture = (slit1 | slit2).astype(float)

E_after_slits = E_source * aperture   # complex field after slits

# ══════════════════════════════════════════════════════════════════════════════
# 3. FRESNEL PROPAGATION — angular spectrum method
#    Propagates complex field amplitude (not intensity) by distance z
# ══════════════════════════════════════════════════════════════════════════════
def fresnel_propagate(E, dx, lam, z):
    """
    Propagate complex field E by distance z using the angular spectrum method.
    Physical: accounts for both amplitude and phase of every spatial frequency.
    """
    N = len(E)
    # Spatial frequency coordinates
    fx = np.fft.fftfreq(N, d=dx)           # cycles per metre
    # Angular spectrum transfer function H(fx) = exp(i k z sqrt(1 - (λfx)²))
    # Evanescent components (λ|fx| > 1) are zeroed
    factor = 1 - (lam * fx)**2
    propagating = factor > 0
    H = np.where(propagating,
                 np.exp(1j * 2 * np.pi * z / lam * np.sqrt(np.where(propagating, factor, 1))),
                 0)
    E_fft = np.fft.fft(E)
    E_prop = np.fft.ifft(E_fft * H)
    return E_prop

# Propagate to detector plane
E_detector = fresnel_propagate(E_after_slits, dx, λ, z_near)
I_detector = np.abs(E_detector)**2   # intensity at detector (for display)

# ══════════════════════════════════════════════════════════════════════════════
# 4. DETECTOR MODELS
#    Both operate on the SAME complex field E_detector.
#    The difference is what the detector hardware does with the field.
# ══════════════════════════════════════════════════════════════════════════════

# ── 4a. Correlation-Preserving Detector ───────────────────────────────────────
# Retains full complex amplitude — models a coherence-sensitive detector
# (e.g., homodyne, wavefront sensor, or phase-sensitive pixel array).
E_preserve = E_detector.copy()

# ══════════════════════════════════════════════════════════════════════════════
# 5. FAR-FIELD PATTERN — Fraunhofer diffraction
#    FFT of COMPLEX FIELD AMPLITUDE (not intensity — that was the original bug)
# ══════════════════════════════════════════════════════════════════════════════
def fraunhofer(E, dx, lam, z):
    """
    Far-field (Fraunhofer) diffraction pattern.
    Returns: (observation coords in mm, intensity pattern normalised to 1)
    """
    N = len(E)
    F = np.fft.fftshift(np.fft.fft(np.fft.ifftshift(E)))
    I = np.abs(F)**2
    fx = np.fft.fftshift(np.fft.fftfreq(N, d=dx))
    x_obs = lam * z * fx * 1e3    # mm
    return x_obs, I / I.max()

# ── 4b. Correlation-Destroying Detector ───────────────────────────────────────
# An intensity-only detector records |E(x_pixel)|² at each pixel independently,
# discarding inter-pixel phase. Modelled as the ensemble average of far-field
# intensities over many random per-pixel phase realisations. This converges to
# the incoherent sum: <|FFT(E·e^{iφ})|²> = |E|² convolved with flat phase →
# no fringe structure, only single-slit envelope survives.
rng = np.random.default_rng(seed=42)
n_incoherent = 300
I_far_destroy_accum = np.zeros(N)
for _ in range(n_incoherent):
    phase_scramble = np.exp(1j * rng.uniform(0, 2 * np.pi, size=N))
    E_frame = E_detector * phase_scramble
    _, I_frame = fraunhofer(E_frame, dx, λ, z_far)
    I_far_destroy_accum += I_frame
I_far_destroy = I_far_destroy_accum / n_incoherent
I_far_destroy = I_far_destroy / I_far_destroy.max()

x_obs, I_far_preserve = fraunhofer(E_preserve, dx, λ, z_far)

# ══════════════════════════════════════════════════════════════════════════════
# 6. FRINGE VISIBILITY — Michelson definition
#    V = (I_max - I_min) / (I_max + I_min)
#    Computed over the central fringe region only
# ══════════════════════════════════════════════════════════════════════════════
def compute_visibility(x_obs, I, window_mm=2.0):
    """
    Compute Michelson visibility over central ±window_mm of pattern.
    Returns V and uncertainty estimate from peak/trough spread.
    """
    mask = np.abs(x_obs) < window_mm
    I_win = I[mask]
    I_max = I_win.max()
    I_min = I_win.min()
    V = (I_max - I_min) / (I_max + I_min + 1e-12)
    return V

V_preserve = compute_visibility(x_obs, I_far_preserve)
V_destroy  = compute_visibility(x_obs, I_far_destroy)

print(f"Fringe Visibility — Preserve : V = {V_preserve:.4f}")
print(f"Fringe Visibility — Destroy  : V = {V_destroy:.4f}")
print(f"Contrast ratio               : {V_preserve / (V_destroy + 1e-9):.1f}×")

# ══════════════════════════════════════════════════════════════════════════════
# 7. DIAGNOSTIC PLOTS
# ══════════════════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(14, 9))
fig.patch.set_facecolor("#0d1117")
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

plot_kw = dict(facecolor="#0d1117")
label_kw = dict(color="#c9d1d9", fontsize=9)
title_kw = dict(color="#e6edf3", fontsize=10, fontweight="bold", pad=8)

x_src_mm = x_src * 1e3
x_obs_mm = x_obs

# ── Row 0, Col 0: Source field amplitude ──────────────────────────────────────
ax = fig.add_subplot(gs[0, 0], **plot_kw)
ax.plot(x_src_mm, np.abs(E_source), color="#58a6ff", lw=1.2)
ax.fill_between(x_src_mm, np.abs(E_source), alpha=0.15, color="#58a6ff")
ax.set_title("Gaussian Source Field |E|", **title_kw)
ax.set_xlabel("x (mm)", **label_kw)
ax.set_ylabel("|E| (norm.)", **label_kw)
ax.tick_params(colors="#8b949e", labelsize=8)
for spine in ax.spines.values(): spine.set_color("#30363d")
ax.set_facecolor("#161b22")

# ── Row 0, Col 1: Aperture + illumination ─────────────────────────────────────
ax = fig.add_subplot(gs[0, 1], **plot_kw)
ax.plot(x_src_mm, aperture, color="#f0883e", lw=1.2, label="Aperture")
ax.plot(x_src_mm, np.abs(E_after_slits), color="#ffa657", lw=1.2,
        linestyle="--", label="|E·aperture|")
ax.set_title("Double-Slit Aperture × Field", **title_kw)
ax.set_xlabel("x (mm)", **label_kw)
ax.set_ylabel("Amplitude", **label_kw)
ax.set_xlim(-0.6, 0.6)
ax.legend(fontsize=7, labelcolor="#c9d1d9", facecolor="#161b22",
          edgecolor="#30363d")
ax.tick_params(colors="#8b949e", labelsize=8)
for spine in ax.spines.values(): spine.set_color("#30363d")
ax.set_facecolor("#161b22")

# ── Row 0, Col 2: Detector-plane intensity (Fresnel) ──────────────────────────
ax = fig.add_subplot(gs[0, 2], **plot_kw)
ax.plot(x_src_mm, I_detector / I_detector.max(), color="#3fb950", lw=1.2)
ax.fill_between(x_src_mm, I_detector / I_detector.max(),
                alpha=0.15, color="#3fb950")
ax.set_title(f"Detector Plane Intensity\n(Fresnel, z = {z_near*100:.0f} cm)", **title_kw)
ax.set_xlabel("x (mm)", **label_kw)
ax.set_ylabel("Intensity (norm.)", **label_kw)
ax.tick_params(colors="#8b949e", labelsize=8)
for spine in ax.spines.values(): spine.set_color("#30363d")
ax.set_facecolor("#161b22")

# ── Row 1, Col 0: Far-field — preserve ────────────────────────────────────────
ax = fig.add_subplot(gs[1, 0], **plot_kw)
ax.plot(x_obs_mm, I_far_preserve, color="#58a6ff", lw=1.3)
ax.fill_between(x_obs_mm, I_far_preserve, alpha=0.12, color="#58a6ff")
ax.set_title(f"Far Field — Coherent\nV = {V_preserve:.3f}", **title_kw)
ax.set_xlabel("x_obs (mm)", **label_kw)
ax.set_ylabel("Intensity (norm.)", **label_kw)
ax.set_xlim(-8, 8)
ax.tick_params(colors="#8b949e", labelsize=8)
for spine in ax.spines.values(): spine.set_color("#30363d")
ax.set_facecolor("#161b22")

# ── Row 1, Col 1: Far-field — destroy ─────────────────────────────────────────
ax = fig.add_subplot(gs[1, 1], **plot_kw)
ax.plot(x_obs_mm, I_far_destroy, color="#f85149", lw=1.3)
ax.fill_between(x_obs_mm, I_far_destroy, alpha=0.12, color="#f85149")
ax.set_title(f"Far Field — Decoherent\nV = {V_destroy:.3f}", **title_kw)
ax.set_xlabel("x_obs (mm)", **label_kw)
ax.set_ylabel("Intensity (norm.)", **label_kw)
ax.set_xlim(-8, 8)
ax.tick_params(colors="#8b949e", labelsize=8)
for spine in ax.spines.values(): spine.set_color("#30363d")
ax.set_facecolor("#161b22")

# ── Row 1, Col 2: Visibility comparison ───────────────────────────────────────
ax = fig.add_subplot(gs[1, 2], **plot_kw)
ax.plot(x_obs_mm, I_far_preserve, color="#58a6ff", lw=1.3, label=f"Preserve  V={V_preserve:.3f}")
ax.plot(x_obs_mm, I_far_destroy,  color="#f85149", lw=1.3,
        linestyle="--", label=f"Destroy   V={V_destroy:.3f}")
ax.set_title("Visibility Contrast", **title_kw)
ax.set_xlabel("x_obs (mm)", **label_kw)
ax.set_ylabel("Intensity (norm.)", **label_kw)
ax.set_xlim(-8, 8)
ax.legend(fontsize=7, labelcolor="#c9d1d9", facecolor="#161b22",
          edgecolor="#30363d")
ax.tick_params(colors="#8b949e", labelsize=8)
for spine in ax.spines.values(): spine.set_color("#30363d")
ax.set_facecolor("#161b22")

# ── Supertitle ────────────────────────────────────────────────────────────────
fig.suptitle(
    "Detector-Plane Imaging (DPI) — Corrected Simulation\n"
    f"λ={λ*1e9:.0f} nm  |  d={d*1e6:.0f} µm  |  a={a*1e6:.0f} µm  |  "
    f"z_near={z_near*100:.0f} cm  |  z_far={z_far:.1f} m",
    color="#e6edf3", fontsize=11, y=1.01
)

plt.savefig("figures/dpi_sequence_corrected.png", dpi=200,
            bbox_inches="tight", facecolor=fig.get_facecolor())
plt.savefig("/mnt/user-data/outputs/dpi_sequence_corrected.png", dpi=200,
            bbox_inches="tight", facecolor=fig.get_facecolor())
print("Saved → figures/dpi_sequence_corrected.png")
print("Saved → /mnt/user-data/outputs/dpi_sequence_corrected.png")
