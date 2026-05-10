"""Executable coherence-destroying detector-plane example."""

from __future__ import annotations

import json

from qos.foundation import ImprintFoundationRuntime
from qos.measurement import DetectorPlaneMeasurementRuntime
from qos.runtime.orchestrator import RuntimeOrchestrator, _json_safe, runtime_execution_digest


def main() -> None:
    execution = RuntimeOrchestrator(
        foundation=ImprintFoundationRuntime(synthetic_shape=(3, 8)),
        measurement=DetectorPlaneMeasurementRuntime.destroying(),
    ).run(run_id="example-detector-destroy")
    print(json.dumps(_json_safe(execution.detector_signal), indent=2, sort_keys=True))
    print("digest=" + runtime_execution_digest(execution))


if __name__ == "__main__":
    main()
