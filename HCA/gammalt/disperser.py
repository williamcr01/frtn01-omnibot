import numpy as np

def harmonic_array(x, t, T, H):
    #x - signal (vector)
    #t - time vector
    #T - time window
    #H - number of harmonic elements
    omega = 2 * np.pi / T
    X_harmonic = np.zeros((H + 1, len(t)), dtype=complex)

    for k in range(len(t)):
        tk = t[k]
        idx = (t >= (tk - T)) & (t <= tk)
        tau = t[idx]
        x_segment = x[idx]

        for h in range(H + 1):
            exponential = np.exp(-1j * h * omega * tau)
            #integral = np.trapz(x_segment * exponential, tau)
            integral = np.trapezoid(x_segment * exponential, tau)
            X_harmonic[h, k] = (1 / T) * integral

    return X_harmonic



