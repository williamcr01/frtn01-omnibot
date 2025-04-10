import threading
import time

class RefGen(threading.Thread):
    def __init__(self):
        super().__init__()
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

    def run(self):
        while True:
            if(self.updateFlag):
                if(self.currentIndex < 500):
                    self.refXValue = self.refXpos[self.currentIndex]
                else:
                    self.refXValue = self.refXneg[self.currentIndex - 500]
                
                self.refYValue = self.refY[self.currentIndex]
                self.currentIndex += 1

                print(f"RefX: {self.refXValue}, RefY: {self.refYValue}")
            time.sleep(0.100)

    

