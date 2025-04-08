import HCA.PIParameters as PIParameters

class PI():

    def __init__(self):
        self.I = 0.0
        self.v = 0.0
        self.e = 0.0
        self.p = PIParameters(K=1.0, Ti=0.0, Tr=10.0, Beta=1.0, H=1.0, integratorOn=True)

    def calculateOutput(self, y, yref):
        self.e = yref - y;
        self.v = self.p.K * (self.p.Beta * yref - y) + self.I;
        return self.v;

    def updateState(self, u):
        if self.p.integratorOn:
            self.I = self.I + (self.p.K * self.p.H / self.p.Ti) * self.e + (self.p.H / self.p.Tr) * (u - self.v);
        else:
            self.I = 0.0;
    
    def getHMillis(self):
        return self.p.H * 1000

    def setParameters(self, PIparams):
        self.p = PIparams.clone()
        if not self.p.integratorOn:
           self.I = 0.0
           

    
