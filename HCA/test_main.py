from refgen import RefGen
import disperser as disperser
import assembler as assembler
import time
import matplotlib.pyplot as plt
import numpy as np

def main():
    x_ref_arr = np.array([])
    y_ref_arr = np.array([])
    sample = np.array([])
    i = 0
    refgen = RefGen()
    #gui = GUI(refgen=refgen)
    refgen.start()
    #refgen.OnOffInput()
    time.sleep(1) # give refgen time to start up

    while True:
        i = i + 1
        x_ref, y_ref = refgen.get_ref()
        x_ref_arr = np.append(x_ref_arr, x_ref)
        y_ref_arr = np.append(y_ref_arr, y_ref)
        sample = np.append(sample, i)
        if x_ref < 0.001 and y_ref < 0.001:
            refgen.set_running() # on
            break
        time.sleep(0.05)

    plt.plot(sample, x_ref_arr)
    plt.savefig("myplot.png")
    refgen.set_running() # off



main()
