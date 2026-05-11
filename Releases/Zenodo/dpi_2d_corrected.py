"""
Detector-Plane Imaging (DPI) — 2D Corrected Simulation
=======================================================
Fixes applied to the submitted version:
  1. Destroy far-field: ensemble of intensities (not sqrt(I) through fft2)
  2. Visibility: computed over central fringe window only, not full cross-section
  3. axis('off') excluded from cross-section plot
"""
import numpy as np
import matplotlib.pyplot as plt

# ─────────────────────────────────────────────
# 1. PARAMETERS
# ─────────────────────────────────────────────
λ = 532e-9
k = 2 * np.pi / λ

N = 512
L = 5e-3
dx = L / N

x = np.linspace(-L/2, L/2, N)
X, Y = np.meshgrid(x, x)

d = 250e-6      # slit separation
a = 40e-6       # slit width
z_near = 0.05   # propagation to detector plane (m)
z_far  = 1.0    # observation distance (m)

# ─────────────────────────────────────────────
# 2. SOURCE (Gaussian beam)
# ─────────────────────────────────────────────
w0 = 0.6e-3
E_source = np.exp(-(X**2 + Y**2) / w0**2)
E_source /= np.max(np.abs(E_source))

# ─────────────────────────────────────────────
# 3. DOUBLE-SLIT APERTURE (applied to complex field)
# ─────────────────────────────────────────────
slit1 = np.abs(X + d/2) < a/2
slit2 = np.abs(X - d/2) < a/2
aperture = (slit1 | slit2).astype(float)
E_after = E_source * aperture

# ─────────────────────────────────────────────
# 4. FRESNEL PROPAGATION — 2D angular spectrum
# ─────────────────────────────────────────────
def fresnel_2D(E, dx, lam, z):
    fx = np.fft.fftfreq(N, d=dx)
    FX, FY = np.meshgrid(fx, fx)
    factor = np.maximum(0, 1 - (lam * FX)**2 - (lam * FY)**2)
    H = np.exp(1j * 2 * np.pi * z / lam * np.sqrt(factor))
    return np.fft.ifft2(np.fft.fft2(E) * H)

E_det = fresnel_2D(E_after, dx, λ, z_near)

# ─────────────────────────────────────────────
# 5. DETECTOR MODELS
# ─────────────────────────────────────────────

# 5a. Preserve — full complex amplitude retained
E_preserve = E_det.copy()

# 5b. Destroy — incoherent ensemble average of far-field intensities.
#   Each realisation applies independent random phase per pixel, then
#   records the far-field intensity. Accumulating these converges to
#   the incoherent sum, suppressing all inter-pixel phase correlations.
#   This is the physically correct model; sqrt(I) through fft2 is not.
rng = np.random.default_rng(42)
n_avg = 150

def far_field_intensity(E):
    """Fraunhofer far-field intensity from complex field amplitude."""
    F = np.fft.fftshift(np.fft.fft2(E))
    return np.abs(F)**2

I_destroy_accum = np.zeros((N, N))
for _ in range(n_avg):
    phase = np.exp(1j * rng.uniform(0, 2 * np.pi, size=(N, N)))
    I_destroy_accum += far_field_intensity(E_det * phase)

I_far_destroy = I_destroy_accum / n_avg
I_far_destroy /= I_far_destroy.max()

# Preserve far-field
I_far_preserve = far_field_intensity(E_preserve)
I_far_preserve /= I_far_preserve.max()

