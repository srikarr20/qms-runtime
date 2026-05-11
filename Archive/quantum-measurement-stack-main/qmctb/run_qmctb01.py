"""
QMCTB-01 Runner
Simulation → Diagnostics → QCS
"""

from qmctb.simulations.qmctb_01_detector_plane_causality import run_simulation
from qmctb.diagnostics.visibility import compute_visibility
from qmctb.qcs.qcs_qmctb01 import (
    Diagnostics,
    DetectorMode,
    qcs_decide
)

# -------------------------------
# Configuration
# -------------------------------

VISIBILITY_THRESHOLD = 0.8
N_MAX = 1000
INITIAL_FRAMES = 10

detector_mode = DetectorMode.PRESERVE
N_frames = INITIAL_FRAMES

# -------------------------------
# Benchmark Loop
# -------------------------------

while True:

    print(f"\nRunning QMCTB-01 | frames={N_frames} | mode={detector_mode.name}")

    # ---- Stage 2 + 3: Simulation ----
    data_preserve, data_destroy = run_simulation(
        frames=N_frames,
        tag="qmctb01"
    )

    # ---- Stage 4: Diagnostics ----
    Vp, σp = compute_visibility(data_preserve)
    Vd, σd = compute_visibility(data_destroy)

    diagnostics = Diagnostics(
        V_preserve=Vp,
        sigma_preserve=σp,
        V_destroy=Vd,
        sigma_destroy=σd,
        N_frames=N_frames,
        N_max=N_MAX,
        visibility_threshold=VISIBILITY_THRESHOLD
    )

    # ---- Stage 5: QCS Decision ----
    decision = qcs_decide(diagnostics, detector_mode)

    print(decision.message)
    print(f"V_preserve = {Vp:.3f} ± {σp:.3f}")
    print(f"V_destroy  = {Vd:.3f} ± {σd:.3f}")

    # ---- Act on Decision (future runs only) ----
    if decision.run_status.name == "ACCEPT":
        print("QMCTB-01 PASSED. Configuration frozen.")
        break

    if decision.run_status.name == "REJECT":
        print(f"QMCTB-01 FAILED ({decision.failure_class.name}).")
        break

    # CONTINUE
    detector_mode = decision.detector_mode
    N_frames = decision.next_frame_budget

