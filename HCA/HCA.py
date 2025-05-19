import numpy as np
import matplotlib.pyplot as plt


def initialize_disperser(H, N):
    buffer = np.zeros(N)
    dispersions = np.zeros(H + 1, dtype=complex)
    n = 0  # current sample index

    # Precompute one full cycle of exponential factors
    exp_factors = np.array(
        [np.exp(-1j * 2 * np.pi * h * np.arange(N) / N) / N for h in range(H + 1)]
    )

    return buffer, dispersions, exp_factors, n


def update_disperser(e_n, buffer, dispersions, exp_factors, n):
    N = len(buffer)
    old_e = buffer[n % N]
    buffer[n % N] = e_n  # Update circular buffer

    for h in range(len(dispersions)):
        # Recursive update
        dispersions[h] += (e_n - old_e) * exp_factors[h][n % N]

    return dispersions, (n + 1)

def test():
    # Parameters
    T = 1.0  # Period in seconds
    Ts = 0.01  # Sampling time
    N = int(T / Ts)
    H = 4  # Max harmonic

    # Initialize
    buffer, dispersions, exp_factors, n = initialize_disperser(H, N)

    # Simulate a signal

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

def test_HCA():
    T = 1.0      # Period in seconds
    Ts = 0.05    # Sampling time
    N = int(T / Ts)
    H = 4        # Max harmonic
    duration = 2 * T
    t = np.arange(0, duration, Ts)

    # Signals (x, y, theta)
    x_signal = np.sin(1.1* 2 * np.pi * t) + 0.5 * np.sin(4 * np.pi * t)        # 1 Hz + 2 Hz
    y_signal = np.cos(2 * np.pi * t) + 0.3 * np.sin(6 * np.pi * t)        # 1 Hz + 3 Hz
    theta_signal = 0.8 * np.sin(2 * np.pi * t) + 0.4 * np.sin(8 * np.pi * t)  # 1 Hz + 4 Hz

    signals = {'x': x_signal, 'y': y_signal, 'theta': theta_signal}
    assembled_signals = {'x': [], 'y': [], 'theta': []}
    dispersions_histories = {}

    # Initialize dispersers
    dispersers = {}
    for label in signals:
        buffer, dispersions, exp_factors, n = initialize_disperser(H, N)
        dispersers[label] = {'buffer': buffer, 'disp': dispersions, 'exp': exp_factors, 'n': n}
        dispersions_histories[label] = []

    # Loop over time
    for i in range(len(t)):
        # Update dispersers
        for label, signal in signals.items():
            e_n = signal[i]
            d = dispersers[label]
            d['disp'], d['n'] = update_disperser(
                e_n, d['buffer'], d['disp'], d['exp'], d['n']
            )
            dispersions_histories[label].append(d['disp'].copy())

        # Assemble
        n_val = dispersers['x']['n']  # all n values are assumed equal
        harmonics = np.arange(H + 1)
        phase_vector = np.exp(1j * 2 * np.pi * harmonics * n_val / N)

        dx = dispersers['x']['disp']
        dy = dispersers['y']['disp']
        dtheta = dispersers['theta']['disp']

        xdot = np.real(dx[0] + 2 * np.sum(dx[1:] * phase_vector[1:]))
        ydot = np.real(dy[0] + 2 * np.sum(dy[1:] * phase_vector[1:]))
        thetadot = np.real(dtheta[0] + 2 * np.sum(dtheta[1:] * phase_vector[1:]))

        assembled_signals['x'].append(xdot)
        assembled_signals['y'].append(ydot)
        assembled_signals['theta'].append(thetadot)

    # Convert lists to arrays
    for label in dispersions_histories:
        dispersions_histories[label] = np.array(dispersions_histories[label])
    for label in assembled_signals:
        assembled_signals[label] = np.array(assembled_signals[label])

    # Plotting
    fig, axs = plt.subplots(3, 5, figsize=(18, 12), sharex=True)
    signal_labels = ['x', 'y', 'theta']

    for row, label in enumerate(signal_labels):
        # Original signal
        axs[row][0].plot(t, signals[label])
        axs[row][0].set_title(f"Original {label}")

        # Dispersion magnitudes
        for h in range(H + 1):
            axs[row][1].plot(t, np.real(dispersions_histories[label][:, h]), label=f"h={h}")
        axs[row][1].set_title(f"Dispersion Real Part {label}")
        axs[row][1].legend()

        # Dispersion magnitudes
        for h in range(H + 1):
            axs[row][2].plot(t, np.imag(dispersions_histories[label][:, h]), label=f"h={h}")
        axs[row][2].set_title(f"Dispersion Imag Part {label}")
        axs[row][2].legend()

        # Dispersion magnitudes
        for h in range(H + 1):
            axs[row][3].plot(t, np.abs(dispersions_histories[label][:, h]), label=f"h={h}")
        axs[row][3].set_title(f"Dispersion Magnitude {label}")
        axs[row][3].legend()

        # Assembled signal
        axs[row][4].plot(t, assembled_signals[label])
        axs[row][4].set_title(f"Assembled {label}")

        for col in range(5):
            axs[row][col].grid(True)

    axs[2][0].set_xlabel("Time (s)")
    axs[2][1].set_xlabel("Time (s)")
    axs[2][2].set_xlabel("Time (s)")
    axs[2][3].set_xlabel("Time (s)")
    axs[2][4].set_xlabel("Time (s)")
    plt.tight_layout()
    plt.show()
