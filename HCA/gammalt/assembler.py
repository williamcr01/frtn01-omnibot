import numpy as np

def harmonic_assembler(X_harmonic, t, T):
    omega = 2 * np.pi / T
    H = X_harmonic.shape[0] - 1  # Number of harmonics

    X_reconstructed = np.zeros(len(t))

    for k in range(len(t)):
        tk = t[k]
        sum_val = 0
        for h in range(-H, H + 1):
            idx = abs(h)  # Indexing into harmonic matrix (abs for symmetry)
            if h < 0:
                Xh = np.conj(X_harmonic[idx, k])
            else:
                Xh = X_harmonic[h, k]
            sum_val += Xh * np.exp(1j * h * omega * tk)
        
        X_reconstructed[k] = np.real(sum_val)  # Optional: take real part

    return X_reconstructed
