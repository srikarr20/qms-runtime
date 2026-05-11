import numpy as np


class DetectorNetworkFieldEngine:

    def __init__(
        self,
        n_space=512,
        n_time=240,
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

        self.detectors = [

            {
                "center": 100,
                "width": 25,
                "state": 0.5,
            },

            {
                "center": 260,
                "width": 35,
                "state": 0.5,
            },

            {
                "center": 390,
                "width": 20,
                "state": 0.5,
            },
        ]

    # ========================================================
    # INITIAL FIELD
    # ========================================================

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

    # ========================================================
    # ENVIRONMENTAL DECOHERENCE
    # ========================================================

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
                50
                * np.sin(
                    step / 20
                )
            )
        )

        width = 60

        left = max(
            0,
            center - width,
        )

        right = min(
            self.n_space,
            center + width,
        )

        mask[left:right] *= 0.8

        return mask

    # ========================================================
    # NETWORK UPDATE
    # ========================================================

    def update_detector_network(
        self,
        field,
    ):

        detector_states = []

        for i, detector in enumerate(
            self.detectors
        ):

            center = detector[
                "center"
            ]

            width = detector[
                "width"
            ]

            left = max(
                0,
                center - width,
            )

            right = min(
                self.n_space,
                center + width,
            )

            local_field = field[
                left:right
            ]

            coherence = np.std(
                local_field
            )

            local_response = (
                1.0
                - np.clip(
                    coherence,
                    0.0,
                    0.9,
                )
            )

            neighbor_states = []

            if i > 0:

                neighbor_states.append(
                    self.detectors[
                        i - 1
                    ]["state"]
                )

            if i < len(
                self.detectors
            ) - 1:

                neighbor_states.append(
                    self.detectors[
                        i + 1
                    ]["state"]
                )

            if len(
                neighbor_states
            ) > 0:

                neighbor_influence = (
                    np.mean(
                        neighbor_states
                    )
                )

            else:

                neighbor_influence = (
                    detector["state"]
                )

            updated_state = (
                0.6
                * local_response
                + 0.4
                * neighbor_influence
            )

            updated_state = np.clip(
                updated_state,
                0.1,
                1.0,
            )

            detector["state"] = (
                updated_state
            )

            detector_states.append(
                updated_state
            )

        return detector_states

    # ========================================================
    # DETECTOR MASK
    # ========================================================

    def detector_mask(self):

        mask = np.ones(
            self.n_space
        )

        for detector in self.detectors:

            center = detector[
                "center"
            ]

            width = detector[
                "width"
            ]

            state = detector[
                "state"
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
                state
            )

        return mask

    # ========================================================
    # FIDELITY
    # ========================================================

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

    # ========================================================
    # STEP
    # ========================================================

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

        evolved *= env_mask

        detector_states = (
            self.update_detector_network(
                evolved
            )
        )

        detector_mask = (
            self.detector_mask()
        )

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

            "fidelity":
                fidelity,

            "detector_loss":
                detector_loss,

            "environmental_loss":
                env_loss,

            "noise":
                noise_level,

            "detector_states":
                detector_states,
        }

        return (
            evolved,
            diagnostics,
        )

    # ========================================================
    # FULL EVOLUTION
    # ========================================================

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
