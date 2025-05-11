import time

from RefGen_buffer import RefGen
from PI import PI

def main():
    
    refgen = RefGen()
    #refgen.OnOffInput()
    
    pi = PI(refgen=refgen)

    refgen.start()
    time.sleep(1) # calculate buffer
    pi.start()

if __name__ == "__main__":
    main()
