import numpy as np


class TopologyRuntime:

    def __init__(

        self,

        topology="ring",

        detector_count=8,

    ):

        self.topology = topology

        self.detector_count = detector_count

        self.coupling_strength = 0.12

        self.global_decay = 0.985

        self.local_damping = 0.95

        self.adaptation_rate = 0.002

        self.matrix = self.build_topology()

    # ======================================================
    # BUILD TOPOLOGY
    # ======================================================

    def build_topology(self):

        n = self.detector_count

        matrix = np.zeros((n, n))

        # ==================================================
        # RING
        # ==================================================

        if self.topology == "ring":

            for i in range(n):

                matrix[i, (i - 1) % n] = 1
                matrix[i, (i + 1) % n] = 1

        # ==================================================
        # LINE
        # ==================================================

        elif self.topology == "line":

            for i in range(n - 1):

                matrix[i, i + 1] = 1
                matrix[i + 1, i] = 1

        # ==================================================
        # FULLY CONNECTED
        # ==================================================

        elif self.topology == "fully_connected":

            matrix[:] = 1

            np.fill_diagonal(
                matrix,
                0,
            )

        # ==================================================
        # RANDOM
        # ==================================================

        else:

            np.random.seed(42)

            for i in range(n):

                for j in range(i + 1, n):

                    if np.random.rand() > 0.7:

                        matrix[i, j] = 1
                        matrix[j, i] = 1

        return matrix.astype(float)

    # ======================================================
    # PULSE INJECTION
    # ======================================================

    def inject_pulse(

        self,

        states,

        location=0,

        amplitude=1.0,

    ):

        states = np.array(
            states,
            dtype=float,
        )

        states[location] += amplitude

        return states

    # ======================================================
    # ADAPTIVE TOPOLOGY EVOLUTION
    # ======================================================

    def adapt_topology(

        self,

        states,

    ):

        n = self.detector_count

        for i in range(n):

            for j in range(n):

                if i == j:
                    continue

                similarity = (

                    1.0
                    -
                    abs(
                        states[i]
                        -
                        states[j]
                    )

                )

                self.matrix[i, j] += (

                    self.adaptation_rate
                    * similarity

                )

        # ==============================================
        # NORMALIZATION
        # ==============================================

        self.matrix = np.clip(

            self.matrix,

            0.0,

            2.0,

        )

    # ======================================================
    # PROPAGATION
    # ======================================================

    def propagate(

        self,

        states,

    ):

        states = np.array(
            states,
            dtype=float,
        )

        # ==============================================
        # TOPOLOGY ADAPTATION
        # ==============================================

        self.adapt_topology(
            states
        )

        incoming = (
            self.matrix @ states
        )

        updated = (

            states
            * self.global_decay

            +

            incoming
            * self.coupling_strength

        )

        updated *= self.local_damping

        updated = np.clip(

            updated,

            -1e6,

            1e6,

        )

        return updated

    # ======================================================
    # METRICS
    # ======================================================

    def metrics(self):

        connectivity = np.sum(
            self.matrix,
            axis=1,
        )

        return {

            "topology":
            self.topology,

            "detector_count":
            self.detector_count,

            "average_connectivity":
            float(
                np.mean(connectivity)
            ),

            "topology_entropy":
            float(
                np.var(connectivity)
            ),

            "adaptive_connectivity":
            float(
                np.mean(self.matrix)
            ),

        }
