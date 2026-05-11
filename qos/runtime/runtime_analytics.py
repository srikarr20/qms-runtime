import json
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path
from datetime import datetime

from qos.runtime.runtime_benchmark import (
    RuntimeBenchmark,
)


class RuntimeAnalytics:

    def __init__(

        self,

        profiles,

    ):

        self.profiles = profiles

        self.results = []

    # ======================================================
    # RUN BENCHMARKS
    # ======================================================

    def run(self):

        self.results = []

        for profile in self.profiles:

            benchmark = RuntimeBenchmark(
                profile
            )

            result = benchmark.run()

            self.results.append(
                result
            )

        return self.results

    # ======================================================
    # EXPORT
    # ======================================================

    def export(self):

        if len(self.results) == 0:

            raise RuntimeError(
                "No benchmark results available."
            )

        export_dir = Path(
            "qos/artifacts/analytics"
        )

        export_dir.mkdir(

            parents=True,

            exist_ok=True,

        )

        timestamp = datetime.utcnow().strftime(
            "%Y%m%d_%H%M%S"
        )

        analytics_dir = (
            export_dir
            / f"analytics_{timestamp}"
        )

        analytics_dir.mkdir(

            parents=True,

            exist_ok=True,

        )

        # ==================================================
        # METRICS
        # ==================================================

        profile_names = []

        runtime_scores = []

        coherence_scores = []

        memory_scores = []

        stability_scores = []

        fidelity_scores = []

        for result in self.results:

            validation = result[
                "validation"
            ]

            profile_names.append(
                result["profile"]
            )

            runtime_scores.append(
                validation[
                    "runtime_score"
                ]
            )

            coherence_scores.append(
                validation[
                    "coherence_persistence"
                ]
            )

            memory_scores.append(
                validation[
                    "memory_persistence"
                ]
            )

            stability_scores.append(
                validation[
                    "runtime_stability"
                ]
            )

            fidelity_scores.append(
                validation[
                    "fidelity_stability"
                ]
            )

        # ==================================================
        # DASHBOARD
        # ==================================================

        fig, axes = plt.subplots(
            5,
            1,
            figsize=(14, 22),
        )

        # ==================================================
        # RUNTIME SCORE
        # ==================================================

        axes[0].bar(
            profile_names,
            runtime_scores,
        )

        axes[0].set_ylim(0, 1)

        axes[0].set_title(
            "Runtime Score Comparison"
        )

        # ==================================================
        # COHERENCE
        # ==================================================

        axes[1].bar(
            profile_names,
            coherence_scores,
        )

        axes[1].set_ylim(0, 1)

        axes[1].set_title(
            "Coherence Persistence"
        )

        # ==================================================
        # MEMORY
        # ==================================================

        axes[2].bar(
            profile_names,
            memory_scores,
        )

        axes[2].set_ylim(0, 1)

        axes[2].set_title(
            "Memory Persistence"
        )

        # ==================================================
        # STABILITY
        # ==================================================

        axes[3].bar(
            profile_names,
            stability_scores,
        )

        axes[3].set_ylim(0, 1)

        axes[3].set_title(
            "Runtime Stability"
        )

        # ==================================================
        # FIDELITY
        # ==================================================

        axes[4].bar(
            profile_names,
            fidelity_scores,
        )

        axes[4].set_ylim(0, 1)

        axes[4].set_title(
            "Fidelity Stability"
        )

        plt.tight_layout()

        # ==================================================
        # SAVE DASHBOARD
        # ==================================================

        dashboard_path = (
            analytics_dir
            / "runtime_dashboard.png"
        )

        plt.savefig(
            dashboard_path,
            dpi=300,
        )

        # ==================================================
        # SAVE JSON
        # ==================================================

        json_path = (
            analytics_dir
            / "runtime_analytics.json"
        )

        with open(
            json_path,
            "w",
        ) as f:

            json.dump(
                self.results,
                f,
                indent=4,
            )

        # ==================================================
        # REPORT
        # ==================================================

        report_lines = []

        report_lines.append(
            "=== QOS Runtime Analytics ===\n"
        )

        for result in self.results:

            report_lines.append(
                f"\nPROFILE: {result['profile']}"
            )

            for k, v in result[
                "validation"
            ].items():

                report_lines.append(
                    f"{k}: {v:.6f}"
                )

        report = "\n".join(
            report_lines
        )

        report_path = (
            analytics_dir
            / "runtime_report.txt"
        )

        with open(
            report_path,
            "w",
        ) as f:

            f.write(report)

        print(
            "\n=== Runtime Analytics Exported ==="
        )

        print(analytics_dir)
