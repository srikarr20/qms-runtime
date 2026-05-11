"""Canonical QOS runtime orchestrator.

This module composes the Quantum Measurement Stack in the only causal order
allowed at runtime:

foundation -> measurement -> acquisition -> diagnostics -> control

The orchestrator is deliberately thin. Layer implementations are pluggable
objects with small public methods, while immutable handoff objects from
``qos.contracts`` are the only payloads that cross layer boundaries.
"""

from __future__ import annotations

import ast
import hashlib
import json
import platform
import sys
import uuid
from dataclasses import asdict, dataclass, field, fields, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping, Optional, Protocol, Sequence, Tuple, Type

from qos.contracts import (
    ControlDecision,
    DetectorSignal,
    DiagnosticReport,
    DigitalRecord,
    ImprintFieldState,
)
from qos.acquisition import AcquisitionPolicy, CanonicalAcquisitionRuntime
from qos.diagnostics import CanonicalDiagnosticsRuntime
from qos.foundation import ImprintFoundationRuntime
from qos.measurement.detector_plane import DetectorPlaneMeasurementRuntime

CAUSAL_CHAIN: Tuple[str, ...] = (
    "foundation",
    "measurement",
    "acquisition",
    "diagnostics",
    "control",
)

HANDOFF_CHAIN: Tuple[Type[object], ...] = (
    ImprintFieldState,
    DetectorSignal,
    DigitalRecord,
    DiagnosticReport,
    ControlDecision,
)

FROZEN_BENCHMARK_ROOT = Path("qos/benchmarks/frozen")
EXPERIMENTAL_ORCHESTRATION_ROOTS: Tuple[Path, ...] = (
    Path("qos/experiments"),
    Path("qos/control/adaptive_orchestration/experimental"),
)
RUNTIME_ARTIFACT_ROOT = Path("qos/artifacts/generated/runtime")
PUBLICATION_ROOTS: Tuple[Path, ...] = (
    Path("Papers-Core"),
    Path("Releases"),
    Path("qos/artifacts/releases"),
)

COMPATIBILITY_TARGETS: Tuple[str, ...] = (
    "QMCTB-01",
    "QMCTB-02",
    "QMCTB-03",
    "v257 adaptive orchestration systems",
)

PROHIBITED_DIAGNOSTIC_RECONSTRUCTION_KEYS = frozenset(
    {
        "field",
        "field_state",
        "imprint_field_state",
        "raw_field",
        "reconstructed_field",
        "detector_signal",
        "destroyed_correlations",
    }
)


class FoundationRuntime(Protocol):
    """Public foundation API: emit a pre-measurement field state."""

    def run(self, run_id: str, provenance: Mapping[str, Any]) -> ImprintFieldState:
        """Create the foundation handoff for a run."""


class MeasurementRuntime(Protocol):
    """Public measurement API: consume field state and emit detector signal."""

    def measure(
        self, state: ImprintFieldState, provenance: Mapping[str, Any]
    ) -> DetectorSignal:
        """Apply detector-plane measurement semantics."""


class AcquisitionRuntime(Protocol):
    """Public acquisition API: consume detector signal and emit digital record."""

    def acquire(
        self, signal: DetectorSignal, provenance: Mapping[str, Any]
    ) -> DigitalRecord:
        """Digitize and store the detector signal."""


class DiagnosticsRuntime(Protocol):
    """Public diagnostics API: consume digital record and emit diagnostics."""

    def diagnose(
        self, record: DigitalRecord, provenance: Mapping[str, Any]
    ) -> DiagnosticReport:
        """Evaluate record-level metrics without upstream reconstruction."""


class ControlRuntime(Protocol):
    """Public control API: consume diagnostics and emit future-run decisions."""

    def decide(
        self, report: DiagnosticReport, provenance: Mapping[str, Any]
    ) -> ControlDecision:
        """Choose control actions that apply only to later runs."""


@dataclass(frozen=True)
class RuntimeProvenance:
    """Execution metadata attached to every runtime handoff."""

    run_id: str
    started_at_utc: str
    orchestrator: str = "qos.runtime.orchestrator"
    causal_chain: Tuple[str, ...] = CAUSAL_CHAIN
    handoff_chain: Tuple[str, ...] = tuple(cls.__name__ for cls in HANDOFF_CHAIN)
    compatibility_targets: Tuple[str, ...] = COMPATIBILITY_TARGETS
    python: str = platform.python_version()
    platform: str = platform.platform()

    def as_metadata(self) -> Mapping[str, Any]:
        """Return a JSON-safe immutable provenance view."""
        return asdict(self)


@dataclass(frozen=True)
class RuntimeLayout:
    """Canonical separation between source, experiments, artifacts, and papers."""

    frozen_benchmarks: Path = FROZEN_BENCHMARK_ROOT
    experimental_orchestration: Tuple[Path, ...] = EXPERIMENTAL_ORCHESTRATION_ROOTS
    runtime_artifacts: Path = RUNTIME_ARTIFACT_ROOT
    publications: Tuple[Path, ...] = PUBLICATION_ROOTS


