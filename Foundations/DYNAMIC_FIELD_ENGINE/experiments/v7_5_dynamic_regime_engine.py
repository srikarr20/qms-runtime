import numpy as np
import matplotlib.pyplot as plt
import os


# -----------------------------
# DYNAMIC SYSTEM (WITH TRANSITIONS)
# -----------------------------
def generate_system(T=150, N=128):

    x = np.linspace(0, 2*np.pi, N)
    y = np.linspace(0, 2*np.pi, N)
    X, Y = np.meshgrid(x, y)

    field = []

    for t in range(T):

        if t < 50:
            # stable regime
            frame = np.sin(X + 0.1*t)

        elif t < 100:
            # structured regime
            frame = np.sin(X + 0.1*t) + np.sin(Y - 0.1*t)

        else:
            # chaotic regime
            frame = np.sin(X + 0.1*t) + np.random.normal(0, 0.6, (N,N))

        field.append(frame)

    return np.array(field)


# -----------------------------
# KAPPA ENGINE (INLINE)
# -----------------------------
def compute_kappa(I):

    dx = np.diff(I, axis=2, append=I[:,:,-1:])
    dt = np.diff(I, axis=0, append=I[-1:,:,:])

    grad = dx**2 + dt**2
    coherence = 1 / (1 + grad)

    return I * coherence


# -----------------------------
# SIGNATURE (TEMPORAL AWARE)
# -----------------------------
def compute_signature(kappa):

    inst = []
    pat  = []

    for t in range(1, len(kappa)):

        frame = kappa[t]
        prev  = kappa[t-1]

        # temporal energy
        temporal = np.mean((frame - prev)**2)

        # spatial variance
        spatial = np.std(frame)

        inst.append(temporal * 5 + spatial)
        pat.append(np.std(frame))

    inst = np.array(inst)
    pat  = np.array(pat)

    # normalize
    inst = (inst - np.min(inst)) / (np.ptp(inst) + 1e-8)
    pat  = (pat - np.min(pat)) / (np.ptp(pat) + 1e-8)

    return inst, pat


# -----------------------------
# REGIME CLASSIFIER (TIMEWISE)
# -----------------------------
def classify_series(inst):

    labels = []

    for val in inst:

        if val < 0.3:
            labels.append(0)  # stable
        elif val < 0.7:
            labels.append(1)  # structured
        else:
            labels.append(2)  # chaotic

    return np.array(labels)


# -----------------------------
# TRANSITION DETECTION
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
print("\n🚀 Running V7.5 Dynamic Regime Engine\n")

I = generate_system()

kappa = compute_kappa(I)
inst, pat = compute_signature(kappa)

labels = classify_series(inst)
transitions = detect_transitions(labels)

print("Detected transitions at:", transitions)


# -----------------------------
# VISUALIZATION
# -----------------------------
plt.figure(figsize=(12,5))

# trajectory
plt.subplot(1,2,1)
plt.plot(inst, pat, color="purple")

for t in transitions:
    plt.scatter(inst[t], pat[t], color="black", s=20)

plt.title("Phase Trajectory with Transitions")
plt.xlabel("Instability")
plt.ylabel("Pattern")


# timeline classification
plt.subplot(1,2,2)
plt.plot(labels, color="purple")

plt.title("Regime Timeline")
plt.xlabel("Time")
plt.ylabel("Regime (0=Stable,1=Structured,2=Chaotic)")


# -----------------------------
# SAVE
# -----------------------------
output_dir = os.path.join(os.getcwd(), "outputs")
os.makedirs(output_dir, exist_ok=True)

save_path = os.path.join(output_dir, "v7_5_dynamic_regime.png")
plt.savefig(save_path)

print("\n✅ Saved →", save_path)
