import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.ndimage import label


# -----------------------------
# SYSTEM (same)
# -----------------------------
def generate_system(T=120, N=128):

    x = np.linspace(0, 2*np.pi, N)
    y = np.linspace(0, 2*np.pi, N)
    X, Y = np.meshgrid(x, y)

    field = []

    for t in range(T):

        if t < 40:
            frame = np.sin(X + 0.1*t)

        elif t < 80:
            frame = np.sin(X + 0.1*t) + np.sin(Y - 0.1*t)

        else:
            frame = np.sin(X + 0.1*t) + np.random.normal(0, 0.7, (N,N))

        field.append(frame)

    return np.array(field)


# -----------------------------
# KAPPA
# -----------------------------
def compute_kappa(I):

    dx = np.diff(I, axis=2, append=I[:,:,-1:])
    dt = np.diff(I, axis=0, append=I[-1:,:,:])

    grad = dx**2 + dt**2
    coherence = 1 / (1 + grad)

    return I * coherence


# -----------------------------
# MODE EXTRACTION
# -----------------------------
def extract_modes(frame):

    norm = (frame - np.min(frame)) / (np.ptp(frame) + 1e-8)
    thresh = np.percentile(norm, 80)

    binary = norm > thresh

    labeled, num = label(binary)

    return labeled, num


# -----------------------------
# INTERACTION DENSITY
# -----------------------------
def interaction_density(kappa):

    density = []

    prev_label, _ = extract_modes(kappa[0])

    for t in range(1, len(kappa)):

        curr_label, _ = extract_modes(kappa[t])

        overlap = np.sum((prev_label > 0) & (curr_label > 0))

        density.append(overlap)

        prev_label = curr_label

    return np.array(density)


# -----------------------------
# DYNAMICS
# -----------------------------
def compute_dynamics(signal):

    d1 = np.gradient(signal)
    d2 = np.gradient(d1)

    window = 5
    var = np.array([
        np.var(signal[max(0, i-window):i+1])
        for i in range(len(signal))
    ])

    return d1, d2, var


# -----------------------------
# CONFIDENCE
# -----------------------------
def compute_confidence(d1, d2, var):

    def norm(x):
        return (x - np.min(x)) / (np.ptp(x) + 1e-8)

    d1n = norm(d1)
    d2n = norm(d2)
    varn = norm(var)

    return 0.4*d1n + 0.3*d2n + 0.3*varn


# -----------------------------
# BIDIRECTIONAL WARNINGS
# -----------------------------
def detect_warnings(d1, d2, var, confidence):

    warnings = []

    for i in range(len(d1)):

        if (
            d1[i] > np.percentile(d1, 75) and
            d2[i] > np.percentile(d2, 75) and
            var[i] > np.percentile(var, 75)
        ):
            warnings.append((i, "build-up", confidence[i]))

        elif (
            d1[i] < np.percentile(d1, 25) and
            d2[i] < np.percentile(d2, 25) and
            var[i] > np.percentile(var, 75)
        ):
            warnings.append((i, "collapse", confidence[i]))

    return warnings


# -----------------------------
# GROUP INTO ZONES
# -----------------------------
def group_warnings(warnings, gap=3):

    if not warnings:
        return []

    warnings = sorted(warnings, key=lambda x: x[0])

    zones = []
    current = [warnings[0]]

    for i in range(1, len(warnings)):

        if warnings[i][0] - warnings[i-1][0] <= gap:
            current.append(warnings[i])
        else:
            zones.append(current)
            current = [warnings[i]]

    zones.append(current)
    return zones


# -----------------------------
# DECISION LOGIC
# -----------------------------
def classify_zone(zone):

    times = [z[0] for z in zone]
    confs = [z[2] for z in zone]

    duration = max(times) - min(times)
    strength = np.mean(confs)

    if strength > 0.7:
        return "CRITICAL"
    elif strength > 0.5:
        return "WARNING"
    elif duration > 2:
        return "WATCH"
    else:
        return "NORMAL"


# -----------------------------
# MAIN
# -----------------------------
print("\n🚀 Running V11 Decision Engine\n")

I = generate_system()
kappa = compute_kappa(I)

density = interaction_density(kappa)

d1, d2, var = compute_dynamics(density)

confidence = compute_confidence(d1, d2, var)

warnings = detect_warnings(d1, d2, var, confidence)

zones = group_warnings(warnings)

print("\n🧭 Decision Output:\n")

for z in zones:

    state = classify_zone(z)

    t_start = z[0][0]
    t_end = z[-1][0]

    print(f"{t_start} → {t_end} : {state}")
