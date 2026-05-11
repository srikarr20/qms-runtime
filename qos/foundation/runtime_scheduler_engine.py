import numpy as np


class RuntimeSchedulerEngine:

    def __init__(

        self,

        spatial_points=512,

        runtime_steps=300,

        wavelength=32,

        coherence_decay=0.996,

        detector_count=3,

    ):

        self.spatial_points = spatial_points

        self.runtime_steps = runtime_steps

        self.wavelength = wavelength

        self.coherence_decay = coherence_decay

        self.detector_count = detector_count

        self.x = np.arange(spatial_points)

        # ====================================================
        # DETECTOR NETWORK
        # ====================================================

        self.detector_states = np.array(

            [0.3, 0.7, 0.4],

            dtype=float,

        )

        self.detector_memory = np.zeros(

            detector_count,

            dtype=float,

        )

        # ====================================================
        # SCHEDULER
        # ====================================================

        self.detector_latency = np.array(

            [0, 6, 12],

            dtype=int,

        )

        self.detector_windows = np.array(

            [18, 24, 30],

            dtype=int,

        )

        self.activation_clock = np.zeros(

            detector_count,

            dtype=int,

        )

        # ====================================================
        # ENVIRONMENT
        # ====================================================

        self.environmental_loss = 0.05

        self.detector_loss = 0.05

        self.noise_floor = 0.001

    # ========================================================
    # DETECTOR ACTIVATION
    # ========================================================

    def detector_active(

        self,

        detector_index,

        runtime_step,

    ):

        latency = self.detector_latency[
            detector_index
        ]

        window = self.detector_windows[
            detector_index
        ]

        phase = (
            runtime_step - latency
        ) % (window * 2)

        return phase < window

    # ========================================================
    # FIELD
    # ========================================================

    def field(

        self,

        runtime_step,

    ):

        phase = (

            2
            * np.pi
            * (
                self.x
                - runtime_step
            )
            / self.wavelength

        )

        field = (
            np.sin(phase) + 1
        )

        coherence = (
            self.coherence_decay
            ** runtime_step
        )

        field *= coherence

        # ====================================================
        # DETECTOR COUPLING
        # ====================================================

        coupling = np.ones_like(field)

        detector_positions = [

            80,
            240,
            400,
        ]

        for i, position in enumerate(
            detector_positions
        ):

            active = self.detector_active(
                i,
                runtime_step,
            )

            if active:

                strength = (
                    self.detector_states[i]
                )

                imprint = np.exp(
                    -(
                        (
                            self.x
                            - position
                        ) ** 2
                    )
                    / 400
                )

                coupling *= (
                    1
                    - strength
                    * imprint
                )

                self.detector_memory[i] += (
                    0.01
                    * strength
                )

        field *= coupling

        # ====================================================
        # LOSSES
        # ====================================================

        field *= (
            1
            - self.environmental_loss
        )

        field *= (
            1
            - self.detector_loss
        )

        # ====================================================
        # NOISE
        # ====================================================

        field += np.random.normal(

            0,

            self.noise_floor,

            size=self.spatial_points,

        )

        return field

    # ========================================================
    # DETECTOR EVOLUTION
    # ========================================================

    def update_detectors(

        self,

        runtime_step,

        observability,

    ):

        target = np.clip(

            observability,

            0,

            1,

        )

        for i in range(
            self.detector_count
        ):

            active = self.detector_active(
                i,
                runtime_step,
            )

            if active:

                delta = (
                    target
                    - self.detector_states[i]
                )

                self.detector_states[i] += (
                    0.04
                    * delta
                )

            # ================================================
            # MEMORY HYSTERESIS
            # ================================================

            self.detector_states[i] += (

                0.002
                * self.detector_memory[i]

            )

            self.detector_states[i] = np.clip(

                self.detector_states[i],

                0,

                0.99,

            )

    # ========================================================
    # EVOLVE
    # ========================================================

    def evolve(self):

        history = []

        tensor = []

        for runtime_step in range(
            self.runtime_steps
        ):

            field = self.field(
                runtime_step
            )

            observability = np.mean(
                np.abs(field)
            )

            coherence = np.std(field)

            self.update_detectors(

                runtime_step,

                observability,

            )

            history.append(field)

            tensor.append(

                {

                    "runtime_step":
                        runtime_step,

                    "fidelity":
                        float(
                            observability
                        ),

                    "coherence":
                        float(
                            coherence
                        ),

                    "detector_loss":
                        float(
                            self.detector_loss
                        ),

                    "environmental_loss":
                        float(
                            self.environmental_loss
                        ),

                    "noise":
                        float(
                            self.noise_floor
                        ),

                    "detector_states":
                        self.detector_states.tolist(),

                    "detector_memory":
                        self.detector_memory.tolist(),

                    "scheduler_windows":
                        self.detector_windows.tolist(),

                    "scheduler_latency":
                        self.detector_latency.tolist(),

                }

            )

        return (

            np.array(history),

            tensor,

        )
