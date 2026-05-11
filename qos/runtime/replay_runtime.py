import json
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path
from datetime import datetime


class ReplayRuntime:

    def __init__(
        self,
        snapshot_name,
    ):

        self.snapshot_name = (
            snapshot_name
        )

        self.base_dir = Path(
            "qos/artifacts/runtime_snapshots"
        )

        self.snapshot_dir = (
            self.base_dir
            / snapshot_name
        )

        if not self.snapshot_dir.exists():

            raise FileNotFoundError(
                f"Snapshot not found: {snapshot_name}"
            )

        self.field_history = np.load(
            self.snapshot_dir
            / "field_history.npy"
        )

        with open(
            self.snapshot_dir
            / "runtime_tensor.json"
        ) as f:

            self.runtime_tensor = json.load(f)

    # ======================================================
    # METADATA
    # ======================================================

    def metadata(self):

        return {

            "snapshot_name":
                self.snapshot_name,

            "runtime_steps":
                len(
                    self.field_history
                ),

            "field_shape":
                list(
                    self.field_history.shape
                ),

        }

    # ======================================================
    # SAFE MEMORY STATES
    # ======================================================

    def safe_memory_states(self):

        memory_states = []

        for x in self.runtime_tensor:

            if "memory_states" in x:

                memory_states.append(
                    x["memory_states"]
                )

            elif "detector_memories" in x:

                memory_states.append(
                    x["detector_memories"]
                )

            else:

                detector_count = len(
                    x["detector_states"]
                )

                memory_states.append(
                    [0.0]
                    * detector_count
                )

        return np.array(
            memory_states
        )

    # ======================================================
    # BUILD FIGURE
    # ======================================================

    def build_figure(self):

        fig, axes = plt.subplots(
            4,
            1,
            figsize=(14, 18),
        )

        # ==================================================
        # PANEL 1
        # ==================================================

        im = axes[0].imshow(
            self.field_history,
            aspect="auto",
            origin="lower",
        )

        axes[0].set_title(
            "Replay Field Runtime"
        )

        axes[0].set_xlabel(
            "Spatial Coordinate"
        )

        axes[0].set_ylabel(
            "Runtime Step"
        )

        fig.colorbar(
            im,
            ax=axes[0],
            label="Field Amplitude",
        )

        # ==================================================
        # PANEL 2
        # ==================================================

        fidelity = [
            x["fidelity"]
            for x in self.runtime_tensor
        ]

        coherence = [
            x["coherence"]
            for x in self.runtime_tensor
        ]

        axes[1].plot(
            fidelity,
            linewidth=2,
            label="Fidelity",
        )

        axes[1].plot(
            coherence,
            linewidth=2,
            label="Coherence",
        )

        axes[1].legend()

        axes[1].grid(True)

        axes[1].set_title(
            "Replay Runtime Tensor"
        )

        # ==================================================
        # PANEL 3
        # ==================================================

        detector_states = np.array(
            [
                x["detector_states"]
                for x in self.runtime_tensor
            ]
        )

        for i in range(
            detector_states.shape[1]
        ):

            axes[2].plot(
                detector_states[:, i],
                linewidth=2,
                label=f"Detector {i+1}",
            )

        axes[2].legend()

        axes[2].grid(True)

        axes[2].set_title(
            "Replay Detector States"
        )

        # ==================================================
        # PANEL 4
        # ==================================================

        memory_states = (
            self.safe_memory_states()
        )

        for i in range(
            memory_states.shape[1]
        ):

            axes[3].plot(
                memory_states[:, i],
                linewidth=2,
                label=f"Memory {i+1}",
            )

        axes[3].legend()

        axes[3].grid(True)

        axes[3].set_title(
            "Replay Memory Tensor"
        )

        plt.tight_layout()

        return fig

    # ======================================================
    # REPLAY
    # ======================================================

    def replay(self):

        fig = self.build_figure()

        plt.show()

    # ======================================================
    # EXPORT
    # ======================================================

    def export(self):

        export_dir = Path(
            "qos/artifacts/replays"
        )

        export_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        timestamp = datetime.utcnow().strftime(
            "%Y%m%d_%H%M%S"
        )

        replay_dir = (
            export_dir
            / f"replay_{timestamp}"
        )

        replay_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        fig = self.build_figure()

        fig.savefig(
            replay_dir
            / "replay.png",
            dpi=300,
        )

        with open(
            replay_dir
            / "replay_metadata.json",
            "w",
        ) as f:

            json.dump(
                self.metadata(),
                f,
                indent=4,
            )

        with open(
            replay_dir
            / "replay_tensor.json",
            "w",
        ) as f:

            json.dump(
                self.runtime_tensor,
                f,
                indent=4,
            )

        print(
            "\n=== Replay Exported ==="
        )

        print(replay_dir)
