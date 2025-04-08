import copy

class PIParameters():
    
    def __init__(self, K=0.0, Ti=0.0, Tr=0.0, Beta=0.0, H=0.0, integratorOn=False):
        self.K = K
        self.Ti = Ti
        self.Tr = Tr
        self.Beta = Beta
        self.H = H
        self.integrator_on = integratorOn

    def clone(self):
        return copy.deepcopy(self)