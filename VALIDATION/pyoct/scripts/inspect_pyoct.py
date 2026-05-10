"""
Initial PyOCT semantic inspection
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PYOCT = ROOT / "EXTERNAL" / "PyOCT"

print("\n=== PyOCT Inspection ===\n")

targets = [
    "PyOCTRecon.py",
    "CAO.py",
    "HoloLib.py",
    "dmd_simulation.py",
]

for target in targets:

    path = PYOCT / target

    print(f"\n--- {target} ---")

    if not path.exists():
        print("Missing")
        continue

    with open(path, "r", errors="ignore") as f:

        lines = f.readlines()

    print(f"Total lines: {len(lines)}")

    keywords = [
        "Interference",
        "phase",
        "dispersion",
        "fft",
        "reconstruct",
        "spectral",
        "aberration",
        "coherence",
        "sampling",
    ]

    for keyword in keywords:

        hits = [
            i + 1
            for i, line in enumerate(lines)
            if keyword.lower() in line.lower()
        ]

        if hits:
            print(f"{keyword}: {len(hits)} hits")
