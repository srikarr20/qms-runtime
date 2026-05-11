import argparse
import json

from datetime import datetime

from pathlib import Path

import numpy as np

import matplotlib.pyplot as plt


from qos.foundation.detector_network_field_engine import (
    DetectorNetworkFieldEngine,
)

from qos.foundation.memory_detector_network_engine import (
    MemoryDetectorNetworkEngine,
)


# ============================================================
# DETECTOR NETWORK
# ============================================================

def run_detector_network():

    engine = (
        DetectorNetworkFieldEngine()
    )

    history, tensor = (
        engine.evolve()
    )

    fig, axes = plt.subplots(
        3,
        1,
        figsize=(14, 14),
    )

    # ========================================================
    # PANEL 1
    # ========================================================

    im = axes[0].imshow(
        history,
        aspect="auto",
        origin="lower",
    )

    axes[0].set_title(
        "Detector Network Runtime"
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

    # ========================================================
    # PANEL 2
    # ========================================================

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
        linewidth=2,
        label="Detector Fidelity",
    )

    axes[1].plot(
        coherence,
        linewidth=2,
        label="Coherence",
    )

    axes[1].plot(
        detector_loss,
        linewidth=2,
        label="Detector Loss",
    )

    axes[1].plot(
        environmental_loss,
        linewidth=2,
        label="Environmental Loss",
    )

    axes[1].plot(
        noise,
        linewidth=2,
        label="Noise",
    )

    axes[1].set_title(
        "Network Runtime Tensor"
    )

    axes[1].set_xlabel(
        "Runtime Step"
    )

    axes[1].set_ylabel(
        "Metric Value"
    )

    axes[1].legend()

    axes[1].grid(True)

    # ========================================================
    # PANEL 3
    # ========================================================

    detector_states = np.array(
        [
            x["detector_states"]
            for x in tensor
        ]
    )

    for i in range(
        detector_states.shape[1]
    ):

        axes[2].plot(
            detector_states[:, i],
            linewidth=2,
            label=f"Detector {i+1}",
        )

    axes[2].set_title(
        "Detector Network States"
    )

    axes[2].set_xlabel(
        "Runtime Step"
    )

    axes[2].set_ylabel(
        "Detector Coupling State"
    )

    axes[2].legend()

    axes[2].grid(True)

    plt.tight_layout()

    # ========================================================
    # SAVE
    # ========================================================

    timestamp = datetime.utcnow().strftime(
        "%Y%m%d_%H%M%S"
    )

    artifact_dir = (
        Path(
            "qos/artifacts/generated/runtime"
        )
        / f"detector_network_{timestamp}"
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.savefig(
        artifact_dir
        / "detector_network.png",
        dpi=300,
    )

    metrics = {

        "runtime_tensor":
            tensor,

        "field_shape":
            list(history.shape),

        "final_fidelity":
            float(
                fidelity[-1]
            ),

        "final_coherence":
            float(
                coherence[-1]
            ),
    }

    with open(
        artifact_dir
        / "detector_network_tensor.json",
        "w",
    ) as f:

        json.dump(
            metrics,
            f,
            indent=4,
        )

    print(
        "\n=== Detector Network Runtime ==="
    )

    print(
        f"Artifacts: {artifact_dir}"
    )

    plt.show()


# ============================================================
# MEMORY NETWORK
# ============================================================

def run_memory_network():

    engine = (
        MemoryDetectorNetworkEngine()
    )

    history, tensor = (
        engine.evolve()
    )

    fig, axes = plt.subplots(
        4,
        1,
        figsize=(14, 18),
    )

    # ========================================================
    # PANEL 1
    # ========================================================

    im = axes[0].imshow(
        history,
        aspect="auto",
        origin="lower",
    )

    axes[0].set_title(
        "Memory Detector Runtime"
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

    # ========================================================
    # PANEL 2
    # ========================================================

    fidelity = [
        x["fidelity"]
        for x in tensor
    ]

    coherence = [
        x["coherence"]
        for x in tensor
    ]

    axes[1].plot(
        fidelity,
        linewidth=2,
        label="Detector Fidelity",
    )

    axes[1].plot(
        coherence,
        linewidth=2,
        label="Coherence",
    )

    axes[1].legend()

    axes[1].grid(True)

    axes[1].set_title(
        "Memory Runtime Tensor"
    )

    # ========================================================
    # PANEL 3
    # ========================================================

    detector_states = np.array(
        [
            x["detector_states"]
            for x in tensor
        ]
    )

    for i in range(
        detector_states.shape[1]
    ):

        axes[2].plot(
            detector_states[:, i],
            linewidth=2,
            label=f"Detector {i+1}",
        )

    axes[2].legend()

    axes[2].grid(True)

    axes[2].set_title(
        "Detector States"
    )

    # ========================================================
    # PANEL 4
    # ========================================================

    detector_memories = np.array(
        [
            x["detector_memories"]
            for x in tensor
        ]
    )

    for i in range(
        detector_memories.shape[1]
    ):

        axes[3].plot(
            detector_memories[:, i],
            linewidth=2,
            label=f"Memory {i+1}",
        )

    axes[3].legend()

    axes[3].grid(True)

    axes[3].set_title(
        "Detector Memory Tensor"
    )

    plt.tight_layout()

    # ========================================================
    # SAVE
    # ========================================================

    timestamp = datetime.utcnow().strftime(
        "%Y%m%d_%H%M%S"
    )

    artifact_dir = (
        Path(
            "qos/artifacts/generated/runtime"
        )
        / f"memory_network_{timestamp}"
    )

    artifact_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.savefig(
        artifact_dir
        / "memory_network.png",
        dpi=300,
    )

    with open(
        artifact_dir
        / "memory_network_tensor.json",
        "w",
    ) as f:

        json.dump(
            {
                "runtime_tensor":
                    tensor
            },
            f,
            indent=4,
        )

    print(
        "\n=== Memory Detector Runtime ==="
    )

    print(
        f"Artifacts: {artifact_dir}"
    )

    plt.show()


# ============================================================
# MAIN
# ============================================================

def main():

    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(
        dest="command"
    )

    # ========================================================
    # COMMANDS
    # ========================================================

    subparsers.add_parser(
        "network"
    )

    subparsers.add_parser(
        "memory-network"
    )

    args = parser.parse_args()

    # ========================================================
    # EXECUTION
    # ========================================================

    if (
        args.command
        == "network"
    ):

        run_detector_network()

    elif (
        args.command
        == "memory-network"
    ):

        run_memory_network()

    else:

        parser.print_help()


# ============================================================
# ENTRY
# ============================================================

if __name__ == "__main__":

    main()
