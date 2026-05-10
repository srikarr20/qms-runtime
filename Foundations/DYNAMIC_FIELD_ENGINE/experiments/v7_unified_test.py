import matplotlib.pyplot as plt

from core.kappa_engine import compute_kappa, compute_signature
from simulations.wave_generator import generate_wave

modes = ["stable", "interference", "chaotic"]
colors = ["green", "blue", "red"]

plt.figure()

for mode, color in zip(modes, colors):

    print("Running:", mode)

    I = generate_wave(mode=mode)

    kappa = compute_kappa(I)
    inst, pat = compute_signature(kappa)

    plt.plot(inst, pat, color=color, label=mode)

plt.legend()
plt.xlabel("Instability")
plt.ylabel("Pattern")
plt.title("Unified Dynamics Engine — Phase Space")

plt.savefig("../outputs/v7_unified_phase.png")

print("\n✅ Saved → outputs/v7_unified_phase.png")
