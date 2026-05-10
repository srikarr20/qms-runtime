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
# MODE COUNT PER FRAME
# -----------------------------
def count_modes(kappa):

    counts = []

    for t in range(len(kappa)):
        _, num = extract_modes(kappa[t])
        counts.append(num)

    return np.array(counts)


# -----------------------------
# BIRTH / DEATH DETECTION
# -----------------------------
def lifecycle_events(counts):

    births = []
    deaths = []

    for i in range(1, len(counts)):

        diff = counts[i] - counts[i-1]

        if diff > 10:   # threshold
            births.append(i)

        elif diff < -10:
            deaths.append(i)

    return births, deaths


# -----------------------------
# MAIN
# -----------------------------
print("\n🚀 Running V8.3 Mode Lifecycle Engine\n")

I = generate_system()
kappa = compute_kappa(I)

counts = count_modes(kappa)
births, deaths = lifecycle_events(counts)

print("Birth events:", births)
print("Death events:", deaths)


# -----------------------------
# VISUALIZATION
# -----------------------------
plt.figure(figsize=(10,4))

plt.plot(counts, label="Mode Count")

for b in births:
    plt.axvline(b, color="green", linestyle="--", label="birth")

for d in deaths:
    plt.axvline(d, color="red", linestyle="--", label="death")

plt.title("Mode Birth & Death")
plt.xlabel("Time")
plt.ylabel("Number of Modes")

# save
output_dir = os.path.join(os.getcwd(), "outputs")
os.makedirs(output_dir, exist_ok=True)

save_path = os.path.join(output_dir, "v8_3_lifecycle.png")
plt.savefig(save_path)

print("\n✅ Saved →", save_path)
