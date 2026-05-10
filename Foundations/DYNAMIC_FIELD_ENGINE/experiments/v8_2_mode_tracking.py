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
# CENTROID TRACKING
# -----------------------------
def compute_centroids(labeled, num):

    centroids = []

    for i in range(1, num+1):

        coords = np.argwhere(labeled == i)

        if len(coords) > 0:
            centroid = np.mean(coords, axis=0)
            centroids.append(centroid)

    return centroids


# -----------------------------
# TRACK MODES OVER TIME
# -----------------------------
def track_modes(kappa):

    trajectories = []

    prev_centroids = None

    for t in range(len(kappa)):

        labeled, num = extract_modes(kappa[t])
        centroids = compute_centroids(labeled, num)

        if prev_centroids is not None and centroids:

            # match nearest centroids
            distances = []

            for c in centroids:
                d = [np.linalg.norm(c - p) for p in prev_centroids]
                distances.append(np.min(d))

            trajectories.append(np.mean(distances))

        else:
            trajectories.append(0)

        prev_centroids = centroids

    return np.array(trajectories)


# -----------------------------
# MAIN
# -----------------------------
print("\n🚀 Running V8.2 Mode Tracking Engine\n")

I = generate_system()
kappa = compute_kappa(I)

motion = track_modes(kappa)


# -----------------------------
# VISUALIZATION
# -----------------------------
plt.figure(figsize=(10,4))

plt.plot(motion)
plt.title("Mode Motion (Centroid Drift)")
plt.xlabel("Time")
plt.ylabel("Average Movement")

# save
output_dir = os.path.join(os.getcwd(), "outputs")
os.makedirs(output_dir, exist_ok=True)

save_path = os.path.join(output_dir, "v8_2_mode_tracking.png")
plt.savefig(save_path)

print("\n✅ Saved →", save_path)
