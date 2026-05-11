import numpy as np


class TopologicalFieldEngine:

    def __init__(
        self,
        n_space=512,
        n_time=200,
        transport_velocity=2,
        coherence_decay=0.999,
        noise_strength=0.002,
    ):

        self.n_space = n_space

        self.n_time = n_time

        self.transport_velocity = (
            transport_velocity
        )

        self.coherence_decay = (
            coherence_decay
        )

        self.noise_strength = (
            noise_strength
        )

    # -----------------------------------
    # INITIAL FIELD
    # -----------------------------------

    def initialize_field(self):

        x = np.arange(
            self.n_space
        )

        field = (
            1.0
            + 0.98
            * np.cos(
                2
                * np.pi
                * x
                / 40
            )
        )

        return field

    # -----------------------------------
    # ENVIRONMENTAL DECOHERENCE
    # -----------------------------------

    def decoherence_mask(
        self,
        step,
    ):

        mask = np.ones(
            self.n_space
        )

        center = (
            180
            + int(
                40
                * np.sin(
                    step / 20
                )
            )
        )

        width = 50

        left = max(
            0,
            center - width,
        )

        right = min(
            self.n_space,
            center + width,
        )

        mask[left:right] *= 0.75

        return mask

    # -----------------------------------
    # DETECTOR TOPOLOGY
    # -----------------------------------

    def detector_topology(
        self,
        step,
    ):

        detectors = [

            {
                "center":
                    120
                    + int(
                        20
                        * np.sin(
                            step / 18
                        )
                    ),

                "width": 25,

                "strength": 0.65,
            },

            {
                "center":
                    260
                    + int(
                        30
                        * np.sin(
                            step / 25
                        )
                    ),

                "width": 40,

                "strength": 0.55,
            },

            {
                "center":
                    390
                    + int(
                        15
                        * np.sin(
                            step / 12
                        )
                    ),

                "width": 20,

                "strength": 0.75,
            },
        ]

        return detectors

    # -----------------------------------
    # MULTI-DETECTOR COUPLING
    # -----------------------------------

    def detector_coupling_mask(
        self,
        step,
    ):

        mask = np.ones(
            self.n_space
        )

        detectors = (
            self.detector_topology(
                step
            )
        )

        for detector in detectors:

            center = detector[
                "center"
            ]

            width = detector[
                "width"
            ]

            strength = detector[
                "strength"
            ]

            left = max(
                0,
                center - width,
            )

            right = min(
                self.n_space,
                center + width,
            )

            mask[left:right] *= (
                strength
            )

        return mask

    # -----------------------------------
    # FIDELITY METRIC
    # -----------------------------------

    def fidelity_metric(
        self,
        field,
        detector_loss,
        env_loss,
        noise,
    ):

        coherence = np.std(field)

        denominator = (
            coherence
            + detector_loss
            + env_loss
            + noise
            + 1e-8
        )

        fidelity = (
            coherence
            / denominator
        )

        fidelity = np.clip(
            fidelity,
            0.0,
            1.0,
        )

        return (
            coherence,
            fidelity,
        )

    # -----------------------------------
    # EVOLUTION STEP
    # -----------------------------------

    def evolve_step(
        self,
        field,
        step,
    ):

        evolved = np.roll(
            field,
            self.transport_velocity,
        )

        evolved *= (
            self.coherence_decay
        )

        env_mask = (
            self.decoherence_mask(
                step
            )
        )

        detector_mask = (
            self.detector_coupling_mask(
                step
            )
        )

        evolved *= env_mask

        evolved *= detector_mask

        noise = np.random.normal(
            0,
            self.noise_strength,
            evolved.shape,
        )

        evolved += noise

        detector_loss = (
            1.0
            - np.mean(
                detector_mask
            )
        )

        env_loss = (
            1.0
            - np.mean(
                env_mask
            )
        )

        noise_level = np.std(noise)

        coherence, fidelity = (
            self.fidelity_metric(
                evolved,
                detector_loss,
                env_loss,
                noise_level,
            )
        )

        diagnostics = {
            "coherence":
                coherence,

            "detector_loss":
                detector_loss,

            "environmental_loss":
                env_loss,

            "noise":
                noise_level,

            "fidelity":
                fidelity,
        }

        return (
            evolved,
            diagnostics,
        )

    # -----------------------------------
    # FULL EVOLUTION
    # -----------------------------------

    def evolve(self):

        field = (
            self.initialize_field()
        )

        history = []

        tensor = []

        for step in range(
            self.n_time
        ):

            history.append(
                field.copy()
            )

            field, diagnostics = (
                self.evolve_step(
                    field,
                    step,
                )
            )

            tensor.append(
                diagnostics
            )

        return (
            np.array(history),
            tensor,
        )
