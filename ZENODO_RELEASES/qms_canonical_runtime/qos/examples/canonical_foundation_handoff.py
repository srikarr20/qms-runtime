"""Minimal executable example for canonical foundation handoff objects."""

from __future__ import annotations

import json

from qos.foundation import ImprintFoundationRuntime
from qos.runtime.orchestrator import RuntimeOrchestrator, _json_safe, runtime_execution_digest


def main() -> None:
    foundation = ImprintFoundationRuntime(synthetic_shape=(3, 8))
    execution = RuntimeOrchestrator(foundation=foundation).run(run_id="example-foundation")
    print(json.dumps(_json_safe(execution.imprint_field_state), indent=2, sort_keys=True))
    print("digest=" + runtime_execution_digest(execution))


if __name__ == "__main__":
    main()
