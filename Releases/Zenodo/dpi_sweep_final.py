"""
DPI — Final Experiment-Grade Simulation (2D + Decoherence Sweep)
----------------------------------------------------------------
Physically grounded simulation of detector-plane coherence preservation.

Pipeline per σ:
  Same E_det → per-frame phase scramble → far-field intensity →
  ensemble average → pixel bin → shot+read noise → visibility

Fixes over previous version:
  - σ=0 preserve case uses continue to skip destroy loop
  - Shot noise applied per frame (not to ensemble mean)
  - Preserve case uses isolated RNG seed for reproducibility
"""

import numpy as np
import matplotlib.pyplot as plt

# ─────────────────────────────────────────────
# PARAMETERS
# ─────────────────────────────────────────────
λ = 532e-9
N = 512
L = 5e-3
dx = L / N

x = np.linspace(-L/2, L/2, N)
X, Y = np.meshgrid(x, x)

d = 250e-6      # slit separation (m)
a = 40e-6       # slit width (m)
z_near = 0.05   # source → detector plane (m)
z_far  = 1.0    # detector → observation plane (m)

BIN         = 4
NOISE_SCALE = 500
READ_NOISE  = 0.01

SIGMA_VALUES = np.linspace(0, np.pi, 20)
N_AVG        = 80

rng = np.random.default_rng(42)

# ─────────────────────────────────────────────
# SOURCE FIELD (Gaussian TEM00)
# ─────────────────────────────────────────────
w0 = 0.6e-3
E_source = np.exp(-(X**2 + Y**2) / w0**2)
E_source /= np.max(np.abs(E_source))

# ─────────────────────────────────────────────
# DOUBLE-SLIT APERTURE
# ─────────────────────────────────────────────
slit1 = np.abs(X + d/2) < a/2
slit2 = np.abs(X - d/2) < a/2
aperture = (slit1 | slit2).astype(float)
E_after = E_source * aperture

# ─────────────────────────────────────────────
# FRESNEL PROPAGATION (angular spectrum method)
# ─────────────────────────────────────────────
def fresnel_2D(E, dx, lam, z):
    fx = np.fft.fftfreq(N, d=dx)
    FX, FY = np.meshgrid(fx, fx)
    factor = np.maximum(0, 1 - (lam * FX)**2 - (lam * FY)**2)
    H = np.exp(1j * 2 * np.pi * z / lam * np.sqrt(factor))
    return np.fft.ifft2(np.fft.fft2(E) * H)

E_det = fresnel_2D(E_after, dx, λ, z_near)

# ─────────────────────────────────────────────
# FAR FIELD — FFT of complex amplitude (not intensity)
# ─────────────────────────────────────────────
def far_field(E):
    return np.abs(np.fft.fftshift(np.fft.fft2(E)))**2

