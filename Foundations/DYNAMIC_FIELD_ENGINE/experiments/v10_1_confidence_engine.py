import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.ndimage import label


# -----------------------------
# SYSTEM
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
# CONFIDENCE SCORING
# -----------------------------
def compute_confidence(d1, d2, var):

    # normalize each component
    def norm(x):
        return (x - np.min(x)) / (np.ptp(x) + 1e-8)

    d1n = norm(d1)
    d2n = norm(d2)
    varn = norm(var)

    # weighted score
    confidence = 0.4*d1n + 0.3*d2n + 0.3*varn

    return confidence


# -----------------------------
# WARNING DETECTION
# -----------------------------
def detect_warnings(confidence, threshold=0.7):

    warnings = [i for i, c in enumerate(confidence) if c > threshold]

    return warnings


# -----------------------------
# MAIN
# -----------------------------
print("\n🚀 Running V10.1 Confidence Engine\n")

I = generate_system()
kappa = compute_kappa(I)

density = interaction_density(kappa)

d1, d2, var = compute_dynamics(density)

confidence = compute_confidence(d1, d2, var)

warnings = detect_warnings(confidence)

print("\n⚠ Warnings with confidence:")
for w in warnings:
    print(f"t={w}, confidence={round(confidence[w], 2)}")


# -----------------------------
# VISUALIZATION
# -----------------------------
plt.figure(figsize=(12,5))

# density
plt.subplot(1,2,1)
plt.plot(density)
plt.title("Interaction Density")

# confidence
plt.subplot(1,2,2)
plt.plot(confidence)

for w in warnings:
    plt.axvline(w, color="red", linestyle="--")

plt.title("Confidence Signal")

# save
output_dir = os.path.join(os.getcwd(), "outputs")
os.makedirs(output_dir, exist_ok=True)

save_path = os.path.join(output_dir, "v10_1_confidence.png")
plt.savefig(save_path)

print("\n✅ Saved →", save_path)