@dataclass(frozen=True)
class RuntimeExecution:
    """Auditable output bundle for one canonical runtime execution."""

    provenance: RuntimeProvenance
    layout: RuntimeLayout
    imprint_field_state: ImprintFieldState
    detector_signal: DetectorSignal
    digital_record: DigitalRecord
    diagnostic_report: DiagnosticReport
    control_decision: ControlDecision


@dataclass(frozen=True)
class MinimalFoundationRuntime:
    """Compatibility alias for the canonical Imprint foundation runtime."""

    shape: Tuple[int, ...] = (1,)
    coordinates: Mapping[str, Any] = field(default_factory=lambda: {"basis": "canonical"})
    parameters: Mapping[str, Any] = field(default_factory=lambda: {"model": "minimal-imprint"})

    def run(self, run_id: str, provenance: Mapping[str, Any]) -> ImprintFieldState:
        time_steps = int(self.shape[0]) if len(self.shape) == 2 else 4
        size = int(self.shape[-1]) if self.shape else 16
        return ImprintFoundationRuntime(
            synthetic_shape=(max(time_steps, 2), max(size, 2)),
            parameters={
                **dict(self.parameters),
                "compatibility_alias": "MinimalFoundationRuntime",
                "legacy_coordinates": dict(self.coordinates),
            },
        ).run(run_id, provenance)


@dataclass(frozen=True)
class MinimalAcquisitionRuntime:
    """Compatibility alias for canonical acquisition."""

    sampling_rate_hz: float = 1.0
    bit_depth: int = 16
    transforms: Tuple[str, ...] = ("sample", "quantize", "record")

    def acquire(
        self, signal: DetectorSignal, provenance: Mapping[str, Any]
    ) -> DigitalRecord:
        return CanonicalAcquisitionRuntime(
            AcquisitionPolicy(
                policy_id="minimal-acquisition-compatibility",
                sampling_rate_hz=self.sampling_rate_hz,
                bit_depth=self.bit_depth,
            )
        ).acquire(signal, provenance)


@dataclass(frozen=True)
class MinimalDiagnosticsRuntime:
    """Executable diagnostics stub that cannot inspect destroyed information."""

    def diagnose(
        self, record: DigitalRecord, provenance: Mapping[str, Any]
    ) -> DiagnosticReport:
        irreversible_loss = bool(record.metadata.get("irreversible_loss_inherited", True))
        return DiagnosticReport(
            report_id=f"diag-{record.record_id}",
            source_record_id=record.record_id,
            metrics={
                "record_shape": record.shape,
                "sampling_rate_hz": record.sampling_rate_hz,
                "bit_depth": record.bit_depth,
                "observed_transform_count": len(record.transforms),
            },
            confidence={
                "record_level_only": True,
                "upstream_irreversibility_respected": irreversible_loss,
            },
            limitations=(
                "diagnostics consume DigitalRecord only",
                "destroyed upstream correlations are unavailable and unreconstructed",
            ),
            metadata={"provenance": provenance},
        )


@dataclass(frozen=True)
class QCSControlRuntime:
    """Executable QCS control stub constrained to future-run effects."""

    default_action: str = "continue"

    def decide(
        self, report: DiagnosticReport, provenance: Mapping[str, Any]
    ) -> ControlDecision:
        return ControlDecision(
            decision_id=f"qcs-{report.report_id}",
            source_report_id=report.report_id,
            action=self.default_action,
            applies_to_future_run=True,
            parameters={
                "future_run_only": True,
                "adaptive_detector_policies": "extension-point",
                "coherence_transfer_functions": "extension-point",
                "detector_bandwidth_observability": "extension-point",
                "controlled_decoherence": "extension-point",
                "distributed_detector_topology": "extension-point",
            },
            rationale="Minimal QCS stub preserves records and affects only future executions.",
            metadata={"provenance": provenance},
        )


