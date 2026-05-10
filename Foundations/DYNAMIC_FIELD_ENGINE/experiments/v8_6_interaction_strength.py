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

    sizes = []

    for i in range(1, num+1):
        sizes.append(np.sum(labeled == i))

    return num, sizes


# -----------------------------
# STRONG INTERACTIONS ONLY
# -----------------------------
def strong_interactions(kappa, min_change=50):

    splits = []
    merges = []

    prev_num, prev_sizes = extract_modes(kappa[0])

    for t in range(1, len(kappa)):

        num, sizes = extract_modes(kappa[t])

        change = abs(num - prev_num)

        if change > min_change:

            if num > prev_num:
                splits.append(t)
            else:
                merges.append(t)

        prev_num = num
        prev_sizes = sizes

    return splits, merges


# -----------------------------
# MAIN
# -----------------------------
print("\n🚀 Running V8.6 Interaction Strength Engine\n")

I = generate_system()
kappa = compute_kappa(I)

splits, merges = strong_interactions(kappa)

print("Strong splits:", splits)
print("Strong merges:", merges)


# -----------------------------
# VISUALIZATION
# -----------------------------
plt.figure(figsize=(10,4))

counts = [extract_modes(kappa[t])[0] for t in range(len(kappa))]
plt.plot(counts, label="Mode Count")

for s in splits:
    plt.axvline(s, color="green", linestyle="--")

for m in merges:
    plt.axvline(m, color="red", linestyle="--")

plt.title("Strong Interactions Only")
plt.xlabel("Time")
plt.ylabel("Modes")

# save
output_dir = os.path.join(os.getcwd(), "outputs")
os.makedirs(output_dir, exist_ok=True)

save_path = os.path.join(output_dir, "v8_6_strong_interactions.png")
plt.savefig(save_path)

print("\n✅ Saved →", save_path)
