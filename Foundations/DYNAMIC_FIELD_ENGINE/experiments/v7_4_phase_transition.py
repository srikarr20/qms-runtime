import sys
import os

# path fix
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
import matplotlib.pyplot as plt

from core.kappa_engine import compute_kappa, compute_signature
from simulations.wave_generator import generate_wave


# -----------------------------
# TRANSITION DETECTION
# -----------------------------
def detect_transitions(inst, pat):

    # change rates
    inst_change = np.abs(np.diff(inst))
    pat_change  = np.abs(np.diff(pat))

    # combined signal
    change_signal = inst_change + pat_change

    # threshold = dynamic (adaptive)
    threshold = np.mean(change_signal) + 2*np.std(change_signal)

    # find spikes (transitions)
    transition_points = np.where(change_signal > threshold)[0]

    return change_signal, transition_points


# -----------------------------
# REGIME TRACKING
# -----------------------------
def track_regime(inst):

    regimes = []

    for val in inst:

        if val < 0.3:
            regimes.append("Stable")
        elif val < 0.7:
            regimes.append("Structured")
        else:
            regimes.append("Chaotic")

    return regimes


# -----------------------------
# MAIN
# -----------------------------
modes = ["stable", "interference", "chaotic"]
colors = ["green", "blue", "red"]

plt.figure(figsize=(10,5))

for i, (mode, color) in enumerate(zip(modes, colors)):

    print("\n====================")
    print("Running:", mode)

    I = generate_wave(mode=mode)

    kappa = compute_kappa(I)
    inst, pat = compute_signature(kappa)

    change_signal, transitions = detect_transitions(inst, pat)
    regimes = track_regime(inst)

    print("Transitions detected at frames:", transitions)
    print("Total transitions:", len(transitions))

    # -----------------------------
    # Plot trajectory
    # -----------------------------
    plt.subplot(1,2,1)
    plt.plot(inst, pat, color=color, label=mode)

    # mark transitions
    for t in transitions:
        plt.scatter(inst[t], pat[t], color="black", s=10)

    # -----------------------------
    # Plot change signal
    # -----------------------------
    plt.subplot(1,2,2)
    plt.plot(change_signal, color=color, label=mode)


# -----------------------------
# SAVE
# -----------------------------
output_dir = os.path.join(os.path.dirname(__file__), "..", "outputs")
os.makedirs(output_dir, exist_ok=True)

plt.subplot(1,2,1)
plt.title("Trajectory + Transition Points")
plt.xlabel("Instability")
plt.ylabel("Pattern")
plt.legend()

plt.subplot(1,2,2)
plt.title("Change Signal (Transition Detection)")
plt.xlabel("Time")
plt.ylabel("Change Magnitude")
plt.legend()

save_path = os.path.join(output_dir, "v7_4_phase_transition.png")
plt.savefig(save_path)

print("\n✅ Saved →", save_path)
