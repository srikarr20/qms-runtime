
# Imprint Field — Phase XXIV Report Package

This archive contains all outputs and the interactive Jupyter notebook from **Imprint Field Phase XXIV**.

## 📘 Contents

| File | Description |
|------|--------------|
| `ImprintField_PhaseXXIV_Report.ipynb` | Interactive notebook with plots, explanations, and re-runnable demo simulations |
| `sweep_results_completed.pkl` | Python pickle file with final retention sweep results (`(eta, clamp)` grid) |
| `sweep_heatmap_B_completed.png` | Heatmap visualization of Node B retention across parameter sweep |
| `J_trained_full.pkl` | Trained coupling matrix (`J`) after full A→B training |
| `rec_full.pkl` | Recorded node energy responses after full training |
| `stdp_res.pkl` | Results of the STDP plasticity experiment |
| `reduced_fixed_results.pkl` | Reduced-order steady-state analysis results |
| `manifest.pkl` | Summary dictionary of all produced files and their locations |

## 🧭 How to Use

1. **Upload to Google Drive**
   - Upload this ZIP to your Drive and extract it.
   - Open `ImprintField_PhaseXXIV_Report.ipynb` with **Google Colab** (or Jupyter Notebook).

2. **Run the Notebook**
   - The notebook includes:
     - Data loading and visualization cells.
     - Parameter sweep heatmap.
     - Probe responses after full training.
     - Plasticity comparison (Hebbian vs STDP).
     - Reduced-order fixed-point summary.
     - Small, re-runnable demo simulation cell (safe for Colab).

3. **Re-run Experiments (Optional)**
   - You can modify parameters (e.g., learning rate `eta`, clamp values) and re-run short training demos interactively.
   - Full simulations are computationally heavy — start with the demo cells to explore dynamics.

4. **File Paths**
   - All file paths in the notebook assume a local folder structure matching this package.
   - If you move files, update the `paths` dictionary in the notebook’s first code cell.

## 🧩 Next Steps

- **Phase XXV (planned):** Hierarchical coupling and temporal pattern storage experiments.
- You can build on this notebook by extending the simulation to multi-level coherence circuits or by introducing dynamic measurement collapse models.

---

**Created by:** Simulation & Development GPT  
**Package Version:** Phase XXIV — Completed Sweep Report  
**Date:** 2025-11-12
