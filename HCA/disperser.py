import numpy as np
import threading

class Disperser(threading.Thread):
    
    def __init__(self):
        super().__init__()