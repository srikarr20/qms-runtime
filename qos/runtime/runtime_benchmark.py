import json
import numpy as np

from pathlib import Path

from qos.runtime.runtime_execution import (
    RuntimeExecution,
)

from qos.runtime.runtime_validator import (
    RuntimeValidator,
)


class RuntimeBenchmark:

    def __init__(

        self,

        profile_name,

    ):

        self.profile_name = (
            profile_name
        )

        profile_path = Path(

            "qos/runtime/profiles"

        ) / f"{profile_name}.json"

        if not profile_path.exists():

            raise FileNotFoundError(

                f"Profile not found: {profile_name}"

            )

        with open(profile_path) as f:

            self.profile = json.load(f)

    # ======================================================
    # RUN
    # ======================================================

    def run(self):

        runtime = RuntimeExecution(

            runtime_steps=self.profile[
                "runtime_steps"
            ]

        )

        runtime.environmental_loss = (
            self.profile[
                "environmental_loss"
            ]
        )

        runtime.detector_loss = (
            self.profile[
                "detector_loss"
            ]
        )

        runtime.noise_floor = (
            self.profile[
                "noise_floor"
            ]
        )

        runtime.field_runtime.coherence_decay = (

            self.profile[
                "coherence_decay"
            ]

        )

        field_history, tensor = (
            runtime.execute()
        )

        validator = RuntimeValidator(
            tensor
        )

        validation = (
            validator.validate()
        )

        return {

            "profile":
                self.profile_name,

            "validation":
                validation,

        }
