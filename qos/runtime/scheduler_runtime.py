import numpy as np


class SchedulerRuntime:

    def __init__(

        self,

        detector_count=3,

    ):

        self.detector_latency = np.array(

            [0, 6, 12],

            dtype=int,

        )

        self.detector_windows = np.array(

            [18, 24, 30],

            dtype=int,

        )

        self.detector_count = (
            detector_count
        )

    # ======================================================
    # ACTIVE
    # ======================================================

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
