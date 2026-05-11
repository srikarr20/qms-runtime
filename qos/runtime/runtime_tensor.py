from dataclasses import dataclass, asdict


@dataclass
class RuntimeTensor:

    runtime_step: int

    coherence: float

    fidelity: float

    noise: float

    detector_loss: float

    environmental_loss: float

    detector_states: list

    memory_states: list

    scheduler_windows: list

    scheduler_latency: list

    topology_state: dict

    metadata: dict

    # ======================================================
    # EXPORT
    # ======================================================

    def to_dict(self):

        return asdict(self)
