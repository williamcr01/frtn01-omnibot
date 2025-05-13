import time
import matplotlib.pyplot as plt
from RefGen_buffer import RefGen
from PI import PI
import HCA as hca

H = 5
N = 40

def main():
    
    #refgen = RefGen()
    #refgen.OnOffInput()
    
    #pi = PI(refgen=refgen, N=N, H=H)

    #refgen.start()
    #time.sleep(1) # calculate buffer
    #pi.start()

    hca.test_HCA()

main()

