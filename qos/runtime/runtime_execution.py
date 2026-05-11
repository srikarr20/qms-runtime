import numpy as np

from qos.runtime.runtime_tensor import (
    RuntimeTensor,
)

from qos.runtime.topology_runtime import (
    TopologyRuntime,
)


class RuntimeExecution:

    def __init__(

        self,

        runtime_steps=120,

        detector_count=8,

        topology="ring",

        pulse_sites=None,

        pulse_amplitudes=None,

    ):

        self.runtime_steps = runtime_steps

        self.detector_count = detector_count

        self.topology = topology

        self.pulse_sites = (
            pulse_sites
            or [0]
        )

        self.pulse_amplitudes = (
            pulse_amplitudes
            or [1.0]
        )

        self.topology_runtime = (
            TopologyRuntime(

                topology=topology,

                detector_count=
                detector_count,

            )
        )

    # ======================================================
    # EXECUTE
    # ======================================================

    def execute(self):

        field_history = []

        runtime_tensor = []

        detector_states = np.zeros(
            self.detector_count
        )

        memory_states = np.zeros(
            self.detector_count
        )

        # ==============================================
        # MULTI-PULSE INJECTION
        # ==============================================

        for location, amplitude in zip(

            self.pulse_sites,

            self.pulse_amplitudes,

        ):

            detector_states = (

                self.topology_runtime.inject_pulse(

                    detector_states,

                    location=location,

                    amplitude=amplitude,

                )

            )

        # ==============================================
        # RUNTIME LOOP
        # ==============================================

        for step in range(

            self.runtime_steps

        ):

            detector_states = (
                self.topology_runtime.propagate(

                    detector_states
                )
            )

            # ==========================================
            # MEMORY EVOLUTION
            # ==========================================

            memory_states = (

                0.97 * memory_states

                +

                0.03 * detector_states

            )

            coherence = float(

                np.exp(

                    -np.var(
                        detector_states
                    )

                )

            )

            fidelity = float(

                1.0
                /
                (
                    1.0
                    +
                    np.mean(
                        np.abs(
                            detector_states
                        )
                    )
                )

            )

            tensor = RuntimeTensor(

                runtime_step=step,

                detector_states=
                detector_states.tolist(),

                coherence=
                coherence,

                fidelity=
                fidelity,

                noise=0.0,

                detector_loss=float(

                    np.mean(
                        np.abs(
                            detector_states
                        )
                    )

                ),

                environmental_loss=float(

                    1.0 - coherence

                ),

                memory_states=
                memory_states.tolist(),

                scheduler_windows=[

                    step,

                    step + 1,

                ],

                scheduler_latency=0.0,

                topology_state=
                self.topology_runtime.metrics(),

                metadata={

                    "runtime_step":
                    step,

                    "topology":
                    self.topology,

                    "pulse_sites":
                    self.pulse_sites,

                    "pulse_amplitudes":
                    self.pulse_amplitudes,

                },

            )

            runtime_tensor.append(
                tensor
            )

            field_history.append(
                detector_states.copy()
            )

        return (

            field_history,

            runtime_tensor,

        )
