"""
QMS SDK Example:
Acquisition-Conditioned Observability Degradation
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

    intensity = (
        1.0
        + visibility
        * np.cos(2 * np.pi * x / period)
    )

    return x, intensity


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


def main():

    print(
        "\n=== QMS Acquisition Degradation Demo ==="
    )

    x, ideal = interference_pattern()

    ideal_vis = visibility(ideal)

    print(f"\nIdeal Visibility: {ideal_vis:.4f}")

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

    plt.figure(figsize=(12, 8))

    plt.plot(
        ideal,
        label=f"Ideal ({ideal_vis:.2f})",
        linewidth=2,
    )

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

        vis = visibility(acquired)

        print(f"\n--- {label} ---")
        print(f"sigma:           {sigma}")
        print(f"noise_std:       {noise}")
        print(f"bin_factor:      {bin_factor}")
        print(f"visibility:      {vis:.4f}")
        print(
            f"visibility loss: {ideal_vis - vis:.4f}"
        )

        plt.plot(
            acquired,
            label=f"{label} ({vis:.2f})",
            alpha=0.8,
        )

    plt.title(
        "QMS: Acquisition-Conditioned Observability"
    )

    plt.xlabel("Detector Coordinate")

    plt.ylabel("Intensity")

    plt.legend()

    plt.tight_layout()

    output_path = (
        "examples/acquisition_degradation.png"
    )

    plt.savefig(
        output_path,
        dpi=300,
    )

    print(
        f"\nSaved visualization: {output_path}"
    )

    plt.show()


if __name__ == "__main__":
    main()
