from pathlib import Path

import json
import numpy as np


class PersistenceRuntime:

    def __init__(self):

        self.base_dir = Path(

            "qos/artifacts/runtime_snapshots"

        )

        self.base_dir.mkdir(

            parents=True,

            exist_ok=True,

        )

    # ======================================================
    # SAVE
    # ======================================================

    def save(

        self,

        snapshot_name,

        field_history,

        runtime_tensor,

    ):

        snapshot_dir = (
            self.base_dir / snapshot_name
        )

        snapshot_dir.mkdir(

            parents=True,

            exist_ok=True,

        )

        np.save(

            snapshot_dir
            / "field_history.npy",

            np.array(field_history),

        )

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

        return snapshot_dir
