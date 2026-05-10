"""Executable low-bandwidth canonical acquisition example."""

from __future__ import annotations

import json

from qos.acquisition import CanonicalAcquisitionRuntime
from qos.foundation import ImprintFoundationRuntime
from qos.measurement import DetectorPlaneMeasurementRuntime
from qos.runtime.orchestrator import RuntimeOrchestrator, _json_safe, runtime_execution_digest


def main() -> None:
    execution = RuntimeOrchestrator(
        foundation=ImprintFoundationRuntime(synthetic_shape=(3, 16)),
        measurement=DetectorPlaneMeasurementRuntime.preserving(),
        acquisition=CanonicalAcquisitionRuntime.low_bandwidth(),
    ).run(run_id="example-low-bandwidth-acquisition")
    print(json.dumps(_json_safe(execution.digital_record), indent=2, sort_keys=True))
    print("digest=" + runtime_execution_digest(execution))


if __name__ == "__main__":
    main()

