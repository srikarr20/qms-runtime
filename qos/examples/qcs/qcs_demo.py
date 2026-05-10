from qos.control.runtime.qcs_runtime import (
    CanonicalQCSRuntime,
)

from qos.contracts.handoffs import (
    DiagnosticReport,
)


runtime = CanonicalQCSRuntime()

# ---------------------------------
# Canonical DiagnosticReport
# ---------------------------------
report = DiagnosticReport(
    report_id="diag-demo-001",
    source_record_id="record-demo-001",
    metrics={
        "visibility": 0.42,
        "observability_index": 0.33,
    },
)

# ---------------------------------
# Process diagnostics
# ---------------------------------
decision = runtime.process(report)

print("\n=== QCS Decision ===")
print(decision)
