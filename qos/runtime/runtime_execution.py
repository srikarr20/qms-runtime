import numpy as np

from qos.runtime.runtime_tensor import (
    RuntimeTensor,
)

from qos.runtime.field_runtime import (
    FieldRuntime,
)

from qos.runtime.detector_runtime import (
    DetectorRuntime,
)

from qos.runtime.scheduler_runtime import (
    SchedulerRuntime,
)

from qos.runtime.memory_runtime import (
    MemoryRuntime,
)


class RuntimeExecution:

    def __init__(

        self,

        runtime_steps=240,

    ):

        self.runtime_steps = (
            runtime_steps
        )

        self.field_runtime = (
            FieldRuntime()
        )

        self.detector_runtime = (
            DetectorRuntime()
        )

        self.scheduler_runtime = (
            SchedulerRuntime()
        )

        self.memory_runtime = (
            MemoryRuntime()
        )

        self.environmental_loss = (
            0.05
        )

        self.detector_loss = (
            0.05
        )

        self.noise_floor = (
            0.001
        )

        self.field_history = []

        self.runtime_tensor = []

    # ======================================================
    # EXECUTE
    # ======================================================

    def execute(self):

        for runtime_step in range(
            self.runtime_steps
        ):

            field = (
                self.field_runtime
                .evolve_field(
                    runtime_step
                )
            )

            observability = np.mean(
                np.abs(field)
            )

            coherence = np.std(
                field
            )

            self.detector_runtime.update(
                observability
            )

            self.memory_runtime.update(
                self.detector_runtime
                .detector_states
            )

            coupling = (
                self.detector_runtime
                .coupling_mask(
                    self.field_runtime.x
                )
            )

            field *= coupling

            field *= (
                1
                - self.environmental_loss
            )

            field *= (
                1
                - self.detector_loss
            )

            field += np.random.normal(

                0,

                self.noise_floor,

                size=field.shape,

            )

            self.field_history.append(
                field.copy()
            )

            tensor = RuntimeTensor(

                runtime_step=runtime_step,

                coherence=float(
                    coherence
                ),

                fidelity=float(
                    observability
                ),

                noise=float(
                    self.noise_floor
                ),

                detector_loss=float(
                    self.detector_loss
                ),

                environmental_loss=float(
                    self.environmental_loss
                ),

                detector_states=(
                    self.detector_runtime
                    .detector_states
                    .tolist()
                ),

                memory_states=(
                    self.detector_runtime
                    .detector_memory
                    .tolist()
                ),

                scheduler_windows=(
                    self.scheduler_runtime
                    .detector_windows
                    .tolist()
                ),

                scheduler_latency=(
                    self.scheduler_runtime
                    .detector_latency
                    .tolist()
                ),

                topology_state={

                    "detector_positions":

                        self.detector_runtime
                        .detector_positions

                },

                metadata={

                    "runtime_type":
                        "RuntimeExecution"

                },

            )

            self.runtime_tensor.append(
                tensor.to_dict()
            )

        return (

            np.array(
                self.field_history
            ),

            self.runtime_tensor,

        )
