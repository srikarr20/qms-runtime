# Control Layer

Owns QCS policy decisions, run budgets, scheduling, retry, abort, recalibration,
and future-run orchestration.

Input: `DiagnosticReport`.

Output: `ControlDecision`.

Control must not alter raw data, detector output, acquisition records, or
diagnostic results. All actions apply only to future runs.

