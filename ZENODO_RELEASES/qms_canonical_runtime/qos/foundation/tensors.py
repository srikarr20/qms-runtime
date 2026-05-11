"""Canonical tensor descriptors for QOS foundation runtimes."""

from __future__ import annotations

import hashlib
import pickle
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Optional, Tuple

import numpy as np

Metadata = Mapping[str, Any]


def _freeze(metadata: Optional[Metadata]) -> Metadata:
    return MappingProxyType(dict(metadata or {}))


def stable_array_digest(array: np.ndarray) -> str:
    """Return a deterministic digest for an array without changing its layout."""
    contiguous = np.ascontiguousarray(array)
    digest = hashlib.sha256()
    digest.update(str(contiguous.shape).encode("utf-8"))
    digest.update(str(contiguous.dtype).encode("utf-8"))
    digest.update(contiguous.view(np.uint8))
    return digest.hexdigest()


@dataclass(frozen=True)
class FieldTensor:
    """Immutable descriptor plus runtime tensor for pre-measurement field data."""

    values: np.ndarray
    coordinates: Metadata = field(default_factory=dict)
    parameters: Metadata = field(default_factory=dict)
    lineage: Tuple[str, ...] = ()
    provenance: Metadata = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "values", np.asarray(self.values))
        object.__setattr__(self, "coordinates", _freeze(self.coordinates))
        object.__setattr__(self, "parameters", _freeze(self.parameters))
        object.__setattr__(self, "provenance", _freeze(self.provenance))

    @property
    def shape(self) -> Tuple[int, ...]:
        return tuple(int(item) for item in self.values.shape)

    @property
    def dtype(self) -> str:
        return str(self.values.dtype)

    def descriptor(self, *, include_digest: bool = False) -> Metadata:
        metadata = {
            "shape": self.shape,
            "dtype": self.dtype,
            "coordinates": dict(self.coordinates),
            "parameters": dict(self.parameters),
            "lineage": self.lineage,
            "provenance": dict(self.provenance),
        }
        if include_digest:
            metadata["sha256"] = stable_array_digest(self.values)
        return MappingProxyType(metadata)


def field_tensor_from_legacy_payload(
    payload: Mapping[str, Any],
    *,
    lineage: Iterable[str] = ("ImprintField", "field_data.pkl"),
    provenance: Optional[Metadata] = None,
) -> FieldTensor:
    """Adapt the recovered ImprintField ``field_data.pkl`` schema."""
    if "field" not in payload:
        raise KeyError("Legacy ImprintField payload must contain a 'field' tensor.")

    field_values = np.asarray(payload["field"])
    coordinates = {
        "basis": "legacy-imprint-grid",
        "axis_order": ("time", "x", "y", "z") if field_values.ndim == 4 else "unknown",
    }
    if "dx" in payload:
        coordinates["dx"] = payload["dx"]
    if "dt" in payload:
        coordinates["dt"] = payload["dt"]

    return FieldTensor(
        values=field_values,
        coordinates=coordinates,
        parameters={
            "source_schema": "field_data.pkl",
            "source_keys": tuple(sorted(str(key) for key in payload.keys())),
        },
        lineage=tuple(lineage),
        provenance=provenance,
    )


def load_legacy_field_data(
    path: str | Path,
    *,
    provenance: Optional[Metadata] = None,
) -> FieldTensor:
    """Load a recovered ImprintField ``field_data.pkl`` without schema changes."""
    with Path(path).open("rb") as handle:
        payload = pickle.load(handle)
    if not isinstance(payload, Mapping):
        raise TypeError("Legacy field data must be a mapping with a 'field' tensor.")
    return field_tensor_from_legacy_payload(payload, provenance=provenance)


def synthetic_imprint_tensor(
    *,
    time_steps: int = 4,
    size: int = 16,
    dx: float = 1.0,
    dt: float = 1.0,
    provenance: Optional[Metadata] = None,
) -> FieldTensor:
    """Create a deterministic compact ImprintField-compatible tensor."""
    axis = np.linspace(0.0, 2.0 * np.pi, size, endpoint=False)
    x, y, z = np.meshgrid(axis, axis, axis, indexing="ij")
    frames = []
    for t in range(time_steps):
        phase = 0.15 * t
        carrier = np.sin(x + phase) + 0.5 * np.cos(y - phase)
        imprint = np.exp(-((x - np.pi) ** 2 + (y - np.pi) ** 2 + (z - np.pi) ** 2) / 2.5)
        frames.append(carrier + imprint * np.cos(z + phase))
    return FieldTensor(
        values=np.asarray(frames, dtype=np.float64),
        coordinates={
            "basis": "canonical-imprint-grid",
            "axis_order": ("time", "x", "y", "z"),
            "dx": dx,
            "dt": dt,
        },
        parameters={"model": "synthetic-imprint-field", "deterministic": True},
        lineage=("foundation-runtime", "ImprintField", "synthetic"),
        provenance=provenance,
    )
