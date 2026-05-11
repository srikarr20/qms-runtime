"""
Detector-plane operational validation
"""

from qos.runtime.orchestrator import RuntimeOrchestrator


def run_case(label):

    print(f"\n=== {label} ===")

    orchestrator = RuntimeOrchestrator()

    result = orchestrator.run()

    # ---------------------------------
    # Full runtime object
    # ---------------------------------
    print("\nExecution Object:")
    print(result)

    # ---------------------------------
    # Canonical diagnostics handoff
    # ---------------------------------
    print("\nDiagnostic Report:")
    print(result.diagnostic_report)

    # ---------------------------------
    # Canonical control handoff
    # ---------------------------------
    print("\nControl Decision:")
    print(result.control_decision)


def main():

    run_case("Canonical Runtime Validation")


if __name__ == "__main__":
    main()
