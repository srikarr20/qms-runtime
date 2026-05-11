"""Persistent tensor evolution summaries for canonical foundation APIs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Tuple

import numpy as np

from qos.foundation.dynamic_field_engine.core import (
    classify_regimes,
    compute_kappa,
    compute_signature,
    detect_transitions,
    mode_metrics,
    predictive_signals,
    smooth_signal,
)
from qos.foundation.tensors import FieldTensor


@dataclass(frozen=True)
class PersistentEvolution:
    """Stable summary of causal field evolution, ordered by time."""

    kappa: np.ndarray
    instability: np.ndarray
    pattern: np.ndarray
    persistent_instability: np.ndarray
    regimes: np.ndarray
    transitions: Tuple[int, ...]
    mode_count: np.ndarray
    mode_average_size: np.ndarray
    mode_centroid_drift: np.ndarray
    interaction_density: np.ndarray
    confidence: np.ndarray
    warning_indices: Tuple[int, ...]

    def descriptor(self) -> Mapping[str, object]:
        return {
            "kappa_shape": tuple(int(item) for item in self.kappa.shape),
            "instability_length": int(self.instability.size),
            "pattern_length": int(self.pattern.size),
            "regime_labels": tuple(int(item) for item in np.unique(self.regimes)),
            "transitions": self.transitions,
            "mode_count_length": int(self.mode_count.size),
            "interaction_density_length": int(self.interaction_density.size),
            "warning_indices": self.warning_indices,
            "adaptive_coherence_extension": "foundation-signal-only",
        }


def evolve_tensor(
    tensor: FieldTensor,
    *,
    smoothing_window: int = 10,
    warning_threshold: float = 0.7,
) -> PersistentEvolution:
    """Compute persistent foundation evolution in strict temporal order."""
    kappa = compute_kappa(tensor.values)
    signature = compute_signature(kappa)
    persistent_instability = smooth_signal(signature.instability, window=smoothing_window)
    regimes = classify_regimes(persistent_instability)
    transitions = detect_transitions(regimes)
    modes = mode_metrics(kappa)
    predictive = predictive_signals(kappa, threshold=warning_threshold)
    return PersistentEvolution(
        kappa=kappa,
        instability=signature.instability,
        pattern=signature.pattern,
        persistent_instability=persistent_instability,
        regimes=regimes,
        transitions=transitions,
        mode_count=modes.counts,
        mode_average_size=modes.average_sizes,
        mode_centroid_drift=modes.centroid_drift,
        interaction_density=predictive.density,
        confidence=predictive.confidence,
        warning_indices=predictive.warning_indices,
    )