# ─────────────────────────────────────────────
# PIXEL BINNING
# ─────────────────────────────────────────────
def pixel_bin(I, bin_size):
    s = (N // bin_size) * bin_size
    return I[:s, :s].reshape(
        N // bin_size, bin_size,
        N // bin_size, bin_size
    ).mean(axis=(1, 3))

# ─────────────────────────────────────────────
# NOISE — applied per frame, not to ensemble mean
# ─────────────────────────────────────────────
def add_noise(I, rng_inst):
    """
    Shot noise scales as √N per frame; must be applied before averaging,
    not to the ensemble mean (which would underestimate noise by √N_AVG).
    """
    shot = rng_inst.poisson(I * NOISE_SCALE) / NOISE_SCALE
    read = rng_inst.normal(0, READ_NOISE, size=I.shape)
    return np.clip(shot + read, 0, None)

# ─────────────────────────────────────────────
# VISIBILITY — central fringe window only
# ─────────────────────────────────────────────
def compute_visibility(I):
    Nb = I.shape[0]
    c = Nb // 2
    w = Nb // 7
    line = I[c, c - w : c + w]
    Imax, Imin = line.max(), line.min()
    return (Imax - Imin) / (Imax + Imin + 1e-9)

# ─────────────────────────────────────────────
# PRESERVE CASE (σ = 0, isolated RNG seed)
# ─────────────────────────────────────────────
rng_preserve = np.random.default_rng(0)

I_preserve = far_field(E_det)
I_preserve /= I_preserve.max()
I_preserve_binned = pixel_bin(I_preserve, BIN)
I_preserve_noisy  = add_noise(I_preserve_binned, rng_preserve)
V_preserve = compute_visibility(I_preserve_noisy)

# ─────────────────────────────────────────────
# DECOHERENCE SWEEP
# ─────────────────────────────────────────────
V_list = []

for σ in SIGMA_VALUES:

    # σ = 0 is already handled above; add its value and skip
    if σ == 0:
        V_list.append(V_preserve)
        continue

    # Accumulate far-field intensities across N_AVG independent frames.
    # Shot noise applied per frame before accumulation (physically correct).
    I_accum = np.zeros((N // BIN, N // BIN))

    for _ in range(N_AVG):
        # Phase scramble on complex field at detector plane
        phase = np.exp(1j * σ * rng.normal(size=(N, N)))
        I_frame = far_field(E_det * phase)
        I_frame /= I_frame.max()
        I_frame_binned = pixel_bin(I_frame, BIN)
        I_frame_noisy  = add_noise(I_frame_binned, rng)
        I_accum += I_frame_noisy

    I_destroy = I_accum / N_AVG
    I_destroy /= I_destroy.max()

    V = compute_visibility(I_destroy)
    V_list.append(V)

# ─────────────────────────────────────────────
# RESULTS
# ─────────────────────────────────────────────
print(f"V_preserve        = {V_preserve:.3f}")
print(f"V_destroy (σ=π)   = {V_list[-1]:.3f}")
print(f"Contrast ratio    = {V_preserve / (V_list[-1] + 1e-9):.1f}×")

# ─────────────────────────────────────────────
# PLOT
# ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 5))
fig.patch.set_facecolor("#0d1117")
ax.set_facecolor("#161b22")

ax.plot(SIGMA_VALUES, V_list, "o-",
        color="#58a6ff", lw=1.8, ms=5, label="Simulated V(σ)")
ax.axhline(0.8, color="#f0883e", lw=1.0, ls="--",
           label="QMCTB-01 threshold (V = 0.8)")
ax.axhline(V_preserve, color="#3fb950", lw=0.8, ls=":",
           label=f"V_preserve = {V_preserve:.3f}")

ax.set_xticks([0, np.pi/4, np.pi/2, 3*np.pi/4, np.pi])
ax.set_xticklabels(["0", "π/4", "π/2", "3π/4", "π"],
                   color="#c9d1d9", fontsize=9)
ax.set_yticks(np.arange(0, 1.1, 0.1))
ax.tick_params(colors="#8b949e", labelsize=8)
for spine in ax.spines.values():
    spine.set_color("#30363d")

ax.set_xlabel("Phase noise amplitude σ (rad)", color="#c9d1d9", fontsize=10)
ax.set_ylabel("Fringe Visibility V", color="#c9d1d9", fontsize=10)
ax.set_title(
    "Decoherence Sweep — Visibility vs σ\n"
    f"λ={λ*1e9:.0f} nm | d={d*1e6:.0f} µm | a={a*1e6:.0f} µm | "
    f"z={z_near*100:.0f} cm→{z_far:.0f} m | {BIN}×{BIN} bins | N_avg={N_AVG}",
    color="#e6edf3", fontsize=9, pad=10
)
ax.set_xlim(-0.05, np.pi + 0.05)
ax.set_ylim(0, 1.05)
ax.legend(fontsize=8, labelcolor="#c9d1d9",
          facecolor="#161b22", edgecolor="#30363d")
ax.grid(alpha=0.08, color="#30363d")

plt.tight_layout()
plt.savefig("/mnt/user-data/outputs/dpi_sweep_final.png",
            dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
print("Saved → /mnt/user-data/outputs/dpi_sweep_final.png")
plt.show()
