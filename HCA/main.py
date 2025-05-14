import time
import matplotlib.pyplot as plt
from RefGen_buffer import RefGen
from PI import PI
import numpy as np
import sys

dt_control = 0.25
dt_refgen = 0.3
num_points = 100
period = dt_refgen*num_points
H = 1
N = round((dt_refgen*num_points)/dt_control)

H_parts = H + 1

def main():
    
    refgen = RefGen(dt=dt_refgen, num_points=num_points)
    refgen.OnOffInput()
    
    pi = PI(refgen=refgen, N=N, H=H, dt=dt_control, period=period, dt_refgen=dt_refgen)

    refgen.start()
    time.sleep(1) # calculate buffer
    pi.start()

    # Graphs to see error
    plt.ion()

    fig, (ax1, ax2, ax3, ax4, ax5, ax6) = plt.subplots(6, 1, sharex=True, figsize=(10, 8))

    labels1 = ['x', 'x_ref', 'x_err']
    labels2 = ['y', 'y_ref', 'y_err']
    labels3 = []
    labels4 = []
    labels5 = []
    labels6 = []
    for i in range(H_parts):
        labels3.append(f'x re {i}')
        labels4.append(f'x im {i}')
        labels5.append(f'y re {i}')
        labels6.append(f'y im {i}')
    lines1 = [ax1.plot([], [], label=label)[0] for label in labels1]
    lines2 = [ax2.plot([], [], label=label)[0] for label in labels2]
    lines3 = [ax3.plot([], [], label=label)[0] for label in labels3]
    lines4 = [ax4.plot([], [], label=label)[0] for label in labels4]
    lines5 = [ax5.plot([], [], label=label)[0] for label in labels5]
    lines6 = [ax6.plot([], [], label=label)[0] for label in labels6]

    ax1.set_ylabel('X signals')
    ax2.set_ylabel('Y signals')
    ax3.set_ylabel('X real parts')
    ax4.set_ylabel('X imaginary parts')
    ax5.set_ylabel('Y real parts')
    ax6.set_ylabel('Y imaginary parts')
    ax6.set_xlabel('Time (s)')
    ax1.legend()
    ax2.legend()
    ax3.legend()
    ax4.legend()
    ax5.legend()
    ax6.legend()
    ax1.grid(True)
    ax2.grid(True)
    ax3.grid(True)
    ax4.grid(True)
    ax5.grid(True)
    ax6.grid(True)

    # Data buffers
    time_data = []
    x_signals = [[] for _ in labels1]
    y_signals = [[] for _ in labels2]
    x_re_signals = [[] for _ in labels3]
    x_im_signals = [[] for _ in labels4]
    y_re_signals = [[] for _ in labels5]
    y_im_signals = [[] for _ in labels6]

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

            #re_1 = np.real(pi.dispersions_x[2])
            #re_2 = np.imag(pi.dispersions_x[2])

            time_data.append(t)
            x_vals = [x, x_ref, x_err]
            y_vals = [y, y_ref, y_err]
            #re_vals = [re_1, re_2]

            for i in range(H_parts):
                x_re_signals[i].append(np.real(pi.dispersions_x[i]))
                x_im_signals[i].append(np.imag(pi.dispersions_x[i]))
                y_re_signals[i].append(np.real(pi.dispersions_y[i]))
                y_im_signals[i].append(np.imag(pi.dispersions_y[i]))

            for i in range(H_parts):
                lines3[i].set_data(time_data, x_re_signals[i])
                lines4[i].set_data(time_data, x_im_signals[i])
                lines5[i].set_data(time_data, y_re_signals[i])
                lines6[i].set_data(time_data, y_im_signals[i])

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
            ax5.relim()
            ax5.autoscale_view()
            ax6.relim()
            ax6.autoscale_view()
            
            plt.draw()
            plt.pause(0.01) 

    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        print("Shutting down...")
        # Gracefully stop any threads or processes
        pi.stop()
        refgen.stop()
        plt.close('all')
        sys.exit(0)       

if __name__ == "__main__":
    main()
