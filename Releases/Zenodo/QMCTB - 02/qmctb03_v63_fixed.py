# ===============================
# QMCTB-03 (v6.3 fixed)
# EMPIRICAL SMD SCALING
# ===============================

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os

# -------------------------------
# CONFIG
# -------------------------------
N = 256
SIGMA_POINTS = 12
N_AVG = 20
GLOBAL_SEED = 42

L = 5e-3
dx = L / N

lam = 532e-9
z = 0.05

BIN_SIZES = np.arange(2, 65, 2)
D_VALUES  = np.arange(100e-6, 501e-6, 50e-6)

os.makedirs("artifacts", exist_ok=True)

# -------------------------------
# CORE FUNCTIONS
# -------------------------------
def fresnel_2D(E):
    fx = np.fft.fftfreq(N, d=dx)
    FX, FY = np.meshgrid(fx, fx)
    factor = np.clip(1 - (lam*FX)**2 - (lam*FY)**2, 0, None)
    H = np.exp(1j * 2*np.pi*z/lam * np.sqrt(factor))
    return np.fft.ifft2(np.fft.fft2(E) * H)

def far_field(E):
    I = np.abs(np.fft.fftshift(np.fft.fft2(E)))**2
    return I / (I.max() + 1e-12)

def add_noise(I, rng):
    """FIX: noise must be applied — removed in v6.3, restored here."""
    shot = rng.poisson(I * 500) / 500
    read = rng.normal(0, 0.01, size=I.shape)
    return np.clip(shot + read, 0, None)

