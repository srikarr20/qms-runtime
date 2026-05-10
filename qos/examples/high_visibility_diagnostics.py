"""Executable high-visibility diagnostics example."""

from __future__ import annotations

import json

from qos.acquisition import CanonicalAcquisitionRuntime
from qos.diagnostics import CanonicalDiagnosticsRuntime
from qos.foundation import ImprintFoundationRuntime
from qos.measurement import DetectorPlaneMeasurementRuntime
from qos.runtime.orchestrator import RuntimeOrchestrator, _json_safe, runtime_execution_digest


def main() -> None:
    execution = RuntimeOrchestrator(
        foundation=ImprintFoundationRuntime(synthetic_shape=(3, 16)),
        measurement=DetectorPlaneMeasurementRuntime.preserving(),
        acquisition=CanonicalAcquisitionRuntime.high_bandwidth(),
        diagnostics=CanonicalDiagnosticsRuntime(),
    ).run(run_id="example-high-visibility-diagnostics")
    print(json.dumps(_json_safe(execution.diagnostic_report), indent=2, sort_keys=True))
    print("digest=" + runtime_execution_digest(execution))


if __name__ == "__main__":
    main()
