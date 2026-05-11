import argparse
import json
from pathlib import Path
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt

from scipy.ndimage import gaussian_filter

from qos.foundation.dynamic_field_engine import (
    ImprintFieldEngine,
)


# ---------------------------------------------------
# SIGNAL GENERATION
# ---------------------------------------------------

def interference_pattern(
    n=2048,
    period=40,
    visibility=0.98,
):

    x = np.arange(n)

    signal = (
        1.0
        + visibility
        * np.cos(
            2 * np.pi * x / period
        )
    )

    return signal


# ---------------------------------------------------
# ACQUISITION MODEL
# ---------------------------------------------------

def acquire(
    signal,
    sigma=0.0,
    noise_std=0.0,
    bin_factor=1,
):

    acquired = (
        gaussian_filter(
            signal,
            sigma=sigma,
        )
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

        n_bins = (
            len(acquired)
            // bin_factor
        )

        acquired = (
            acquired[
                : n_bins * bin_factor
            ]
            .reshape(
                n_bins,
                bin_factor,
            )
            .mean(axis=1)
        )

    return acquired


# ---------------------------------------------------
# METRICS
# ---------------------------------------------------

def fringe_visibility(signal):

    signal = np.asarray(signal)

    p95 = np.percentile(signal, 95)

    p5 = np.percentile(signal, 5)

    return (
        p95 - p5
    ) / (
        p95 + p5 + 1e-8
    )


def spectral_coherence(signal):

    signal = np.asarray(signal)

    fft = np.abs(
        np.fft.rfft(signal)
    )

    fft[0] = 0.0

    peak = fft.max()

    mean_background = (
        np.mean(fft)
        + 1e-8
    )

    return peak / mean_background


def signal_to_noise(signal):

    signal = np.asarray(signal)

    mean_signal = np.mean(signal)

    std_signal = (
        np.std(signal)
        + 1e-8
    )

    return mean_signal / std_signal


def detector_fidelity(signal):

    fv = fringe_visibility(signal)

    sc = spectral_coherence(signal)

    snr = signal_to_noise(signal)

    normalized_sc = min(
        sc / 20.0,
        1.0,
    )

    normalized_snr = min(
        snr / 10.0,
        1.0,
    )

    fidelity = (
        0.5 * fv
        + 0.3 * normalized_sc
        + 0.2 * normalized_snr
    )

    return {
        "fringe_visibility":
            float(fv),

        "spectral_coherence":
            float(sc),

        "signal_to_noise":
            float(snr),

        "detector_fidelity":
            float(fidelity),
    }


# ---------------------------------------------------
# PROFILE MODE
# ---------------------------------------------------

def run_profile(profile_name):

    profile_path = (
        Path("qos/profiles")
        / f"{profile_name}.json"
    )

    if not profile_path.exists():

        print(
            f"Profile not found: "
            f"{profile_path}"
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

    diagnostics = detector_fidelity(
        acquired
    )

    fidelity = diagnostics[
        "detector_fidelity"
    ]

    timestamp = datetime.utcnow().strftime(
        "%Y%m%d_%H%M%S"
    )

    artifact_dir = (
        Path(
            "qos/artifacts/generated/runtime"
        )
        / f"profile_{timestamp}"
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    metrics = {
        "profile":
            profile_name,

        "diagnostics":
            diagnostics,
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

    plt.figure(figsize=(12, 6))

    plt.plot(
        signal,
        label="Ideal",
        linewidth=2,
    )

    plt.plot(
        acquired,
        label=f"{profile_name} ({fidelity:.2f})",
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

    plt.savefig(
        artifact_dir / "dashboard.png",
        dpi=300,
    )

    print(
        "\n=== QMS Runtime Artifact ==="
    )

    print(
        f"Profile: {profile_name}"
    )

    print(
        f"Detector Fidelity: {fidelity:.4f}"
    )

    print(
        f"Artifacts: {artifact_dir}"
    )

    plt.show()


# ---------------------------------------------------
# EVOLUTION MODE
# ---------------------------------------------------

def run_evolve():

    engine = ImprintFieldEngine()

    history, tensor = (
        engine.evolve()
    )

    fig, axes = plt.subplots(
        2,
        1,
        figsize=(14, 10),
    )

    # -----------------------------------
    # FIELD EVOLUTION
    # -----------------------------------

    im = axes[0].imshow(
        history,
        aspect="auto",
        origin="lower",
    )

    axes[0].set_title(
        "Persistent Imprint Field Evolution"
    )

    axes[0].set_xlabel(
        "Spatial Coordinate"
    )

    axes[0].set_ylabel(
        "Runtime Step"
    )

    fig.colorbar(
        im,
        ax=axes[0],
        label="Field Amplitude",
    )

    # -----------------------------------
    # RUNTIME FIDELITY TENSOR
    # -----------------------------------

    fidelity = [
        x["fidelity"]
        for x in tensor
    ]

    coherence = [
        x["coherence"]
        for x in tensor
    ]

    detector_loss = [
        x["detector_loss"]
        for x in tensor
    ]

    environmental_loss = [
        x["environmental_loss"]
        for x in tensor
    ]

    noise = [
        x["noise"]
        for x in tensor
    ]

    axes[1].plot(
        fidelity,
        label="Detector Fidelity",
        linewidth=2,
    )

    axes[1].plot(
        coherence,
        label="Coherence",
        linewidth=2,
    )

    axes[1].plot(
        detector_loss,
        label="Detector Loss",
        linewidth=2,
    )

    axes[1].plot(
        environmental_loss,
        label="Environmental Loss",
        linewidth=2,
    )

    axes[1].plot(
        noise,
        label="Noise",
        linewidth=2,
    )

    axes[1].set_title(
        "Runtime Fidelity Tensor"
    )

    axes[1].set_xlabel(
        "Runtime Step"
    )

    axes[1].set_ylabel(
        "Metric Value"
    )

    axes[1].legend()

    axes[1].grid(True)

    plt.tight_layout()

    # -----------------------------------
    # SAVE ARTIFACTS
    # -----------------------------------

    timestamp = datetime.utcnow().strftime(
        "%Y%m%d_%H%M%S"
    )

    artifact_dir = (
        Path(
            "qos/artifacts/generated/runtime"
        )
        / f"evolve_{timestamp}"
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.savefig(
        artifact_dir
        / "field_evolution.png",
        dpi=300,
    )

    metrics = {
        "runtime_tensor":
            tensor,

        "shape":
            list(history.shape),
    }

    with open(
        artifact_dir
        / "runtime_tensor.json",
        "w",
    ) as f:

        json.dump(
            metrics,
            f,
            indent=4,
        )

    print(
        "\n=== QMS Field Evolution ==="
    )

    print(
        f"Artifacts: {artifact_dir}"
    )

    plt.show()


# ---------------------------------------------------
# CLI
# ---------------------------------------------------

def main():

    parser = argparse.ArgumentParser(
        prog="qms",
    )

    subparsers = parser.add_subparsers(
        dest="command"
    )

    # -----------------------------------
    # RUN
    # -----------------------------------

    run_parser = subparsers.add_parser(
        "run"
    )

    run_parser.add_argument(
        "--profile",
        required=True,
    )

    # -----------------------------------
    # EVOLVE
    # -----------------------------------

    subparsers.add_parser(
        "evolve"
    )

    args = parser.parse_args()

    if args.command == "run":

        run_profile(
            args.profile
        )

    elif args.command == "evolve":

        run_evolve()

    else:

        parser.print_help()


if __name__ == "__main__":

    main()
