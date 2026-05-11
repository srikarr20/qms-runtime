import json
import matplotlib.pyplot as plt

from pathlib import Path

from qos.runtime.runtime_execution import (
    RuntimeExecution,
)

from qos.runtime.topology_analytics import (
    TopologyAnalytics,
)


class TopologyComparison:

    def __init__(

        self,

        runtime_steps=240,

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
    # RUN COMPARISON
    # ======================================================

    def run(self):

        results = {}

        for topology in self.topologies:

            runtime = RuntimeExecution(

                runtime_steps=
                self.runtime_steps,

                detector_count=
                self.detector_count,

                topology=topology,

            )

            field_history, tensor = (
                runtime.execute()
            )

            analytics = (
                TopologyAnalytics(
                    tensor
                )
            )

            results[topology] = (
                analytics.summary()
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

            "propagation_velocity",

            "detector_variance",

            "coherence_survival",

            "fidelity_survival",

            "saturation_index",

        ]

        fig, axes = plt.subplots(

            len(metrics),

            1,

            figsize=(10, 18),

        )

        topologies = list(
            results.keys()
        )

        for idx, metric in enumerate(metrics):

            values = [

                results[t][metric]

                for t in topologies

            ]

            axes[idx].bar(

                topologies,

                values,

            )

            axes[idx].set_title(metric)

        plt.tight_layout()

        # ==============================================
        # EXPORT
        # ==============================================

        if save:

            export_dir = Path(

                "qos/artifacts/topology_comparison"

            )

            export_dir.mkdir(

                parents=True,

                exist_ok=True,

            )

            chart_path = (

                export_dir
                / "topology_comparison.png"

            )

            json_path = (

                export_dir
                / "topology_comparison.json"

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

                    results,

                    f,

                    indent=4,

                )

            print(
                "\n=== Topology Comparison Exported ==="
            )

            print(chart_path)

            print(json_path)

        plt.show()
