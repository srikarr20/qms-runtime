import numpy as np


class FieldRuntime:

    def __init__(

        self,

        spatial_points=512,

        wavelength=32,

        coherence_decay=0.996,

    ):

        self.spatial_points = (
            spatial_points
        )

        self.wavelength = (
            wavelength
        )

        self.coherence_decay = (
            coherence_decay
        )

        self.x = np.arange(
            spatial_points
        )

    # ======================================================
    # FIELD
    # ======================================================

    def evolve_field(

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
            np.sin(phase)
            + 1
        )

        coherence = (

            self.coherence_decay
            ** runtime_step

        )

        field *= coherence

        return field
