import threading

class RefGen():
    # Reference generator to generate a signal for moving in a straight line
    def __init__(self):
        self.xCurr = 0.0
        self.yCurr = 0.0
        self.xTarget = 0.0
        self.yTarget = 0.0

    def set_target(self, newXTarget, newYTarget):
        self.xTarget = newXTarget
        self.yTarget = newYTarget

    def set_current(self, newXCurr, newYCurr):
        self.xCurr = newXCurr
        self.yCurr = newYCurr

    def get_ref(self):
        return self.xRef, self.yRef

    def run(self):
        while True:
            #TODO: få botten att feeda sin position hela tiden
            dx = self.xTarget - self.xCurr
            dy = self.yTarget - self.yCurr

    def start(self):
        pass
