import time
import matplotlib.pyplot as plt
from RefGen_For_PID import RefGen
from PI import PI
import numpy as np
import sys

dt_control = 0.4
dt_refgen = 0.4
num_points = 50
period = dt_refgen*num_points
H = 2
N = round((dt_refgen*num_points)/dt_control)

H_parts = H + 1

def main():
    
    refgen = RefGen(dt=dt_refgen, num_points=num_points)
    refgen.OnOffInput()
    
    pi = PI(refgen=refgen, N=N, H=H, dt=dt_control, period=period, dt_refgen=dt_refgen)

    refgen.start()
    time.sleep(1) # calculate buffer
    pi.start()

    fig, axs = plt.subplots(4, 2, sharex=True, figsize=(12, 8))
    (ax1, ax2), (ax3, ax4), (ax5, ax6), (ax7, ax8) = axs

    labels1 = ['x', 'x_ref', 'x_err']
    labels2 = ['y', 'y_ref', 'y_err']
    labels3 = [f'x re {i}' for i in range(H_parts)]
    labels4 = [f'x im {i}' for i in range(H_parts)]
    labels5 = [f'y re {i}' for i in range(H_parts)]
    labels6 = [f'y im {i}' for i in range(H_parts)]
    labels7 = [f'theta re {i}' for i in range(H_parts)]
    labels8 = [f'theta im {i}' for i in range(H_parts)]

    lines1 = [ax1.plot([], [], label=label)[0] for label in labels1]
    lines2 = [ax2.plot([], [], label=label)[0] for label in labels2]
    lines3 = [ax3.plot([], [], label=label)[0] for label in labels3]
    lines4 = [ax4.plot([], [], label=label)[0] for label in labels4]
    lines5 = [ax5.plot([], [], label=label)[0] for label in labels5]
    lines6 = [ax6.plot([], [], label=label)[0] for label in labels6]
    lines7 = [ax7.plot([], [], label=label)[0] for label in labels7]
    lines8 = [ax8.plot([], [], label=label)[0] for label in labels8]

    axes = [ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8]
    ylabels = [
        'X signals', 'Y signals',
        'X real parts', 'X imaginary parts',
        'Y real parts', 'Y imaginary parts',
        'Theta real parts', 'Theta imaginary parts'
    ]
    legend_kwargs = dict(loc='center left', bbox_to_anchor=(1, 0.5))

    for ax, label in zip(axes, ylabels):
        ax.set_ylabel(label)
        ax.legend(**legend_kwargs)
        ax.grid(True)

    ax8.set_xlabel('Time (s)')

    time_data = []
    x_signals = [[] for _ in labels1]
    y_signals = [[] for _ in labels2]
    x_re_signals = [[] for _ in labels3]
    x_im_signals = [[] for _ in labels4]
    y_re_signals = [[] for _ in labels5]
    y_im_signals = [[] for _ in labels6]
    theta_re_signals = [[] for _ in labels7]
    theta_im_signals = [[] for _ in labels8]

    fig.subplots_adjust(wspace=0.5)

    start_time = time.time()
    try:
        while plt.fignum_exists(fig.number):
            t = time.time() - start_time

            x = pi.x
            x_ref = pi.x_ref
            x_err = x_ref - x

            y = pi.y
            y_ref = pi.y_ref
            y_err = y_ref - y

            time_data.append(t)

            x_vals = [x, x_ref, x_err]
            y_vals = [y, y_ref, y_err]

            for i in range(H_parts):
                x_re_signals[i].append(np.real(pi.dispersions_x[i]))
                x_im_signals[i].append(np.imag(pi.dispersions_x[i]))
                y_re_signals[i].append(np.real(pi.dispersions_y[i]))
                y_im_signals[i].append(np.imag(pi.dispersions_y[i]))
                theta_re_signals[i].append(np.real(pi.dispersions_theta[i]))
                theta_im_signals[i].append(np.imag(pi.dispersions_theta[i]))

            for i in range(H_parts):
                lines3[i].set_data(time_data, x_re_signals[i])
                lines4[i].set_data(time_data, x_im_signals[i])
                lines5[i].set_data(time_data, y_re_signals[i])
                lines6[i].set_data(time_data, y_im_signals[i])
                lines7[i].set_data(time_data, theta_re_signals[i])
                lines8[i].set_data(time_data, theta_im_signals[i])

            for i in range(3):
                x_signals[i].append(x_vals[i])
                y_signals[i].append(y_vals[i])
                lines1[i].set_data(time_data, x_signals[i])
                lines2[i].set_data(time_data, y_signals[i])

            for ax in axes:
                ax.relim()
                ax.autoscale_view()

            plt.draw()
            plt.pause(0.01) 

    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        print("Shutting down...")
        pi.stop()
        refgen.stop()
        plt.close('all')
        sys.exit(0)       

if __name__ == "__main__":
    main()
