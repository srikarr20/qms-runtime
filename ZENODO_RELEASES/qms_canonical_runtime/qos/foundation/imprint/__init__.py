"""ImprintField lineage adapters for canonical foundation handoffs."""

from qos.foundation.runtime import ImprintFoundationRuntime, field_state_from_tensor
from qos.foundation.tensors import field_tensor_from_legacy_payload, load_legacy_field_data

__all__ = (
    "ImprintFoundationRuntime",
    "field_state_from_tensor",
    "field_tensor_from_legacy_payload",
    "load_legacy_field_data",
)
