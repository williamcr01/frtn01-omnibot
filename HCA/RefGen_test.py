import threading
import time
import numpy as np

class RefGen(threading.Thread):
    def __init__(self, amplitude=1.0, frequency=1.0, dt=0.04):
        super().__init__()
        self.running = True
        self.updateFlag = False

        self.refXValue = 0
        self.refYValue = 0
        self.thetaRefValue = 0

        self.amplitude = amplitude
        self.frequency = frequency  # in Hz
        self.dt = dt

        self.t = 0  # time index in radians

    def getRefPoints(self):
        return [self.refXValue, self.refYValue, self.thetaRefValue]

    def OnOffInput(self):
        self.updateFlag = not self.updateFlag

    def restart(self):
        self.t = 0

    def run(self):
        while self.running:
            if self.updateFlag:
                # Lemniscate of Gerono
                A = self.amplitude
                omega = 2 * np.pi * self.frequency
                x = A * np.cos(self.t)
                y = A * np.sin(self.t) * np.cos(self.t)

                self.refXValue = x
                self.refYValue = y

                # Optional: thetaRefValue as angle of velocity vector
                dx = -A * np.sin(self.t)
                dy = A * (np.cos(self.t)**2 - np.sin(self.t)**2)
                self.thetaRefValue = np.arctan2(dy, dx)

                print(f"RefX: {x:.3f}, RefY: {y:.3f}, Theta: {np.rad2deg(self.thetaRefValue):.2f}°", flush=True)

                self.t += omega * self.dt
                if self.t >= 2 * np.pi:
                    self.t -= 2 * np.pi

                time.sleep(self.dt)

    def stop(self):
        self.running = False