def compute_visibility(I):
    Nb = I.shape[0]
    if Nb < 10:
        return 0.0
    c = Nb // 2
    w = max(2, Nb // 6)
    line = I[c, c-w:c+w]
    if len(line) < 3:
        return 0.0
    line = np.convolve(line, np.ones(3)/3, mode='same')
    vmax, vmin = line.max(), line.min()
    return (vmax - vmin) / (vmax + vmin + 1e-12)

def pixel_bin(I, b):
    s = (I.shape[0] // b) * b
    if s < b:
        return None
    return I[:s,:s].reshape(s//b, b, s//b, b).mean(axis=(1,3))

# -------------------------------
# SIGMOID FIT
# -------------------------------
def sigmoid(s, V_low, V_high, k, sigma_c):
    return V_low + (V_high-V_low) / (1 + np.exp(np.clip(k*(s-sigma_c), -50, 50)))

def fit_error(sigma_vals, V_vals):
    try:
        p0 = [V_vals[-1], V_vals[0], 5, 2]
        popt, _ = curve_fit(sigmoid, sigma_vals, V_vals, p0=p0, maxfev=20000)
        return np.mean((V_vals - sigmoid(sigma_vals, *popt))**2)
    except:
        return np.inf

# -------------------------------
# BUILD SYSTEM
# -------------------------------
def build_system(d):
    x = np.linspace(-L/2, L/2, N)
    X, Y = np.meshgrid(x, x)
    E_source = np.exp(-(X**2 + Y**2) / (0.6e-3)**2)
    a = 40e-6
    aperture = ((np.abs(X + d/2) < a/2) | (np.abs(X - d/2) < a/2)).astype(float)
    return fresnel_2D(E_source * aperture)

# -------------------------------
# SIMULATION
# FIX: seed reset per bin — fair comparison across bin sizes
# -------------------------------
def simulate(E_det, b):
    sigma_vals = np.linspace(0, np.pi, SIGMA_POINTS)
    V_vals = []

    for sigma in sigma_vals:
        # FIX: reset RNG for each sigma so all bins see same noise sequence
        rng = np.random.default_rng(GLOBAL_SEED)
        I_accum = None

        for _ in range(N_AVG):
            phi = rng.normal(0, max(sigma, 1e-9), size=(N, N))
            E = E_det if sigma == 0 else E_det * np.exp(1j * phi)

            I = far_field(E)
            I_b = pixel_bin(I, b)
            if I_b is None:
                return None, None

            # FIX: apply noise (was missing in v6.3)
            I_b = add_noise(I_b, rng)

            I_accum = I_b if I_accum is None else I_accum + I_b

        I_avg = I_accum / N_AVG
        I_avg /= (I_avg.max() + 1e-12)
        V_vals.append(compute_visibility(I_avg))

    return sigma_vals, np.array(V_vals)

# -------------------------------
# MAIN
# -------------------------------
def main():
    print("\n=== QMCTB-03 v6.3 fixed (EMPIRICAL) ===")
    print(f"Grid: {N}x{N} | N_avg={N_AVG} | bins={BIN_SIZES[0]}..{BIN_SIZES[-1]} step 2")
    print(f"d range: {int(D_VALUES[0]*1e6)}..{int(D_VALUES[-1]*1e6)} µm\n")

    d_list, D_star_list, score_list = [], [], []

    for d in D_VALUES:
        print(f"  d = {int(d*1e6):3d} µm", end="  ", flush=True)
        E_det = build_system(d)

        best_score = -np.inf
        best_bin   = None

        for b in BIN_SIZES:
            sigma_vals, V_vals = simulate(E_det, b)
            if sigma_vals is None:
                continue

            contrast = float(V_vals[0] - V_vals[-1])
            err      = fit_error(sigma_vals, V_vals)
            if err == np.inf or contrast <= 0:
                continue

            score = contrast / (err + 1e-6)

            if score > best_score:
                best_score = score
                best_bin   = b

        if best_bin is not None:
            d_list.append(d)
            D_star_list.append(best_bin)
            score_list.append(best_score)
            # Theoretical Nyquist prediction for comparison
            nyquist_b = lam * z / (dx * d)
            print(f"D* = {best_bin:2d}  (Nyquist pred: {nyquist_b:.1f})  score={best_score:.1f}")
        else:
            print("no valid bin found")

    d_arr = np.array(d_list)
    D_arr = np.array(D_star_list)

    # ── Power law fit ──────────────────────────────────────────────────────────
    b_exp, logA = np.polyfit(np.log(d_arr), np.log(D_arr), 1)
    A = np.exp(logA)

    print(f"\n{'='*40}")
    print(f"EMPIRICAL exponent  b = {b_exp:.3f}")
    print(f"Prefactor           A = {A:.4f}")
    print(f"Fit: D* = {A:.4f} * d^{b_exp:.3f}")
    nyquist_exp = -1.0
    print(f"Nyquist prediction:     b = {nyquist_exp:.1f}")
    print(f"Deviation from Nyquist: {abs(b_exp - nyquist_exp):.3f}")
    print(f"{'='*40}")

    # ── Plot ───────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(d_arr*1e6, D_arr, s=70, zorder=3, label="Empirical D*")

    d_fit = np.linspace(d_arr.min(), d_arr.max(), 200)
    ax.plot(d_fit*1e6, A * d_fit**b_exp, '--', color='#d62728', lw=1.8,
            label=f"Power law fit  b = {b_exp:.3f}")

    # Nyquist prediction overlay
    D_nyquist = lam * z / (dx * d_fit)
    ax.plot(d_fit*1e6, D_nyquist, ':', color='green', lw=1.2, alpha=0.7,
            label=f"Nyquist prediction  b = -1.0")

    ax.set_xlabel("Slit separation d (µm)", fontsize=10)
    ax.set_ylabel("Optimal bin size D*", fontsize=10)
    ax.set_title("QMCTB-03 — Empirical SMD Scaling Law\n"
                 f"b = {b_exp:.3f}  (Nyquist: b = -1.0)", fontsize=11, fontweight='bold')
    ax.legend(fontsize=9); ax.grid(alpha=0.3)

    # Parameter box
    ax.text(0.97, 0.97,
        f"D* = {A:.4f} · d^{b_exp:.3f}\n"
        f"N = {N}  |  N_avg = {N_AVG}\n"
        f"λ = 532 nm  |  z = 5 cm",
        transform=ax.transAxes, fontsize=8, va='top', ha='right',
        fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='white', edgecolor='#cccccc', alpha=0.9))

    plt.tight_layout()
    plt.savefig("artifacts/smd_empirical_scaling.png", dpi=300, bbox_inches='tight')
    plt.savefig("/mnt/user-data/outputs/qmctb03_smd_scaling.png", dpi=300, bbox_inches='tight')
    print("\nSaved → artifacts/smd_empirical_scaling.png")
    plt.show()

if __name__ == "__main__":
    main()
