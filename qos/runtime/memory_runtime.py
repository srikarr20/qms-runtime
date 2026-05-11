class MemoryRuntime:

    def __init__(self):

        self.history = []

    # ======================================================
    # UPDATE
    # ======================================================

    def update(

        self,

        detector_states,

    ):

        self.history.append(

            detector_states.copy()

        )

    # ======================================================
    # EXPORT
    # ======================================================

    def tensor(self):

        return self.history
