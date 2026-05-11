"""Load recovered field_data.pkl into a canonical ImprintFieldState."""

from __future__ import annotations

import json
from pathlib import Path

from qos.foundation import ImprintFoundationRuntime
from qos.runtime.orchestrator import _json_safe


LEGACY_FIELD_DATA = Path("Foundations/ImprintField/ImprintFieldOutputs/field_data.pkl")


def main() -> None:
    state = ImprintFoundationRuntime(legacy_field_data_path=LEGACY_FIELD_DATA).run(
        "legacy-field-data",
        {"example": "legacy_field_data_handoff"},
    )
    print(json.dumps(_json_safe(state), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
