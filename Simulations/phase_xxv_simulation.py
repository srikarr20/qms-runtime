# Phase XXV — Simplified Meta-Learning Simulation (Imprint Field Framework)
# Author: Simulation & Development GPT
# Purpose: Demonstrate hierarchical coupling and meta-learning dynamics across five field layers.

import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

# Simulation parameters
n_layers = 5
T = 400
dt = 0.05
times = np.arange(T) * dt

# Physical / dynamical parameters
H = np.linspace(0.8, 1.2, n_layers) * 2.0 * np.pi
Omega_m = 0.6
chi_m = 0.15
gamma = 0.5
psi_drive = 0.0

psi = (0.8 + 0.2 * np.random.randn(n_layers)) * np.exp(1j * 2*np.pi*np.random.rand(n_layers))
Phi = 0.05 * (np.random.randn(n_layers, n_layers))
np.fill_diagonal(Phi, 0.0)

C_t = np.zeros(T)
DeltaC_t = np.zeros(T)
Phi_norm_t = np.zeros(T)
psi_mags = np.zeros((T, n_layers))

def compute_pairwise_coherence(ps):
    n = len(ps)
    if n < 2:
        return 1.0
    tot, count = 0.0, 0
    for i in range(n):
        for j in range(i+1, n):
            overlap = np.vdot(ps[i], ps[j])
            denom = np.abs(ps[i]) * np.abs(ps[j])
            val = (np.abs(overlap) / denom)**2 if denom > 1e-12 else 0.0
            tot += val
            count += 1
    return tot / max(1, count)

for t in range(T):
    C = compute_pairwise_coherence(psi)
    C_t[t], DeltaC_t[t] = C, 1.0 - C
    Phi_norm_t[t] = np.linalg.norm(Phi, ord='fro')
    psi_mags[t, :] = np.abs(psi)

    psi_dot = np.zeros(n_layers, dtype=complex)
    for i in range(n_layers):
        h_term = -1j * H[i] * psi[i]
        coupling = np.sum(Phi[i, :] * psi)
        meta_correction = Omega_m * (1.0 - np.abs(psi[i])**2) * psi[i]
        psi_dot[i] = h_term + coupling + meta_correction + psi_drive

    psi += dt * psi_dot

    pair_term = np.real(np.outer(np.conj(psi), psi))
    mags = np.outer(np.abs(psi), np.abs(psi))
    safe_mags = np.where(mags < 1e-12, 1.0, mags)
    normalized_pair = pair_term / safe_mags

    decoherence_factor = (1.0 - compute_pairwise_coherence(psi))
    dPhi = Omega_m * (normalized_pair - gamma * Phi) - chi_m * decoherence_factor
    np.fill_diagonal(dPhi, 0.0)
    Phi += dt * dPhi

# Visualization
plt.figure(figsize=(8, 4))
plt.plot(times, C_t)
plt.title("Global Coherence (C_t) — Phase XXV Simulation")
plt.xlabel("Time")
plt.ylabel("C_t")
plt.grid(True)
plt.tight_layout()
plt.show()

plt.figure(figsize=(8, 4))
plt.plot(times, DeltaC_t)
plt.title("Coherence Divergence (ΔC = 1 - C_t)")
plt.xlabel("Time")
plt.ylabel("ΔC")
plt.grid(True)
plt.tight_layout()
plt.show()

plt.figure(figsize=(8, 4))
plt.plot(times, Phi_norm_t)
plt.title("Norm of Coupling Matrix Φ over Time")
plt.xlabel("Time")
plt.ylabel("||Φ||")
plt.grid(True)
plt.tight_layout()
plt.show()

plt.figure(figsize=(6, 5))
plt.imshow(Phi, aspect='equal')
plt.title("Final Coupling Matrix Φ")
plt.colorbar(label="Φ_ij")
plt.tight_layout()
plt.show()

print({
    'final_global_coherence': float(C_t[-1]),
    'final_deltaC': float(DeltaC_t[-1]),
    'final_Phi_norm': float(Phi_norm_t[-1])
})
