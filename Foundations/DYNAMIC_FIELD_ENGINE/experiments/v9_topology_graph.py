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
# OVERLAP MATCHING
# -----------------------------
def compute_overlap(prev_label, curr_label):

    overlaps = {}

    prev_ids = np.unique(prev_label)
    curr_ids = np.unique(curr_label)

    for p in prev_ids:
        if p == 0: continue
        for c in curr_ids:
            if c == 0: continue

            overlap = np.sum((prev_label == p) & (curr_label == c))

            if overlap > 20:  # threshold
                overlaps[(p, c)] = overlap

    return overlaps


# -----------------------------
# GRAPH BUILDING
# -----------------------------
def build_graph(kappa):

    graph = []

    prev_label, _ = extract_modes(kappa[0])

    for t in range(1, len(kappa)):

        curr_label, _ = extract_modes(kappa[t])

        overlaps = compute_overlap(prev_label, curr_label)

        for (p, c), weight in overlaps.items():

            graph.append({
                "time": t,
                "from": p,
                "to": c,
                "weight": weight
            })

        prev_label = curr_label

    return graph


# -----------------------------
# ANALYSIS
# -----------------------------
def analyze_graph(graph):

    total_edges = len(graph)

    weights = [g["weight"] for g in graph]

    avg_weight = np.mean(weights) if weights else 0

    return total_edges, avg_weight


# -----------------------------
# MAIN
# -----------------------------
print("\n🚀 Running V9 Topology Graph Engine\n")

I = generate_system()
kappa = compute_kappa(I)

graph = build_graph(kappa)

edges, avg_w = analyze_graph(graph)

print("Total interactions:", edges)
print("Average interaction strength:", round(avg_w, 2))


# -----------------------------
# VISUALIZATION (interaction density)
# -----------------------------
times = [g["time"] for g in graph]

plt.figure(figsize=(10,4))
plt.hist(times, bins=30)
plt.title("Interaction Density Over Time")
plt.xlabel("Time")
plt.ylabel("Number of Interactions")

# save
output_dir = os.path.join(os.getcwd(), "outputs")
os.makedirs(output_dir, exist_ok=True)

save_path = os.path.join(output_dir, "v9_topology_density.png")
plt.savefig(save_path)

print("\n✅ Saved →", save_path)
