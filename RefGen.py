import threading
import time
import numpy as np

class RefGen(threading.Thread):
    def __init__(self):
        super().__init__()
        self.running = True
        self.refXpos = []
        self.refXneg = []
        self.refY = []  
        self.currentIndex = 250

        self.refXValue = 0
        self.refYValue = 0
        self.thetaRefValue = 0

        self.updateFlag = False



    def setRefPoints(self, refXpos, refXneg, refY):
        self.refXpos = refXpos
        self.refXneg = refXneg
        self.refY = refY

    def getRefPoints(self):
        return [self.refXValue, self.refYValue, self.thetaRefValue]
    
    def OnOffInput(self):
        if(self.updateFlag):
            self.updateFlag = False
        else:
            self.updateFlag = True

    def restart(self):
        self.currentIndex = 250
        self.refXValue = self.refXpos[250]
        self.refYValue = self.refY[250]

    def run(self):
        while self.running:
            if(self.updateFlag):
                print(len(self.refY))
                print(len(self.refXpos))
                print(len(self.refXneg))
                print(self.currentIndex)

                if(self.currentIndex < 250): #Bottom right
                    self.refXValue = self.refXpos[self.currentIndex]
                
                elif(self.currentIndex >= 250 and self.currentIndex < 500):#top left
                    self.refXValue = self.refXneg[self.currentIndex]
                
                elif(self.currentIndex >= 500 and self.currentIndex < 750):#top right
                    self.refXValue = self.refXpos[500 - self.currentIndex]

                elif(self.currentIndex >= 750 and self.currentIndex < 1000):
                    self.refXValue = self.refXneg[1000 - self.currentIndex]

                if(self.currentIndex < 500):
                    self.refYValue = self.refY[self.currentIndex]
                else:
                    self.refYValue = self.refY[999 - self.currentIndex]
                
                #self.thetaRefValue += np.deg2rad(0.5)

                #if(self.thetaRefValue >= 2 * np.pi):
                #    self.thetaRefValue = 0
                self.currentIndex += 1
                if(self.currentIndex >= 1000):
                    self.currentIndex = 0

                print(f"RefX: {self.refXValue}, RefY: {self.refYValue}")

                time.sleep(0.04)
    def stop(self):
        self.running = False

    

