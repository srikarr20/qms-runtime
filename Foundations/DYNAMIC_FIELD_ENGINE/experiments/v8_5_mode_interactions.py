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
# MODES
# -----------------------------
def extract_modes(frame):

    norm = (frame - np.min(frame)) / (np.ptp(frame) + 1e-8)
    thresh = np.percentile(norm, 80)

    binary = norm > thresh

    labeled, num = label(binary)

    return labeled, num


# -----------------------------
# INTERACTION DETECTION
# -----------------------------
def detect_interactions(kappa):

    merges = []
    splits = []

    prev_count = None

    for t in range(len(kappa)):

        _, num = extract_modes(kappa[t])

        if prev_count is not None:

            if num < prev_count:
                merges.append(t)

            elif num > prev_count:
                splits.append(t)

        prev_count = num

    return merges, splits


# -----------------------------
# MAIN
# -----------------------------
print("\n🚀 Running V8.5 Mode Interaction Engine\n")

I = generate_system()
kappa = compute_kappa(I)

merges, splits = detect_interactions(kappa)

print("Splits:", splits)
print("Merges:", merges)


# -----------------------------
# VISUALIZATION
# -----------------------------
plt.figure(figsize=(10,4))

counts = [extract_modes(kappa[t])[1] for t in range(len(kappa))]
plt.plot(counts, label="Mode Count")

for s in splits:
    plt.axvline(s, color="green", linestyle="--")

for m in merges:
    plt.axvline(m, color="red", linestyle="--")

plt.title("Mode Interactions (Split / Merge)")
plt.xlabel("Time")
plt.ylabel("Modes")

# save
output_dir = os.path.join(os.getcwd(), "outputs")
os.makedirs(output_dir, exist_ok=True)

save_path = os.path.join(output_dir, "v8_5_interactions.png")
plt.savefig(save_path)

print("\n✅ Saved →", save_path)
