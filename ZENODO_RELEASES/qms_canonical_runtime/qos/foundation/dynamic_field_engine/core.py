"""Reusable Dynamic Field Engine primitives."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Tuple

import numpy as np

EPSILON = 1e-8


@dataclass(frozen=True)
class KappaSignature:
    instability: np.ndarray
    pattern: np.ndarray


@dataclass(frozen=True)
class ModeMetrics:
    counts: np.ndarray
    average_sizes: np.ndarray
    centroid_drift: np.ndarray


@dataclass(frozen=True)
class PredictiveSignals:
    density: np.ndarray
    first_derivative: np.ndarray
    second_derivative: np.ndarray
    rolling_variance: np.ndarray
    confidence: np.ndarray
    warning_indices: Tuple[int, ...]


def compute_kappa(field: np.ndarray) -> np.ndarray:
    tensor = np.asarray(field, dtype=float)
    if tensor.ndim < 2:
        raise ValueError("field must have at least a time axis and one spatial axis")
    temporal = np.diff(tensor, axis=0, append=tensor[-1:])
    spatial_axis = min(2, tensor.ndim - 1)
    spatial = np.diff(tensor, axis=spatial_axis, append=np.take(tensor, [-1], axis=spatial_axis))
    gradient = temporal**2 + spatial**2
    return tensor / (1.0 + gradient)


def compute_signature(kappa: np.ndarray) -> KappaSignature:
    tensor = np.asarray(kappa, dtype=float)
    if tensor.shape[0] < 2:
        zeros = np.zeros(tensor.shape[0], dtype=float)
        return KappaSignature(instability=zeros, pattern=zeros)

    instability = []
    pattern = []
    for t in range(1, tensor.shape[0]):
        temporal_energy = float(np.mean((tensor[t] - tensor[t - 1]) ** 2))
        spatial_pattern = float(np.std(tensor[t]))
        instability.append(temporal_energy * 5.0 + spatial_pattern)
        pattern.append(spatial_pattern)
    return KappaSignature(
        instability=normalize_series(instability),
        pattern=normalize_series(pattern),
    )


def normalize_series(values: Iterable[float]) -> np.ndarray:
    series = np.asarray(tuple(values), dtype=float)
    if series.size == 0:
        return series
    return (series - np.min(series)) / (np.ptp(series) + EPSILON)


def smooth_signal(signal: np.ndarray, *, window: int = 10) -> np.ndarray:
    series = np.asarray(signal, dtype=float)
    if window <= 1 or series.size == 0:
        return series.copy()
    kernel = np.ones(int(window), dtype=float) / float(window)
    return np.convolve(series, kernel, mode="same")


def classify_regimes(
    instability: np.ndarray,
    *,
    stable_threshold: float = 0.3,
    structured_threshold: float = 0.6,
) -> np.ndarray:
    series = np.asarray(instability, dtype=float)
    labels = np.zeros(series.shape, dtype=np.int8)
    labels[series >= stable_threshold] = 1
    labels[series >= structured_threshold] = 2
    return labels


def detect_transitions(labels: np.ndarray) -> Tuple[int, ...]:
    values = np.asarray(labels)
    if values.size < 2:
        return ()
    return tuple(int(i) for i in np.flatnonzero(values[1:] != values[:-1]) + 1)


def extract_modes(frame: np.ndarray, *, percentile: float = 80.0) -> Tuple[np.ndarray, int]:
    values = np.asarray(frame, dtype=float)
    norm = normalize_frame(values)
    active = norm > float(np.percentile(norm, percentile))
    labels = np.zeros(active.shape, dtype=np.int32)
    mode_id = 0
    for start in zip(*np.nonzero(active & (labels == 0))):
        mode_id += 1
        point = tuple(int(item) for item in start)
        labels[point] = mode_id
        stack = [point]
        while stack:
            current = stack.pop()
            for neighbor in _neighbors(current, active.shape):
                if active[neighbor] and labels[neighbor] == 0:
                    labels[neighbor] = mode_id
                    stack.append(neighbor)
    return labels, mode_id


def normalize_frame(frame: np.ndarray) -> np.ndarray:
    values = np.asarray(frame, dtype=float)
    return (values - np.min(values)) / (np.ptp(values) + EPSILON)


def mode_metrics(kappa: np.ndarray, *, percentile: float = 80.0) -> ModeMetrics:
    tensor = np.asarray(kappa, dtype=float)
    counts = []
    average_sizes = []
    centroid_drift = []
    previous_centroids: Optional[np.ndarray] = None
    for t in range(tensor.shape[0]):
        labels, count = extract_modes(tensor[t], percentile=percentile)
        counts.append(count)
        sizes = [int(np.sum(labels == index)) for index in range(1, count + 1)]
        average_sizes.append(float(np.mean(sizes)) if sizes else 0.0)
        centroids = _centroids(labels, count)
        if previous_centroids is None or centroids.size == 0 or previous_centroids.size == 0:
            centroid_drift.append(0.0)
        else:
            distances = [
                float(np.min(np.linalg.norm(previous_centroids - centroid, axis=1)))
                for centroid in centroids
            ]
            centroid_drift.append(float(np.mean(distances)) if distances else 0.0)
        previous_centroids = centroids
    return ModeMetrics(
        counts=np.asarray(counts, dtype=int),
        average_sizes=np.asarray(average_sizes, dtype=float),
        centroid_drift=np.asarray(centroid_drift, dtype=float),
    )


def interaction_density(kappa: np.ndarray, *, percentile: float = 80.0) -> np.ndarray:
    tensor = np.asarray(kappa, dtype=float)
    if tensor.shape[0] < 2:
        return np.zeros(0, dtype=float)
    density = []
    previous_labels, _ = extract_modes(tensor[0], percentile=percentile)
    for t in range(1, tensor.shape[0]):
        current_labels, _ = extract_modes(tensor[t], percentile=percentile)
        density.append(float(np.sum((previous_labels > 0) & (current_labels > 0))))
        previous_labels = current_labels
    return np.asarray(density, dtype=float)


def compute_dynamics(signal: np.ndarray, *, window: int = 5) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    series = np.asarray(signal, dtype=float)
    if series.size == 0:
        empty = np.zeros(0, dtype=float)
        return empty, empty, empty
    if series.size == 1:
        zeros = np.zeros(1, dtype=float)
        return zeros, zeros, zeros
    first = np.gradient(series)
    second = np.gradient(first)
    variance = np.asarray(
        [np.var(series[max(0, i - window) : i + 1]) for i in range(series.size)],
        dtype=float,
    )
    return first, second, variance


def compute_confidence(
    first_derivative: np.ndarray,
    second_derivative: np.ndarray,
    rolling_variance: np.ndarray,
    *,
    weights: Tuple[float, float, float] = (0.4, 0.3, 0.3),
) -> np.ndarray:
    return (
        weights[0] * normalize_series(first_derivative)
        + weights[1] * normalize_series(second_derivative)
        + weights[2] * normalize_series(rolling_variance)
    )


def predictive_signals(kappa: np.ndarray, *, threshold: float = 0.7) -> PredictiveSignals:
    density = interaction_density(kappa)
    first, second, variance = compute_dynamics(density)
    confidence = compute_confidence(first, second, variance)
    warnings = tuple(int(i) for i in np.flatnonzero(confidence > threshold))
    return PredictiveSignals(
        density=density,
        first_derivative=first,
        second_derivative=second,
        rolling_variance=variance,
        confidence=confidence,
        warning_indices=warnings,
    )


def _centroids(labels: np.ndarray, count: int) -> np.ndarray:
    centroids = []
    for index in range(1, count + 1):
        coords = np.argwhere(labels == index)
        if coords.size:
            centroids.append(np.mean(coords, axis=0))
    return np.asarray(centroids, dtype=float)


def _neighbors(point: Tuple[int, ...], shape: Tuple[int, ...]):
    for axis in range(len(shape)):
        for delta in (-1, 1):
            candidate = list(point)
            candidate[axis] += delta
            if 0 <= candidate[axis] < shape[axis]:
                yield tuple(candidate)
