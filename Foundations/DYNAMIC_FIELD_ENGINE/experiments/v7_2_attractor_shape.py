import sys
import os

# path fix
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
import matplotlib.pyplot as plt

from core.kappa_engine import compute_kappa, compute_signature
from simulations.wave_generator import generate_wave


# -----------------------------
# TRAJECTORY FEATURES
# -----------------------------
def trajectory_features(inst, pat):

    dx = np.diff(inst)
    dy = np.diff(pat)

    # trajectory length
    length = np.sum(np.sqrt(dx**2 + dy**2))

    # direction changes (curvature proxy)
    angles = np.arctan2(dy, dx)
    angle_change = np.mean(np.abs(np.diff(angles)))

    # spread
    spread = np.std(inst) + np.std(pat)

    return {
        "length": length,
        "angle_change": angle_change,
        "spread": spread
    }


# -----------------------------
# ATTRACTOR SHAPE CLASSIFIER
# -----------------------------
def classify_shape(feat):

    length = feat["length"]
    angle = feat["angle_change"]
    spread = feat["spread"]

    # 🟢 LOOP (periodic attractor)
    if angle > 0.1 and length < 1.5:
        return "Loop (Periodic)"

    # 🔵 DRIFT (structured but not looping)
    if angle < 0.1 and length < 2.5:
        return "Drift (Structured)"

    # 🔴 CHAOS
    if length >= 2.5 or spread > 0.2:
        return "Chaotic"

    return "Unknown"


# -----------------------------
# MAIN
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

    feat = trajectory_features(inst, pat)
    shape = classify_shape(feat)

    print("Length:", round(feat["length"], 4))
    print("Angle Change:", round(feat["angle_change"], 4))
    print("Spread:", round(feat["spread"], 4))
    print("Detected:", shape)

    plt.plot(inst, pat, color=color, label=f"{mode} → {shape}")


# -----------------------------
# SAVE
# -----------------------------
os.makedirs("../outputs", exist_ok=True)

plt.legend()
plt.xlabel("Instability")
plt.ylabel("Pattern")
plt.title("V7.2 — Attractor Shape Detection")

plt.savefig("../outputs/v7_2_attractor_shape.png")

print("\n✅ Saved → outputs/v7_2_attractor_shape.png")
