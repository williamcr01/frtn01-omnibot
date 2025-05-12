import time

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

if __name__ == "__main__":
    main()
