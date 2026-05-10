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
# ADAPTIVE MODE EXTRACTION
# -----------------------------
def extract_modes(frame):

    # normalize
    norm = (frame - np.min(frame)) / (np.ptp(frame) + 1e-8)

    # 🔥 adaptive threshold (top 20%)
    thresh = np.percentile(norm, 80)

    binary = norm > thresh

    labeled, num = label(binary)

    return labeled, num


# -----------------------------
# METRICS
# -----------------------------
def mode_metrics(kappa):

    num_modes = []
    mode_sizes = []

    for t in range(len(kappa)):

        labeled, num = extract_modes(kappa[t])

        num_modes.append(num)

        sizes = []
        for i in range(1, num+1):
            sizes.append(np.sum(labeled == i))

        mode_sizes.append(np.mean(sizes) if sizes else 0)

    return np.array(num_modes), np.array(mode_sizes)


# -----------------------------
# MAIN
# -----------------------------
print("\n🚀 Running V8.1 Adaptive Mode Engine\n")

I = generate_system()
kappa = compute_kappa(I)

num_modes, mode_sizes = mode_metrics(kappa)


# -----------------------------
# VISUALIZATION
# -----------------------------
plt.figure(figsize=(12,5))

plt.subplot(1,2,1)
plt.plot(num_modes)
plt.title("Adaptive Mode Count")

plt.subplot(1,2,2)
plt.plot(mode_sizes)
plt.title("Adaptive Mode Size")


# save
output_dir = os.path.join(os.getcwd(), "outputs")
os.makedirs(output_dir, exist_ok=True)

save_path = os.path.join(output_dir, "v8_1_adaptive_modes.png")
plt.savefig(save_path)

print("\n✅ Saved →", save_path)
