import HCA.PIParameters as PIParameters

class PI():

    def __init__(self, H):
        self.I = 0.0
        self.v = 0.0
        self.e = 0.0
        self.H = H
        self.p = PIParameters(K=1.0, Ti=0.0, Tr=10.0, Beta=1.0, H=self.H, integrator_on=False)

    def calculate_output(self, y, yref):
        self.e = yref - y;
        self.v = self.p.K * (self.p.Beta * yref - y) + self.I;
        return self.v;

    def update_state(self, u):
        if self.p.integrator_on:
            self.I = self.I + (self.p.K * self.p.H / self.p.Ti) * self.e + (self.p.H / self.p.Tr) * (u - self.v);
        else:
            self.I = 0.0;
    
    def get_H_millis(self):
        return self.p.H * 1000

    def set_parameters(self, PIparams):
        self.p = PIparams.clone()
        if not self.p.integrator_on:
           self.I = 0.0
           

    
