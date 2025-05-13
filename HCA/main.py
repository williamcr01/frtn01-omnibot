import time
import matplotlib.pyplot as plt
from RefGen_buffer import RefGen
from PI import PI
import numpy as np

H = 2
N = 40

H_parts = H + 1

def main():
    
    refgen = RefGen()
    refgen.OnOffInput()
    
    pi = PI(refgen=refgen, N=N, H=H)

    refgen.start()
    time.sleep(1) # calculate buffer
    pi.start()

    # Graphs to see error
    plt.ion()

    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, sharex=True, figsize=(12, 10))

    labels1 = ['x', 'x_ref', 'x_err']
    labels2 = ['y', 'y_ref', 'y_err']
    labels3 = []
    labels4 = []
    for i in range(H_parts):
        labels3.append(f'x re {i}')
        labels4.append(f'x im {i}')
    lines1 = [ax1.plot([], [], label=label)[0] for label in labels1]
    lines2 = [ax2.plot([], [], label=label)[0] for label in labels2]
    lines3 = [ax3.plot([], [], label=label)[0] for label in labels3]
    lines4 = [ax4.plot([], [], label=label)[0] for label in labels4]

    ax1.set_ylabel('X signals')
    ax2.set_ylabel('Y signals')
    ax3.set_ylabel('X real parts')
    ax4.set_ylabel('X imaginary parts')
    ax4.set_xlabel('Time (s)')
    ax1.legend()
    ax2.legend()
    ax3.legend()
    ax4.legend()
    ax1.grid(True)
    ax2.grid(True)
    ax3.grid(True)
    ax4.grid(True)

    # Data buffers
    time_data = []
    x_signals = [[] for _ in labels1]
    y_signals = [[] for _ in labels2]
    x_re_signals = [[] for _ in labels3]
    x_im_signals = [[] for _ in labels4]

    start_time = time.time()

    while True:
        t = time.time() - start_time

        x = pi.x
        x_ref = pi.x_ref
        x_err = x_ref - x

        y = pi.y
        y_ref = pi.y_ref
        y_err = y_ref - y

        re_1 = np.real(pi.dispersions_x[2])
        re_2 = np.imag(pi.dispersions_x[2])

        time_data.append(t)
        x_vals = [x, x_ref, x_err]
        y_vals = [y, y_ref, y_err]
        re_vals = [re_1, re_2]

        for i in range(H_parts):
            x_re_signals[i].append(np.real(pi.dispersions_x[i]))
            x_im_signals[i].append(np.imag(pi.dispersions_x[i]))

        for i in range(H_parts):
            lines3[i].set_data(time_data, x_re_signals[i])
            lines4[i].set_data(time_data, x_im_signals[i])

        for i in range(3):
            x_signals[i].append(x_vals[i])
            y_signals[i].append(y_vals[i])
            lines1[i].set_data(time_data, x_signals[i])
            lines2[i].set_data(time_data, y_signals[i])

        """ for i in range(2):
            x_re_signals[i].append(re_vals[i])
            lines3[i].set_data(time_data, x_re_signals[i]) """
            
        # Rescale axes
        ax1.relim()
        ax1.autoscale_view()
        ax2.relim()
        ax2.autoscale_view()
        ax3.relim()
        ax3.autoscale_view()
        ax4.relim()
        ax4.autoscale_view()
        
        plt.draw()
        plt.pause(0.01)        

if __name__ == "__main__":
    main()
