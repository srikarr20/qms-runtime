"""
PyOCT ↔ QMS observability degradation validation
"""

import numpy as np
from scipy.ndimage import gaussian_filter


# =====================================================
# Synthetic interference pattern
# =====================================================

def interference_pattern(
    n=4096,
    period=40,
    visibility=0.98,
):

    x = np.arange(n)

    I = 1.0 + visibility * np.cos(
        2 * np.pi * x / period
    )

    return x, I


# =====================================================
# Acquisition degradation
# =====================================================

def acquire(
    I,
    sigma=0.0,
    noise_std=0.0,
    bin_factor=1,
):

    out = I.copy()

    # spatial blur
    if sigma > 0:
        out = gaussian_filter(out, sigma=sigma)

    # detector noise
    if noise_std > 0:
        out += np.random.normal(
            0,
            noise_std,
            out.shape,
        )

    # detector binning
    if bin_factor > 1:

        usable = len(out) // bin_factor

        out = out[:usable * bin_factor]

        out = out.reshape(
            usable,
            bin_factor,
        ).mean(axis=1)

    return out


# =====================================================
# Visibility metric
# =====================================================

def visibility(I):

    return (
        np.max(I) - np.min(I)
    ) / (
        np.max(I) + np.min(I) + 1e-12
    )


# =====================================================
# Observability metric
# =====================================================

def observability_index(vis):

    return np.clip(vis, 0.0, 1.0)


# =====================================================
# Validation scenarios
# =====================================================

SCENARIOS = [

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


# =====================================================
# Main
# =====================================================

def main():

    print("\n=== PyOCT ↔ QMS Validation ===\n")

    x, ideal = interference_pattern()

    ideal_vis = visibility(ideal)

    print(f"Ideal visibility: {ideal_vis:.4f}\n")

    for (
        label,
        sigma,
        noise,
        binning,
    ) in SCENARIOS:

        acquired = acquire(
            ideal,
            sigma=sigma,
            noise_std=noise,
            bin_factor=binning,
        )

        vis = visibility(acquired)

        obs = observability_index(vis)

        loss = ideal_vis - vis

        print(f"--- {label} ---")

        print(f"sigma:             {sigma}")
        print(f"noise_std:         {noise}")
        print(f"bin_factor:        {binning}")

        print(f"visibility:        {vis:.4f}")
        print(f"observability:     {obs:.4f}")
        print(f"visibility loss:   {loss:.4f}")

        print()

    print("Validation complete.\n")


if __name__ == "__main__":
    main()
