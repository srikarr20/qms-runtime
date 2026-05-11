import json
import matplotlib.pyplot as plt

from pathlib import Path

from qos.runtime.phase_sweep import (
    PhaseSweep,
)


class CrossTopologyPhaseAnalysis:

    def __init__(

        self,

        runtime_steps=180,

        detector_count=12,

    ):

        self.runtime_steps = runtime_steps

        self.detector_count = detector_count

        self.topologies = [

            "ring",

            "line",

            "random",

            "fully_connected",

        ]

    # ======================================================
    # RUN ALL SWEEPS
    # ======================================================

    def run(self):

        results = {}

        for topology in self.topologies:

            sweep = PhaseSweep(

                topology=topology,

                runtime_steps=
                self.runtime_steps,

                detector_count=
                self.detector_count,

            )

            results[topology] = (
                sweep.run()
            )

        return results

    # ======================================================
    # VISUALIZATION
    # ======================================================

    def visualize(

        self,

        save=True,

    ):

        results = self.run()

        metrics = [

            (
                "coherence_map",
                "Coherence Survival",
            ),

            (
                "variance_map",
                "Detector Variance",
            ),

            (
                "velocity_map",
                "Propagation Velocity",
            ),

        ]

        fig, axes = plt.subplots(

            len(self.topologies),

            len(metrics),

            figsize=(18, 18),

        )

        for row, topology in enumerate(
            self.topologies
        ):

            for col, (metric, title) in enumerate(metrics):

                ax = axes[row, col]

                im = ax.imshow(

                    results[topology][metric],

                    aspect="auto",

                    origin="lower",

                    cmap="plasma",

                )

                ax.set_title(
                    f"{topology}\n{title}"
                )

                ax.set_xlabel(
                    "Global Decay"
                )

                ax.set_ylabel(
                    "Coupling"
                )

                plt.colorbar(
                    im,
                    ax=ax,
                    fraction=0.046,
                )

        plt.tight_layout()

        # ==============================================
        # EXPORT
        # ==============================================

        if save:

            export_dir = Path(

                "qos/artifacts/cross_topology_phase_analysis"

            )

            export_dir.mkdir(

                parents=True,

                exist_ok=True,

            )

            chart_path = (

                export_dir
                / "cross_topology_phase_analysis.png"

            )

            metadata_path = (

                export_dir
                / "cross_topology_phase_metadata.json"

            )

            plt.savefig(

                chart_path,

                dpi=300,

            )

            metadata = {

                "topologies":
                self.topologies,

                "runtime_steps":
                self.runtime_steps,

                "detector_count":
                self.detector_count,

            }

            with open(

                metadata_path,

                "w",

            ) as f:

                json.dump(

                    metadata,

                    f,

                    indent=4,

                )

            print(
                "\n=== Cross Topology Phase Analysis Exported ==="
            )

            print(chart_path)

            print(metadata_path)

        plt.show()
