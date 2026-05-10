import numpy as np

def generate_wave(T=100, N=128, mode="stable"):

    x = np.linspace(0, 2*np.pi, N)
    y = np.linspace(0, 2*np.pi, N)
    X, Y = np.meshgrid(x, y)

    field = []

    for t in range(T):

        if mode == "stable":
            frame = np.sin(X + 0.1*t)

        elif mode == "interference":
            frame = np.sin(X + 0.1*t) + np.sin(Y - 0.1*t)

        elif mode == "chaotic":
            frame = np.sin(X + 0.1*t) + np.random.normal(0, 0.5, (N,N))

        field.append(frame)

    return np.array(field)
