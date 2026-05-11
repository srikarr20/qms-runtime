"""
QMS Dashboard
Multi-Panel Observability Diagnostics
"""

import numpy as np
import matplotlib.pyplot as plt

from scipy.ndimage import gaussian_filter


def interference_pattern(
    n=2048,
    period=40,
    visibility=0.98,
):

    x = np.arange(n)

    signal = (
        1.0
        + visibility
        * np.cos(2 * np.pi * x / period)
    )

    return x, signal


def acquire(
    signal,
    sigma=0.0,
    noise_std=0.0,
    bin_factor=1,
):

    acquired = (
        gaussian_filter(signal, sigma=sigma)
        if sigma > 0
        else signal.copy()
    )

    if noise_std > 0:
        acquired += np.random.normal(
            0,
            noise_std,
            acquired.shape,
        )

    if bin_factor > 1:

        n_bins = len(acquired) // bin_factor

        acquired = (
            acquired[: n_bins * bin_factor]
            .reshape(n_bins, bin_factor)
            .mean(axis=1)
        )

    return acquired


def visibility(signal):

    return (
        signal.max() - signal.min()
    ) / (
        signal.max() + signal.min() + 1e-8
    )


def fft_spectrum(signal):

    fft = np.abs(np.fft.rfft(signal))

    fft /= fft.max() + 1e-8

    return fft


def main():

    print("\n=== QMS Dashboard ===")

    x, ideal = interference_pattern()

    scenarios = [
        (
            "High Fidelity",
            2.0,
            0.02,
            1,
        ),
        (
            "Medium Fidelity",
            12.0,
            0.10,
            4,
        ),
        (
            "Coarse Acquisition",
            40.0,
            0.35,
            8,
        ),
    ]

    acquired_signals = []

    visibility_values = [
        visibility(ideal)
    ]

    labels = [
        "Ideal"
    ]

    for (
        label,
        sigma,
        noise,
        bin_factor,
    ) in scenarios:

        acquired = acquire(
            ideal,
            sigma=sigma,
            noise_std=noise,
            bin_factor=bin_factor,
        )

        acquired_signals.append(
            (label, acquired)
        )

        visibility_values.append(
            visibility(acquired)
        )

        labels.append(label)

    fig, axes = plt.subplots(
        3,
        2,
        figsize=(16, 12),
    )

    # ------------------------------------------
    # Ideal Signal
    # ------------------------------------------

    axes[0, 0].plot(
        ideal,
        linewidth=1.5,
    )

    axes[0, 0].set_title(
        f"Ideal Interference\nVisibility={visibility_values[0]:.2f}"
    )

    axes[0, 0].set_xlabel(
        "Detector Coordinate"
    )

    axes[0, 0].set_ylabel(
        "Intensity"
    )

    # ------------------------------------------
    # Acquired Signals
    # ------------------------------------------

    for idx, (
        label,
        signal,
    ) in enumerate(acquired_signals):

        row = (idx + 1) // 2
        col = (idx + 1) % 2

        axes[row, col].plot(
            signal,
            linewidth=1.0,
        )

        axes[row, col].set_title(
            f"{label}\nVisibility={visibility(signal):.2f}"
        )

        axes[row, col].set_xlabel(
            "Detector Coordinate"
        )

        axes[row, col].set_ylabel(
            "Intensity"
        )

    # ------------------------------------------
    # FFT Diagnostics
    # ------------------------------------------

    fft_ax = axes[0, 1]

    fft_ax.plot(
        fft_spectrum(ideal),
        label="Ideal",
        linewidth=2,
    )

    for label, signal in acquired_signals:

        fft_ax.plot(
            fft_spectrum(signal),
            label=label,
            alpha=0.8,
        )

    fft_ax.set_title(
        "Spectral Coherence Diagnostics"
    )

    fft_ax.set_xlabel(
        "Spatial Frequency"
    )

    fft_ax.set_ylabel(
        "Normalized FFT Power"
    )

    fft_ax.legend()

    # ------------------------------------------
    # Visibility Metrics
    # ------------------------------------------

    bar_ax = axes[2, 1]

    bar_ax.bar(
        labels,
        visibility_values,
    )

    bar_ax.set_ylim(0, 1.1)

    bar_ax.set_ylabel(
        "Visibility"
    )

    bar_ax.set_title(
        "Observability Metrics"
    )

    plt.suptitle(
        "QMS Dashboard: Acquisition-Conditioned Observability",
        fontsize=16,
    )

    plt.tight_layout()

    output_path = (
        "examples/qms_dashboard.png"
    )

    plt.savefig(
        output_path,
        dpi=300,
    )

    print(
        f"\nSaved dashboard: {output_path}"
    )

    plt.show()


if __name__ == "__main__":
    main()
