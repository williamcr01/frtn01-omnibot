import time
import matplotlib.pyplot as plt
from RefGen_buffer import RefGen
from PI import PI

H = 0
N = 1

def main():
    
    refgen = RefGen()
    refgen.OnOffInput()
    
    pi = PI(refgen=refgen, N=N, H=H)

    refgen.start()
    time.sleep(1) # calculate buffer
    pi.start()

    # Graphs to see error
    plt.iob()

    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(10, 6))

    labels1 = ['x', 'x_ref', 'x_err']
    labels2 = ['y', 'y_ref', 'y_err']
    lines1 = [ax1.plot([], [], label=label)[0] for label in labels1]
    lines2 = [ax2.plot([], [], label=label)[0] for label in labels2]

    ax1.set_ylabel('X signals')
    ax2.set_ylabel('Y signals')
    ax2.set_xlabel('Time (s)')
    ax1.legend()
    ax2.legend()
    ax1.grid(True)
    ax2.grid(True)

    # Data buffers
    time_data = []
    x_signals = [[] for _ in labels1]
    y_signals = [[] for _ in labels2]

    start_time = time.time()

    while True:
        t = time.time() - start_time

        x = pi.x
        x_ref = pi.x_ref
        x_err = x_ref - x

        y = pi.y
        y_ref = pi.y_ref
        y_err = y_ref - x

        time_data.append(t)
        x_vals = [x, x_ref, x_err]
        y_vals = [y, y_ref, y_err]

        for i in range(3):
            x_signals[i].append(x_vals[i])
            y_signals[i].append(y_vals[i])
            lines1[i].set_data(time_data, x_signals[i])
            lines2[i].set_data(time_data, y_signals[i])
            
        # Rescale axes
        ax1.relim()
        ax1.autoscale_view()
        ax2.relim()
        
        plt.draw()
        plt.pause(0.1)        

if __name__ == "__main__":
    main()
