"""
Visibility diagnostics for QMCTB
"""

import numpy as np


def compute_visibility(intensity, eps=1e-12):
    """
    Computes fringe visibility and statistical uncertainty.

    Visibility V = (I_max - I_min) / (I_max + I_min)

    Parameters
    ----------
    intensity : np.ndarray
        1D or 2D array of intensity values
    eps : float
        Numerical stability constant

    Returns
    -------
    V : float
        Visibility
    sigma_V : float
        Estimated statistical uncertainty
    """

    I = np.asarray(intensity).flatten()

    I_max = np.max(I)
    I_min = np.min(I)

    V = (I_max - I_min) / (I_max + I_min + eps)

    # Simple uncertainty estimate assuming Poisson noise
    sigma_V = np.sqrt(2 / max(len(I), 1)) * V

    return V, sigma_V

