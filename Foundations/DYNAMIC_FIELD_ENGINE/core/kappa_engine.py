import numpy as np
from scipy.ndimage import gaussian_filter

def compute_kappa(I):

    I_s = gaussian_filter(I, sigma=(1,1,1))

    dx = np.diff(I_s, axis=2, append=I_s[:,:,-1:])
    dt = np.diff(I_s, axis=0, append=I_s[-1:,:,:])

    grad = dx**2 + dt**2
    coherence = 1 / (1 + grad)

    return I_s * coherence


def compute_signature(kappa):

    inst_series = []
    pat_series = []

    for t in range(kappa.shape[0]):

        frame = kappa[t]

        inst = np.mean(np.abs(frame))
        pat = np.std(frame)

        inst_series.append(inst)
        pat_series.append(pat)

    inst_series = np.array(inst_series)
    pat_series = np.array(pat_series)

    inst_series /= (np.max(inst_series) + 1e-8)
    pat_series /= (np.max(pat_series) + 1e-8)

    return inst_series, pat_series
