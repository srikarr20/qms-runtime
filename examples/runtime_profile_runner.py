"""
QMS Runtime Profile Runner
"""

import json
from pathlib import Path
from datetime import datetime

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

    return signal


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

    profile_name = input(
        "\nProfile name: "
    ).strip()

    profile_path = (
        Path("qos/profiles")
        / f"{profile_name}.json"
    )

    if not profile_path.exists():

        print(
            f"Profile not found: {profile_path}"
        )

        return

    with open(profile_path) as f:

        profile = json.load(f)

    signal = interference_pattern()

    acquired = acquire(
        signal,
        sigma=profile["sigma"],
        noise_std=profile["noise_std"],
        bin_factor=profile["bin_factor"],
    )

    vis = visibility(acquired)

    timestamp = datetime.utcnow().strftime(
        "%Y%m%d_%H%M%S"
    )

    artifact_dir = (
        Path(
            "qos/artifacts/generated/runtime"
        )
        / f"{profile_name}_{timestamp}"
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ----------------------------------------
    # Save Metrics
    # ----------------------------------------

    metrics = {
        "profile": profile_name,
        "visibility": float(vis),
        "sigma": profile["sigma"],
        "noise_std": profile["noise_std"],
        "bin_factor": profile["bin_factor"],
    }

    with open(
        artifact_dir / "metrics.json",
        "w",
    ) as f:

        json.dump(
            metrics,
            f,
            indent=4,
        )

    # ----------------------------------------
    # Save Provenance
    # ----------------------------------------

    provenance = {
        "runtime": "QMS",
        "timestamp_utc": timestamp,
        "artifact_dir": str(artifact_dir),
    }

    with open(
        artifact_dir / "provenance.json",
        "w",
    ) as f:

        json.dump(
            provenance,
            f,
            indent=4,
        )

    # ----------------------------------------
    # Save Visualization
    # ----------------------------------------

    plt.figure(figsize=(12, 6))

    plt.plot(
        signal,
        label="Ideal",
        linewidth=2,
    )

    plt.plot(
        acquired,
        label=f"{profile_name} ({vis:.2f})",
        alpha=0.8,
    )

    plt.title(
        f"QMS Runtime Profile: {profile_name}"
    )

    plt.xlabel(
        "Detector Coordinate"
    )

    plt.ylabel(
        "Intensity"
    )

    plt.legend()

    plt.tight_layout()

    image_path = (
        artifact_dir / "dashboard.png"
    )

    plt.savefig(
        image_path,
        dpi=300,
    )

    print(
        "\n=== QMS Runtime Artifact ==="
    )

    print(
        f"Profile:      {profile_name}"
    )

    print(
        f"Visibility:   {vis:.4f}"
    )

    print(
        f"Artifacts:    {artifact_dir}"
    )

    plt.show()


if __name__ == "__main__":
    main()