# ─────────────────────────────────────────────
# 6. PIXEL BINNING (camera integration)
# ─────────────────────────────────────────────
def pixel_bin(I, bin_size=4):
    s = (N // bin_size) * bin_size
    return I[:s, :s].reshape(N//bin_size, bin_size, N//bin_size, bin_size).mean(axis=(1,3))

I_far_preserve = pixel_bin(I_far_preserve)
I_far_destroy  = pixel_bin(I_far_destroy)

# ─────────────────────────────────────────────
# 7. NOISE MODEL (shot + read)
# ─────────────────────────────────────────────
def add_noise(I, scale=500, read_sigma=0.01):
    shot = np.random.poisson(I * scale) / scale
    read = np.random.normal(0, read_sigma, size=I.shape)
    return np.clip(shot + read, 0, None)

I_far_preserve = add_noise(I_far_preserve)
I_far_destroy  = add_noise(I_far_destroy)

# ─────────────────────────────────────────────
# 8. VISIBILITY — central fringe window only
#    FIX: I.max()/I.min() over full cross-section trivially gives V≈1
#    because the outer envelope floor is near zero.
#    Restrict to central ±15% of pixels where fringes actually are.
# ─────────────────────────────────────────────
Nb = I_far_preserve.shape[0]
center = Nb // 2
line_p = I_far_preserve[center]
line_d = I_far_destroy[center]

window = Nb // 7   # central fringe region (≈ ±14% of array)
line_p_win = line_p[center - window : center + window]
line_d_win = line_d[center - window : center + window]

def visibility(I_win):
    """Michelson visibility over a pre-windowed cross-section."""
    Imax, Imin = I_win.max(), I_win.min()
    return (Imax - Imin) / (Imax + Imin + 1e-9)

Vp = visibility(line_p_win)
Vd = visibility(line_d_win)

print(f"V_preserve = {Vp:.3f}")
print(f"V_destroy  = {Vd:.3f}")
print(f"Contrast   = {Vp / (Vd + 1e-9):.1f}×")

# ─────────────────────────────────────────────
# 9. PLOTS
# ─────────────────────────────────────────────
fig, axs = plt.subplots(2, 3, figsize=(12, 8))
fig.patch.set_facecolor("#0d1117")

def imshow_panel(ax, data, title, cmap="turbo"):
    ax.imshow(data, cmap=cmap, origin="lower")
    ax.set_title(title, color="#e6edf3", fontsize=10, pad=6)
    ax.axis("off")
    ax.set_facecolor("#161b22")

imshow_panel(axs[0,0], np.abs(E_source),    "Source Field |E|",        cmap="inferno")
imshow_panel(axs[0,1], aperture,             "Double-Slit Aperture",    cmap="gray")
imshow_panel(axs[0,2], np.abs(E_det)**2,     "Detector Plane Intensity", cmap="inferno")
imshow_panel(axs[1,0], I_far_preserve,       f"Coherent Far-Field\nV = {Vp:.3f}")
imshow_panel(axs[1,1], I_far_destroy,        f"Decoherent Far-Field\nV = {Vd:.3f}")

# Cross-section — axis ON (fix: don't apply axis('off') here)
ax = axs[1, 2]
ax.set_facecolor("#161b22")
ax.plot(line_p, color="#58a6ff", lw=1.2, label=f"Preserve  V={Vp:.3f}")
ax.plot(line_d, color="#f85149", lw=1.2, ls="--", label=f"Destroy   V={Vd:.3f}")
# Mark the visibility window
ax.axvspan(center - window, center + window, alpha=0.08,
           color="#ffa657", label="Visibility window")
ax.set_title("Cross-Section + Visibility Window",
             color="#e6edf3", fontsize=10, pad=6)
ax.set_xlabel("Pixel", color="#8b949e", fontsize=8)
ax.set_ylabel("Intensity (norm.)", color="#8b949e", fontsize=8)
ax.tick_params(colors="#8b949e", labelsize=7)
for spine in ax.spines.values(): spine.set_color("#30363d")
ax.legend(fontsize=7, labelcolor="#c9d1d9",
          facecolor="#161b22", edgecolor="#30363d")

fig.suptitle(
    f"DPI 2D — Corrected  |  λ={λ*1e9:.0f} nm  d={d*1e6:.0f} µm  "
    f"a={a*1e6:.0f} µm  z={z_near*100:.0f} cm→{z_far:.0f} m  "
    f"bins=4  n_avg={n_avg}",
    color="#e6edf3", fontsize=9, y=1.01
)

plt.tight_layout()
plt.savefig("/mnt/user-data/outputs/dpi_2d_corrected.png",
            dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
print("Saved → /mnt/user-data/outputs/dpi_2d_corrected.png")
