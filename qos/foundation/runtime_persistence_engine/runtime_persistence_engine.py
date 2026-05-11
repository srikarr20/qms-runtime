from pathlib import Path
import json
import numpy as np


class RuntimePersistenceEngine:

    def __init__(self):

        self.base_dir = Path(
            "qos/artifacts/runtime_snapshots"
        )

        self.base_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    # =====================================================
    # SAVE SNAPSHOT
    # =====================================================

    def save_snapshot(
        self,
        name,
        field_history,
        runtime_tensor,
    ):

        snapshot_dir = (
            self.base_dir / name
        )

        snapshot_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        np.save(
            snapshot_dir / "field_history.npy",
            np.array(field_history),
        )

        with open(
            snapshot_dir / "runtime_tensor.json",
            "w",
        ) as f:

            json.dump(
                runtime_tensor,
                f,
                indent=4,
            )

        metadata = {

            "snapshot_name":
                name,

            "runtime_steps":
                len(field_history),

            "field_shape":
                list(
                    np.array(field_history).shape
                ),
        }

        with open(
            snapshot_dir / "metadata.json",
            "w",
        ) as f:

            json.dump(
                metadata,
                f,
                indent=4,
            )

        return snapshot_dir

    # =====================================================
    # LOAD SNAPSHOT
    # =====================================================

    def load_snapshot(
        self,
        name,
    ):

        snapshot_dir = (
            self.base_dir / name
        )

        field_history = np.load(
            snapshot_dir / "field_history.npy"
        )

        with open(
            snapshot_dir / "runtime_tensor.json"
        ) as f:

            runtime_tensor = json.load(f)

        with open(
            snapshot_dir / "metadata.json"
        ) as f:

            metadata = json.load(f)

        return (
            field_history,
            runtime_tensor,
            metadata,
        )

    # =====================================================
    # LIST SNAPSHOTS
    # =====================================================

    def list_snapshots(self):

        snapshots = []

        for p in self.base_dir.iterdir():

            if p.is_dir():

                snapshots.append(p.name)

        return sorted(snapshots)
