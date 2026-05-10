import pickle
import os
import matplotlib.pyplot as plt

with open(
    "Foundations/ImprintField/ImprintFieldOutputs/field_data.pkl",
    "rb"
) as f:
    data = pickle.load(f)

field = data["field"]

os.makedirs("Diagnostics/runtime_inspection", exist_ok=True)

times = [0, 1, 2, 5]

for t in times:
    plt.figure(figsize=(6,6))

    plt.imshow(field[t][:,:,15])
    plt.colorbar()

    plt.title(f"Midplane Slice t={t}")

    save_path = f"Diagnostics/runtime_inspection/midplane_t{t}.png"

    plt.savefig(save_path, dpi=200, bbox_inches="tight")

    print("saved:", save_path)

    plt.close()
