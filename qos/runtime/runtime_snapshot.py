import json
import numpy as np

from pathlib import Path
from datetime import datetime


class RuntimeSnapshot:

    @staticmethod
    def save(

        field_history,

        runtime_tensor,

    ):

        base_dir = Path(
            "qos/artifacts/runtime_snapshots"
        )

        base_dir.mkdir(

            parents=True,

            exist_ok=True,

        )

        timestamp = datetime.utcnow().strftime(
            "%Y%m%d_%H%M%S"
        )

        snapshot_name = (
            f"runtime_snapshot_{timestamp}"
        )

        snapshot_dir = (
            base_dir
            / snapshot_name
        )

        snapshot_dir.mkdir(

            parents=True,

            exist_ok=True,

        )

        # ==================================================
        # SAVE FIELD HISTORY
        # ==================================================

        np.save(

            snapshot_dir
            / "field_history.npy",

            field_history,

        )

        # ==================================================
        # SAVE RUNTIME TENSOR
        # ==================================================

        with open(

            snapshot_dir
            / "runtime_tensor.json",

            "w",

        ) as f:

            json.dump(

                runtime_tensor,

                f,

                indent=4,

            )

        # ==================================================
        # METADATA
        # ==================================================

        metadata = {

            "snapshot_name":
                snapshot_name,

            "runtime_steps":
                len(runtime_tensor),

            "field_shape":
                list(
                    field_history.shape
                ),

        }

        with open(

            snapshot_dir
            / "metadata.json",

            "w",

        ) as f:

            json.dump(

                metadata,

                f,

                indent=4,

            )

        print(
            "\n=== Runtime Snapshot Saved ==="
        )

        print(snapshot_dir)

        return snapshot_name

    # ======================================================
    # LOAD
    # ======================================================

    @staticmethod
    def load(

        snapshot_name,

    ):

        base_dir = Path(
            "qos/artifacts/runtime_snapshots"
        )

        snapshot_dir = (
            base_dir
            / snapshot_name
        )

        if not snapshot_dir.exists():

            raise FileNotFoundError(

                f"Snapshot not found: {snapshot_name}"

            )

        field_history = np.load(

            snapshot_dir
            / "field_history.npy"

        )

        with open(

            snapshot_dir
            / "runtime_tensor.json"

        ) as f:

            runtime_tensor = json.load(f)

        with open(

            snapshot_dir
            / "metadata.json"

        ) as f:

            metadata = json.load(f)

        return {

            "field_history":
                field_history,

            "runtime_tensor":
                runtime_tensor,

            "metadata":
                metadata,

        }
