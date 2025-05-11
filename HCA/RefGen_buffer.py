import threading
import time
import numpy as np

class RefGen(threading.Thread):
    def __init__(self, amplitude=1.0, frequency=1.0, dt=0.1, num_points=100):
        super().__init__()
        self.running = True
        self.updateFlag = False

        self.refXValue = 0
        self.refYValue = 0
        self.thetaRefValue = 0

        self.amplitude = amplitude
        self.frequency = frequency  # in Hz
        self.dt = dt
        self.num_points = num_points

        self.refBuffer = []  # Precomputed list of (x, y, theta)
        self.index = 0

        self._generate_reference_path()
        #print(self.refBuffer)

    def _generate_reference_path(self):
        A = self.amplitude
        omega = 2 * np.pi * self.frequency
        t_vals = np.linspace(0, 2 * np.pi, self.num_points)

        for t in t_vals:
            x = A * np.cos(t)
            y = A * np.sin(t) * np.cos(t)
            dx = -A * np.sin(t)
            dy = A * (np.cos(t)**2 - np.sin(t)**2)
            theta = np.arctan2(dy, dx)
            self.refBuffer.append((x, y, theta))

    def getRefPoints(self):
        return [self.refXValue, self.refYValue, self.thetaRefValue]

    def OnOffInput(self):
        self.updateFlag = not self.updateFlag

    def restart(self):
        self.index = 0

    def run(self):
        while self.running:
            if self.updateFlag:
                x, y, theta = self.refBuffer[self.index]
                self.refXValue = x
                self.refYValue = y
                self.thetaRefValue = theta

                print(f"RefX: {x:.3f}, RefY: {y:.3f}, Theta: {np.rad2deg(theta):.2f}°", flush=True)

                self.index += 1
                if self.index >= self.num_points:
                    self.index = 0  # Loop forever

                time.sleep(self.dt)

    def stop(self):
        self.running = False
