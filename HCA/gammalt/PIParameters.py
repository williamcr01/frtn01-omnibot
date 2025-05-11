import copy

class PIParameters():
    
    def __init__(self, K=0.0, Ti=0.0, Tr=0.0, Beta=0.0, H=0.0, integrator_on=False):
        self.K = K
        self.Ti = Ti
        self.Tr = Tr
        self.Beta = Beta
        self.H = H
        self.integrator_on = integrator_on

    def clone(self):
        return copy.deepcopy(self)