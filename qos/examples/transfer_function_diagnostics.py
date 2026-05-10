"""Executable coherence transfer-function diagnostics example."""

from __future__ import annotations

import json

from qos.acquisition import (
    AcquisitionPolicy,
    CanonicalAcquisitionRuntime,
    DetectorBandwidthLimit,
    SpatialMeasurementDecoherence,
)
from qos.diagnostics import CanonicalDiagnosticsRuntime
from qos.foundation import ImprintFoundationRuntime
from qos.measurement import DetectorPlaneMeasurementRuntime
from qos.runtime.orchestrator import RuntimeOrchestrator, _json_safe, runtime_execution_digest


def main() -> None:
    execution = RuntimeOrchestrator(
        foundation=ImprintFoundationRuntime(synthetic_shape=(3, 16)),
        measurement=DetectorPlaneMeasurementRuntime.preserving(),
        acquisition=CanonicalAcquisitionRuntime(
            AcquisitionPolicy(
                policy_id="transfer-function-diagnostics-example",
                sampling_rate_hz=120_000.0,
                bit_depth=16,
                bandwidth_limit=DetectorBandwidthLimit(
                    bandwidth_hz=48_000.0,
                    nominal_signal_bandwidth_hz=60_000.0,
                ),
                spatial_decoherence=SpatialMeasurementDecoherence(
                    sigma_radians=0.35,
                    correlation_length_pixels=8.0,
                ),
            )
        ),
        diagnostics=CanonicalDiagnosticsRuntime(),
    ).run(run_id="example-transfer-function-diagnostics")
    print(json.dumps(_json_safe(execution.diagnostic_report), indent=2, sort_keys=True))
    print("digest=" + runtime_execution_digest(execution))


if __name__ == "__main__":
    main()
