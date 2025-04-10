import threading
import time

class RefGen(threading.Thread):
    def __init__(self):
        super().__init__()
        self.running = True
        self.refXpos = []
        self.refXneg = []
        self.refY = []  
        self.currentIndex = 0

        self.refXValue = 0
        self.refYValue = 0

        self.updateFlag = False



    def setRefPoints(self, refXpos, refXneg, refY):
        self.refXpos = refXpos
        self.refXneg = refXneg
        self.refY = refY
        self.updateFlag = True

    def getRefPoints(self):
        return [self.refXValue, self.refYValue]

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
                
                self.currentIndex += 1
                if(self.currentIndex >= 1000):
                    self.currentIndex = 0

                print(f"RefX: {self.refXValue}, RefY: {self.refYValue}")

                time.sleep(0.01)
    def stop(self):
        self.running = False

    

