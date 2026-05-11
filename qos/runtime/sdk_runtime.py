from dataclasses import dataclass

from qos.runtime.orchestrator import (
    RuntimeOrchestrator,
)


@dataclass
class SDKExecutionSummary:
    run_id: str
    detector_model: str
    visibility: float
    observability: float
    control_action: str

    def __repr__(self) -> str:
        return (
            f"<QMS SDKExecution "
            f"run_id={self.run_id} "
            f"visibility={self.visibility} "
            f"observability={self.observability} "
            f"action={self.control_action}>"
        )

    def summary(self) -> str:
        return (
            "\n=== QMS SDK Execution ===\n"
            f"Run ID: {self.run_id}\n"
            f"Detector Model: {self.detector_model}\n"
            f"Visibility: {self.visibility}\n"
            f"Observability: {self.observability}\n"
            f"Control Action: {self.control_action}\n"
        )


class SDKRuntime:
    """
    Developer-friendly QMS SDK runtime facade.

    Wraps the canonical RuntimeOrchestrator
    while exposing simplified summaries.
    """

    def __init__(self):
        self.runtime = RuntimeOrchestrator()

    def run(self):

        execution = self.runtime.run()

        visibility = (
            execution.diagnostic_report.metrics
            .get("visibility", {})
            .get("visibility_index", 0.0)
        )

        observability = (
            execution.diagnostic_report.metrics
            .get("observability", {})
            .get("observability_index", 0.0)
        )

        return SDKExecutionSummary(
            run_id=execution.provenance.run_id[:8],
            detector_model=execution.detector_signal.detector_model,
            visibility=visibility,
            observability=observability,
            control_action=execution.control_decision.action,
        )
