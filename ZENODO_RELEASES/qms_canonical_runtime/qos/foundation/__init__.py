"""Foundation layer: pre-measurement field and imprint dynamics."""

from .runtime import ImprintFoundationRuntime, field_state_from_tensor
from .tensors import (
    FieldTensor,
    field_tensor_from_legacy_payload,
    load_legacy_field_data,
    stable_array_digest,
    synthetic_imprint_tensor,
)

__all__ = (
    "FieldTensor",
    "ImprintFoundationRuntime",
    "field_state_from_tensor",
    "field_tensor_from_legacy_payload",
    "load_legacy_field_data",
    "stable_array_digest",
    "synthetic_imprint_tensor",
)
