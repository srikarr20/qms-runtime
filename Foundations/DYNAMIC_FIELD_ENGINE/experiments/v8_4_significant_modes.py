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
# MODE EXTRACTION (SIGNIFICANT)
# -----------------------------
def extract_modes(frame):

    norm = (frame - np.min(frame)) / (np.ptp(frame) + 1e-8)
    thresh = np.percentile(norm, 80)

    binary = norm > thresh

    labeled, num = label(binary)

    sizes = []

    for i in range(1, num+1):
        sizes.append(np.sum(labeled == i))

    return labeled, sizes


# -----------------------------
# SIGNIFICANT MODES ONLY
# -----------------------------
def significant_modes(kappa, min_size=200):

    counts = []

    for t in range(len(kappa)):

        labeled, sizes = extract_modes(kappa[t])

        sig = [s for s in sizes if s > min_size]

        counts.append(len(sig))

    return np.array(counts)


# -----------------------------
# LIFECYCLE
# -----------------------------
def lifecycle_events(counts):

    births = []
    deaths = []

    for i in range(1, len(counts)):

        diff = counts[i] - counts[i-1]

        if diff > 1:
            births.append(i)

        elif diff < -1:
            deaths.append(i)

    return births, deaths


# -----------------------------
# MAIN
# -----------------------------
print("\n🚀 Running V8.4 Significant Mode Engine\n")

I = generate_system()
kappa = compute_kappa(I)

counts = significant_modes(kappa)

births, deaths = lifecycle_events(counts)

print("Births:", births)
print("Deaths:", deaths)


# -----------------------------
# VISUALIZATION
# -----------------------------
plt.figure(figsize=(10,4))

plt.plot(counts, label="Significant Modes")

for b in births:
    plt.axvline(b, color="green", linestyle="--")

for d in deaths:
    plt.axvline(d, color="red", linestyle="--")

plt.title("Significant Mode Birth & Death")
plt.xlabel("Time")
plt.ylabel("Mode Count")

# save
output_dir = os.path.join(os.getcwd(), "outputs")
os.makedirs(output_dir, exist_ok=True)

save_path = os.path.join(output_dir, "v8_4_significant_modes.png")
plt.savefig(save_path)

print("\n✅ Saved →", save_path)
