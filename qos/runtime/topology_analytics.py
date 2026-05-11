import json
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path


class TopologyAnalytics:

    def __init__(

        self,

        runtime_tensor,

    ):

        self.runtime_tensor = runtime_tensor

        self.detector_history = np.array([

            x["detector_states"]

            for x in runtime_tensor

        ])

        self.coherence = np.array([

            x["coherence"]

            for x in runtime_tensor

        ])

        self.fidelity = np.array([

            x["fidelity"]

            for x in runtime_tensor

        ])

    # ======================================================
    # METRICS
    # ======================================================

    def propagation_velocity(self):

        delta = np.diff(

            self.detector_history,

            axis=0,

        )

        velocity = np.mean(
            np.abs(delta)
        )

        return float(velocity)

    def detector_variance(self):

        variance = np.mean(

            np.var(

                self.detector_history,

                axis=1,

            )

        )

        return float(variance)

    def coherence_survival(self):

        return float(
            np.mean(self.coherence)
        )

    def fidelity_survival(self):

        return float(
            np.mean(self.fidelity)
        )

    def saturation_index(self):

        max_state = np.max(
            np.abs(
                self.detector_history
            )
        )

        mean_state = np.mean(
            np.abs(
                self.detector_history
            )
        )

        return float(
            mean_state / (
                max_state + 1e-9
            )
        )

    # ======================================================
    # SUMMARY
    # ======================================================

    def summary(self):

        return {

            "propagation_velocity":
            self.propagation_velocity(),

            "detector_variance":
            self.detector_variance(),

            "coherence_survival":
            self.coherence_survival(),

            "fidelity_survival":
            self.fidelity_survival(),

            "saturation_index":
            self.saturation_index(),

        }

    # ======================================================
    # VISUALIZATION
    # ======================================================

    def visualize(

        self,

        save=True,

    ):

        metrics = self.summary()

        names = list(metrics.keys())

        values = list(metrics.values())

        plt.figure(
            figsize=(10, 5)
        )

        plt.bar(
            names,
            values,
        )

        plt.xticks(rotation=15)

        plt.title(
            "Topology Stability Analytics"
        )

        plt.tight_layout()

        # ==============================================
        # EXPORT
        # ==============================================

        if save:

            export_dir = Path(

                "qos/artifacts/topology_analytics"

            )

            export_dir.mkdir(

                parents=True,

                exist_ok=True,

            )

            chart_path = (

                export_dir
                / "topology_analytics.png"

            )

            json_path = (

                export_dir
                / "topology_analytics.json"

            )

            plt.savefig(

                chart_path,

                dpi=300,

            )

            with open(

                json_path,

                "w",

            ) as f:

                json.dump(

                    metrics,

                    f,

                    indent=4,

                )

            print(
                "\n=== Topology Analytics Exported ==="
            )

            print(chart_path)

            print(json_path)

        plt.show()
