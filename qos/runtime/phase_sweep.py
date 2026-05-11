import json
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path

from qos.runtime.runtime_execution import (
    RuntimeExecution,
)

from qos.runtime.topology_analytics import (
    TopologyAnalytics,
)


class PhaseSweep:

    def __init__(

        self,

        topology="ring",

        runtime_steps=180,

        detector_count=12,

    ):

        self.topology = topology

        self.runtime_steps = runtime_steps

        self.detector_count = detector_count

        self.coupling_range = np.linspace(
            0.02,
            0.40,
            12,
        )

        self.decay_range = np.linspace(
            0.90,
            0.999,
            12,
        )

    # ======================================================
    # SWEEP
    # ======================================================

    def run(self):

        coherence_map = np.zeros(

            (
                len(self.coupling_range),

                len(self.decay_range),

            )

        )

        variance_map = np.zeros_like(
            coherence_map
        )

        velocity_map = np.zeros_like(
            coherence_map
        )

        # ==============================================
        # PARAMETER SWEEP
        # ==============================================

        for i, coupling in enumerate(

            self.coupling_range

        ):

            for j, decay in enumerate(

                self.decay_range

            ):

                runtime = RuntimeExecution(

                    runtime_steps=
                    self.runtime_steps,

                    detector_count=
                    self.detector_count,

                    topology=
                    self.topology,

                )

                # ======================================
                # OVERRIDE TOPOLOGY PARAMETERS
                # ======================================

                runtime.topology_runtime.coupling_strength = (
                    float(coupling)
                )

                runtime.topology_runtime.global_decay = (
                    float(decay)
                )

                field_history, tensor = (
                    runtime.execute()
                )

                analytics = (
                    TopologyAnalytics(
                        tensor
                    )
                )

                summary = (
                    analytics.summary()
                )

                coherence_map[i, j] = (
                    summary[
                        "coherence_survival"
                    ]
                )

                variance_map[i, j] = (
                    summary[
                        "detector_variance"
                    ]
                )

                velocity_map[i, j] = (
                    summary[
                        "propagation_velocity"
                    ]
                )

        return {

            "coherence_map":
            coherence_map,

            "variance_map":
            variance_map,

            "velocity_map":
            velocity_map,

        }

    # ======================================================
    # VISUALIZATION
    # ======================================================

    def visualize(

        self,

        save=True,

    ):

        results = self.run()

        export_dir = Path(

            "qos/artifacts/phase_sweeps"

        )

        export_dir.mkdir(

            parents=True,

            exist_ok=True,

        )

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

            3,

            1,

            figsize=(10, 16),

        )

        for idx, (key, title) in enumerate(metrics):

            im = axes[idx].imshow(

                results[key],

                aspect="auto",

                origin="lower",

                cmap="plasma",

            )

            axes[idx].set_title(title)

            axes[idx].set_xlabel(
                "Global Decay"
            )

            axes[idx].set_ylabel(
                "Coupling Strength"
            )

            axes[idx].set_xticks(
                range(
                    len(
                        self.decay_range
                    )
                )
            )

            axes[idx].set_xticklabels([

                f"{x:.2f}"

                for x in self.decay_range

            ], rotation=45)

            axes[idx].set_yticks(
                range(
                    len(
                        self.coupling_range
                    )
                )
            )

            axes[idx].set_yticklabels([

                f"{x:.2f}"

                for x in self.coupling_range

            ])

            plt.colorbar(
                im,
                ax=axes[idx],
            )

        plt.tight_layout()

        # ==============================================
        # EXPORT
        # ==============================================

        if save:

            chart_path = (

                export_dir
                / f"{self.topology}_phase_sweep.png"

            )

            plt.savefig(

                chart_path,

                dpi=300,

            )

            metadata = {

                "topology":
                self.topology,

                "runtime_steps":
                self.runtime_steps,

                "detector_count":
                self.detector_count,

            }

            with open(

                export_dir
                / f"{self.topology}_phase_metadata.json",

                "w",

            ) as f:

                json.dump(

                    metadata,

                    f,

                    indent=4,

                )

            print(
                "\n=== Phase Sweep Exported ==="
            )

            print(chart_path)

        plt.show()
