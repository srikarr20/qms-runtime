import sys
import os

# 🔧 Fix path (so core imports work)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
import matplotlib.pyplot as plt

from core.kappa_engine import compute_kappa, compute_signature
from simulations.wave_generator import generate_wave


# -----------------------------
# DYNAMICAL FEATURES
# -----------------------------
def trajectory_features(inst, pat):

    spread = np.std(inst) + np.std(pat)

    area = (np.max(inst) - np.min(inst)) * (np.max(pat) - np.min(pat))

    length = np.sum(np.sqrt(np.diff(inst)**2 + np.diff(pat)**2))

    return {
        "spread": spread,
        "area": area,
        "length": length
    }


# -----------------------------
# REGIME CLASSIFICATION
# -----------------------------
def classify_regime(feat):

    spread = feat["spread"]
    length = feat["length"]

    # 🟢 Stable attractor
    if spread < 0.1 and length < 2:
        return "Stable"

    # 🔵 Structured (interference / periodic)
    if spread < 0.2 and length < 5:
        return "Structured"

    # 🔴 Chaotic
    if spread >= 0.2 or length >= 5:
        return "Chaotic"

    return "Unknown"


# -----------------------------
# MAIN EXPERIMENT
# -----------------------------
modes = ["stable", "interference", "chaotic"]
colors = ["green", "blue", "red"]

plt.figure()

for mode, color in zip(modes, colors):

    print("\n====================")
    print("Running:", mode)

    I = generate_wave(mode=mode)

    kappa = compute_kappa(I)
    inst, pat = compute_signature(kappa)

    # 🔥 Extract features
    feat = trajectory_features(inst, pat)

    # 🔥 Classify regime
    regime = classify_regime(feat)

    # 🔥 Print diagnostics
    print("Spread:", round(feat["spread"], 4))
    print("Area:", round(feat["area"], 4))
    print("Trajectory Length:", round(feat["length"], 4))
    print("Detected Regime:", regime)

    # Plot trajectory
    plt.plot(inst, pat, color=color, label=f"{mode} → {regime}")


# -----------------------------
# PLOT
# -----------------------------
plt.legend()
plt.xlabel("Instability")
plt.ylabel("Pattern")
plt.title("V7.1 — Regime Detection (Attractor Analysis)")

plt.savefig("../outputs/v7_1_regime_detection.png")

print("\n✅ Saved → outputs/v7_1_regime_detection.png")