@dataclass(frozen=True)
class RuntimeOrchestrator:
    """Canonical runtime coordinator for the QOS causal chain."""

    foundation: FoundationRuntime = field(default_factory=ImprintFoundationRuntime)
    measurement: MeasurementRuntime = field(default_factory=DetectorPlaneMeasurementRuntime)
    acquisition: AcquisitionRuntime = field(default_factory=CanonicalAcquisitionRuntime)
    diagnostics: DiagnosticsRuntime = field(default_factory=CanonicalDiagnosticsRuntime)
    control: ControlRuntime = field(default_factory=QCSControlRuntime)
    layout: RuntimeLayout = field(default_factory=RuntimeLayout)

    def run(self, run_id: Optional[str] = None) -> RuntimeExecution:
        """Execute the canonical handoff chain once."""
        provenance = RuntimeProvenance(
            run_id=run_id or uuid.uuid4().hex,
            started_at_utc=datetime.now(timezone.utc).isoformat(),
        )
        metadata = provenance.as_metadata()

        assert_causal_import_boundaries()

        state = self.foundation.run(provenance.run_id, metadata)
        self._require_handoff(state, ImprintFieldState, "foundation")

        signal = self.measurement.measure(state, metadata)
        self._require_handoff(signal, DetectorSignal, "measurement")
        self._require_detector_irreversibility(signal)

        record = self.acquisition.acquire(signal, metadata)
        self._require_handoff(record, DigitalRecord, "acquisition")

        report = self.diagnostics.diagnose(record, metadata)
        self._require_handoff(report, DiagnosticReport, "diagnostics")
        self._require_no_diagnostic_reconstruction(report)

        decision = self.control.decide(report, metadata)
        self._require_handoff(decision, ControlDecision, "control")
        self._require_future_only_control(decision)

        return RuntimeExecution(
            provenance=provenance,
            layout=self.layout,
            imprint_field_state=state,
            detector_signal=signal,
            digital_record=record,
            diagnostic_report=report,
            control_decision=decision,
        )

    @staticmethod
    def _require_handoff(value: object, expected: Type[object], layer: str) -> None:
        if not isinstance(value, expected):
            raise TypeError(f"{layer} must emit {expected.__name__}.")

    @staticmethod
    def _require_detector_irreversibility(signal: DetectorSignal) -> None:
        if not signal.irreversible_loss:
            raise ValueError("DetectorSignal must preserve detector-plane irreversibility.")

    @staticmethod
    def _require_no_diagnostic_reconstruction(report: DiagnosticReport) -> None:
        keys = {str(key).lower() for key in report.metrics.keys()}
        prohibited = keys & PROHIBITED_DIAGNOSTIC_RECONSTRUCTION_KEYS
        if prohibited:
            raise ValueError(
                "DiagnosticReport attempted upstream reconstruction via metrics: "
                + ", ".join(sorted(prohibited))
            )

    @staticmethod
    def _require_future_only_control(decision: ControlDecision) -> None:
        if not decision.applies_to_future_run:
            raise ValueError("ControlDecision may affect only future runs.")


def run_canonical_runtime(run_id: Optional[str] = None) -> RuntimeExecution:
    """Convenience entry point for one canonical QOS runtime execution."""
    return RuntimeOrchestrator().run(run_id=run_id)


def assert_causal_import_boundaries(root: Optional[Path] = None) -> None:
    """Reject imports that invert the causal layer order or mix frozen/experimental roots."""
    package_root = root or Path(__file__).resolve().parents[1]
    violations = tuple(_find_import_boundary_violations(package_root))
    if violations:
        raise ImportError("QOS causal import boundary violations: " + "; ".join(violations))


def runtime_execution_digest(execution: RuntimeExecution) -> str:
    """Create a stable digest for audit logs or external runtime artifact manifests."""
    payload = _json_safe(execution)
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _find_import_boundary_violations(package_root: Path) -> Sequence[str]:
    layer_order = {layer: index for index, layer in enumerate(CAUSAL_CHAIN)}
    violations = []
    for source in package_root.rglob("*.py"):
        module_parts = source.relative_to(package_root).with_suffix("").parts
        if not module_parts:
            continue
        source_layer = module_parts[0]
        if source_layer == "runtime":
            continue
        try:
            tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        except SyntaxError as exc:
            violations.append(f"{source}: cannot parse imports: {exc}")
            continue

        imported_roots = _imported_qos_roots(tree)
        for imported_layer in imported_roots:
            if _is_inverted_layer_import(source_layer, imported_layer, layer_order):
                violations.append(f"{source}: {source_layer} imports downstream {imported_layer}")
            if source_layer == "benchmarks" and imported_layer == "experiments":
                violations.append(f"{source}: frozen/evolving benchmarks must not import experiments")


    return violations


def _imported_qos_roots(tree: ast.AST) -> Sequence[str]:
    roots = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                parts = alias.name.split(".")
                if len(parts) > 1 and parts[0] == "qos":
                    roots.append(parts[1])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                parts = node.module.split(".")
                if len(parts) > 1 and parts[0] == "qos":
                    roots.append(parts[1])
    return tuple(roots)


def _is_inverted_layer_import(
    source_layer: str, imported_layer: str, layer_order: Mapping[str, int]
) -> bool:
    if source_layer not in layer_order or imported_layer not in layer_order:
        return False
    return layer_order[imported_layer] > layer_order[source_layer]


def _json_safe(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return {item.name: _json_safe(getattr(value, item.name)) for item in fields(value)}
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (Mapping, MappingProxyType)):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


if __name__ == "__main__":
    execution = run_canonical_runtime(run_id="manual")
    print(json.dumps(_json_safe(execution), indent=2, sort_keys=True))
    print(f"digest={runtime_execution_digest(execution)}", file=sys.stderr)
