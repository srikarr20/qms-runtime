import json
import numpy as np

from pathlib import Path
from datetime import datetime


class RuntimeValidator:

    def __init__(

        self,

        runtime_tensor,

    ):

        self.runtime_tensor = (
            runtime_tensor
        )

    # ======================================================
    # FIDELITY STABILITY
    # ======================================================

    def fidelity_stability(self):

        fidelity = np.array(

            [

                x["fidelity"]

                for x in self.runtime_tensor

            ]

        )

        variance = np.var(
            fidelity
        )

        score = 1.0 / (
            1.0 + variance
        )

        return float(score)

    # ======================================================
    # COHERENCE PERSISTENCE
    # ======================================================

    def coherence_persistence(self):

        coherence = np.array(

            [

                x["coherence"]

                for x in self.runtime_tensor

            ]

        )

        score = np.mean(
            coherence
        )

        return float(score)

    # ======================================================
    # DETECTOR CONVERGENCE
    # ======================================================

    def detector_convergence(self):

        detector_states = np.array(

            [

                x["detector_states"]

                for x in self.runtime_tensor

            ]

        )

        final_state = (
            detector_states[-1]
        )

        spread = np.std(
            final_state
        )

        score = 1.0 / (
            1.0 + spread
        )

        return float(score)

    # ======================================================
    # MEMORY PERSISTENCE
    # ======================================================

    def memory_persistence(self):

        memory_states = []

        for x in self.runtime_tensor:

            if "memory_states" in x:

                memory_states.append(
                    x["memory_states"]
                )

            else:

                detector_count = len(
                    x["detector_states"]
                )

                memory_states.append(

                    [0.0]
                    * detector_count

                )

        memory_states = np.array(
            memory_states
        )

        final_memory = (
            memory_states[-1]
        )

        score = np.mean(
            final_memory
        )

        return float(score)

    # ======================================================
    # RUNTIME STABILITY
    # ======================================================

    def runtime_stability(self):

        fidelity = np.array(

            [

                x["fidelity"]

                for x in self.runtime_tensor

            ]

        )

        coherence = np.array(

            [

                x["coherence"]

                for x in self.runtime_tensor

            ]

        )

        fidelity_gradient = np.mean(

            np.abs(
                np.diff(fidelity)
            )

        )

        coherence_gradient = np.mean(

            np.abs(
                np.diff(coherence)
            )

        )

        instability = (
            fidelity_gradient
            + coherence_gradient
        )

        score = 1.0 / (
            1.0 + instability
        )

        return float(score)

    # ======================================================
    # VALIDATE
    # ======================================================

    def validate(self):

        validation = {

            "fidelity_stability":
                self.fidelity_stability(),

            "coherence_persistence":
                self.coherence_persistence(),

            "detector_convergence":
                self.detector_convergence(),

            "memory_persistence":
                self.memory_persistence(),

            "runtime_stability":
                self.runtime_stability(),

        }

        runtime_score = np.mean(

            list(
                validation.values()
            )

        )

        validation[
            "runtime_score"
        ] = float(
            runtime_score
        )

        return validation

    # ======================================================
    # EXPORT
    # ======================================================

    def export(

        self,

        validation,

    ):

        base_dir = Path(
            "qos/artifacts/validation"
        )

        base_dir.mkdir(

            parents=True,

            exist_ok=True,

        )

        timestamp = datetime.utcnow().strftime(
            "%Y%m%d_%H%M%S"
        )

        export_dir = (

            base_dir

            / f"validation_{timestamp}"

        )

        export_dir.mkdir(

            parents=True,

            exist_ok=True,

        )

        # ==================================================
        # JSON
        # ==================================================

        with open(

            export_dir
            / "runtime_validation.json",

            "w",

        ) as f:

            json.dump(

                validation,

                f,

                indent=4,

            )

        # ==================================================
        # TXT REPORT
        # ==================================================

        report_lines = []

        report_lines.append(
            "=== QOS Runtime Validation ===\n"
        )

        for k, v in validation.items():

            report_lines.append(
                f"{k}: {v:.6f}"
            )

        report = "\n".join(
            report_lines
        )

        with open(

            export_dir
            / "runtime_report.txt",

            "w",

        ) as f:

            f.write(report)

        print(
            "\n=== Runtime Validation Exported ==="
        )

        print(export_dir)
