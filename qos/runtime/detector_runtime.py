import numpy as np


class DetectorRuntime:

    def __init__(

        self,

        detector_count=3,

    ):

        self.detector_count = (
            detector_count
        )

        self.detector_states = np.array(

            [0.3, 0.7, 0.4],

            dtype=float,

        )

        self.detector_memory = np.zeros(

            detector_count,

            dtype=float,

        )

        self.detector_positions = [

            80,
            240,
            400,
        ]

    # ======================================================
    # UPDATE
    # ======================================================

    def update(

        self,

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

            delta = (
                target
                - self.detector_states[i]
            )

            self.detector_states[i] += (
                0.04 * delta
            )

            self.detector_memory[i] += (
                0.01
                * self.detector_states[i]
            )

            self.detector_states[i] = np.clip(

                self.detector_states[i],

                0,

                0.99,

            )

            self.detector_memory[i] = np.clip(

                self.detector_memory[i],

                0,

                1.0,

            )

    # ======================================================
    # COUPLING
    # ======================================================

    def coupling_mask(

        self,

        x,

    ):

        # ==================================================
        # IMPORTANT:
        # force FLOAT tensor
        # ==================================================

        coupling = np.ones_like(

            x,

            dtype=float,

        )

        for i, position in enumerate(
            self.detector_positions
        ):

            imprint = np.exp(

                -(
                    (
                        x
                        - position
                    ) ** 2
                )
                / 400

            )

            strength = (
                self.detector_states[i]
            )

            coupling *= (

                1.0

                - strength
                * imprint

            )

        return coupling
