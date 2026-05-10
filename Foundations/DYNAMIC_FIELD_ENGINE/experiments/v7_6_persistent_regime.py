import numpy as np
import matplotlib.pyplot as plt
import os


# -----------------------------
# SYSTEM
# -----------------------------
def generate_system(T=150, N=128):

    x = np.linspace(0, 2*np.pi, N)
    y = np.linspace(0, 2*np.pi, N)
    X, Y = np.meshgrid(x, y)

    field = []

    for t in range(T):

        if t < 50:
            frame = np.sin(X + 0.1*t)

        elif t < 100:
            frame = np.sin(X + 0.1*t) + np.sin(Y - 0.1*t)

        else:
            frame = np.sin(X + 0.1*t) + np.random.normal(0, 0.6, (N,N))

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
# SIGNATURE
# -----------------------------
def compute_signature(kappa):

    inst = []

    for t in range(1, len(kappa)):

        frame = kappa[t]
        prev  = kappa[t-1]

        temporal = np.mean((frame - prev)**2)
        spatial  = np.std(frame)

        inst.append(temporal * 5 + spatial)

    inst = np.array(inst)

    # normalize
    inst = (inst - np.min(inst)) / (np.ptp(inst) + 1e-8)

    return inst


# -----------------------------
# SMOOTHING (KEY ADDITION)
# -----------------------------
def smooth_signal(signal, window=10):

    smoothed = np.convolve(signal, np.ones(window)/window, mode='same')
    return smoothed


# -----------------------------
# REGIME CLASSIFICATION (PERSISTENT)
# -----------------------------
def classify_persistent(inst):

    labels = []

    for val in inst:

        if val < 0.3:
            labels.append(0)
        elif val < 0.6:
            labels.append(1)
        else:
            labels.append(2)

    return np.array(labels)


# -----------------------------
# CLEAN TRANSITIONS
# -----------------------------
def detect_transitions(labels):

    transitions = []

    for i in range(1, len(labels)):
        if labels[i] != labels[i-1]:
            transitions.append(i)

    return transitions


# -----------------------------
# MAIN
# -----------------------------
print("\n🚀 Running V7.6 Persistent Regime Engine\n")

I = generate_system()

kappa = compute_kappa(I)
inst = compute_signature(kappa)

# 🔥 SMOOTH (critical)
inst_smooth = smooth_signal(inst, window=15)

labels = classify_persistent(inst_smooth)
transitions = detect_transitions(labels)

print("Transitions:", transitions)


# -----------------------------
# VISUALIZATION
# -----------------------------
plt.figure(figsize=(12,5))

# instability
plt.subplot(1,2,1)
plt.plot(inst, alpha=0.3, label="raw")
plt.plot(inst_smooth, label="smoothed")
plt.title("Instability Signal")
plt.legend()

# timeline
plt.subplot(1,2,2)
plt.plot(labels, color="purple")

for t in transitions:
    plt.axvline(t, color="black", linestyle="--")

plt.title("Persistent Regime Timeline")

# save
output_dir = os.path.join(os.getcwd(), "outputs")
os.makedirs(output_dir, exist_ok=True)

save_path = os.path.join(output_dir, "v7_6_persistent_regime.png")
plt.savefig(save_path)

print("\n✅ Saved →", save_path)
