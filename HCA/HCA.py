import numpy as np


def initialize_disperser(H, N):
    """
    Initializes buffers and exponential lookup table for all harmonics.

    Returns:
        buffer: circular buffer of shape (N,)
        dispersions: current harmonic values, shape (H + 1,)
        exp_factors: precomputed exponential factors of shape (H + 1,)
    """
    buffer = np.zeros(N)
    dispersions = np.zeros(H + 1, dtype=complex)
    n = 0  # current sample index

    # Precompute one full cycle of exponential factors
    exp_factors = np.array(
        [np.exp(-1j * 2 * np.pi * h * np.arange(N) / N) / N for h in range(H + 1)]
    )

    return buffer, dispersions, exp_factors, n


def update_disperser(e_n, buffer, dispersions, exp_factors, n):
    """
    Updates the dispersion vector with new sample e_n.

    Returns:
        Updated dispersions and updated index n.
    """
    N = len(buffer)
    old_e = buffer[n % N]
    buffer[n % N] = e_n  # Update circular buffer

    for h in range(len(dispersions)):
        # Recursive update
        dispersions[h] += (e_n - old_e) * exp_factors[h][n % N]

    return dispersions, (n + 1)

def test():
    # --- Example Usage ---
    # Parameters
    T = 1.0  # Period in seconds
    Ts = 0.01  # Sampling time
    N = int(T / Ts)
    H = 4  # Max harmonic

    # Initialize
    buffer, dispersions, exp_factors, n = initialize_disperser(H, N)

    # Simulate a signal
    import matplotlib.pyplot as plt

    t = np.arange(0, 2 * T, Ts)
    e_signal = np.sin(2 * np.pi * t) + 0.5 * np.sin(4 * np.pi * t)  # 1 Hz + 2 Hz
    print(e_signal)
    disp_history = []

    for e_n in e_signal:
        dispersions, n = update_disperser(e_n, buffer, dispersions, exp_factors, n)
        disp_history.append(dispersions.copy())

    # Plot magnitude of harmonics over time
    disp_history = np.array(disp_history)
    plt.figure()
    for h in range(H + 1):
        plt.plot(t, np.abs(disp_history[:, h]), label=f"h={h}")
    plt.legend()
    plt.title("Magnitude of Harmonic Components")
    plt.xlabel("Time (s)")
    plt.ylabel("Magnitude")
    plt.grid()
    plt.show()
