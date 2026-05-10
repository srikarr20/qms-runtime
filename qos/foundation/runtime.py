"""Canonical foundation runtime implementation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Optional, Tuple

from qos.contracts import ImprintFieldState
from qos.foundation.persistent_dynamics.evolution import evolve_tensor
from qos.foundation.tensors import FieldTensor, load_legacy_field_data, synthetic_imprint_tensor


@dataclass(frozen=True)
class ImprintFoundationRuntime:
    """Emit canonical ImprintFieldState from reusable foundation primitives."""

    tensor: Optional[FieldTensor] = None
    legacy_field_data_path: Optional[Path] = None
    synthetic_shape: Tuple[int, int] = (4, 16)
    include_tensor_digest: bool = False
    max_evolution_steps: Optional[int] = 16
    smoothing_window: int = 10
    warning_threshold: float = 0.7
    parameters: Mapping[str, Any] = field(default_factory=dict)

    def run(self, run_id: str, provenance: Mapping[str, Any]) -> ImprintFieldState:
        tensor = self._resolve_tensor(provenance)
        evolution_tensor = self._evolution_tensor(tensor)
        evolution = evolve_tensor(
            evolution_tensor,
            smoothing_window=self.smoothing_window,
            warning_threshold=self.warning_threshold,
        )
        descriptor = tensor.descriptor(include_digest=self.include_tensor_digest)
        parameters = {
            **dict(tensor.parameters),
            **dict(self.parameters),
            "runtime": "qos.foundation.runtime.ImprintFoundationRuntime",
            "tensor": descriptor,
            "evolution_tensor_shape": evolution_tensor.shape,
            "persistent_evolution": evolution.descriptor(),
            "provenance": provenance,
        }
        coordinates = {
            **dict(tensor.coordinates),
            "causal_order": "strict-time-axis-first",
            "runtime_tensor_shape": tensor.shape,
            "runtime_tensor_dtype": tensor.dtype,
        }
        lineage = (
            *tensor.lineage,
            "DYNAMIC_FIELD_ENGINE:kappa-signature-regime-mode-predictive",
            "persistent_dynamics:evolve_tensor",
        )
        return ImprintFieldState(
            state_id=f"ifs-{run_id}",
            shape=tensor.shape,
            coordinates=coordinates,
            parameters=parameters,
            lineage=lineage,
        )

    def _resolve_tensor(self, provenance: Mapping[str, Any]) -> FieldTensor:
        if self.tensor is not None:
            return self.tensor
        if self.legacy_field_data_path is not None:
            return load_legacy_field_data(self.legacy_field_data_path, provenance=provenance)
        time_steps, size = self.synthetic_shape
        return synthetic_imprint_tensor(
            time_steps=int(time_steps),
            size=int(size),
            provenance=provenance,
        )

    def _evolution_tensor(self, tensor: FieldTensor) -> FieldTensor:
        if self.max_evolution_steps is None or tensor.values.shape[0] <= self.max_evolution_steps:
            return tensor
        return FieldTensor(
            values=tensor.values[: self.max_evolution_steps],
            coordinates=tensor.coordinates,
            parameters={
                **dict(tensor.parameters),
                "analysis_window": (0, int(self.max_evolution_steps)),
                "source_tensor_shape": tensor.shape,
            },
            lineage=(*tensor.lineage, "bounded-evolution-window"),
            provenance=tensor.provenance,
        )


def field_state_from_tensor(
    tensor: FieldTensor,
    *,
    run_id: str = "foundation",
    provenance: Optional[Mapping[str, Any]] = None,
) -> ImprintFieldState:
    """Convenience API for examples and benchmark runners."""
    return ImprintFoundationRuntime(tensor=tensor).run(run_id, dict(provenance or {}))
