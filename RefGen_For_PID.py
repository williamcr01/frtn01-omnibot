import threading
import time
import numpy as np

class RefGen(threading.Thread):
    def __init__(self, amplitude=1.0, frequency=1.0, dt=0.2, num_points=100):
        super().__init__()
        self.running = True
        self.updateFlag = False
        self.botIsRunning = False

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
            #y = A * np.sin(t)
            dx = -A * np.sin(t)
            dy = A * (np.cos(t)**2 - np.sin(t)**2)
            #dy = A * np.cos(t)
            #theta = np.arctan2(dy, dx)
            theta = 0
            self.refBuffer.append((x, y, theta))

    def getRefPoints(self):
        return [self.refXValue, self.refYValue, self.thetaRefValue]

    def OnOffInput(self):
        self.updateFlag = not self.updateFlag

    def botRunning(self, run):
        self.botIsRunning = run

    def restart(self):
        self.index = 0

    def run(self):
        print(
            f"RefX: {self.refBuffer[self.index][0]:.3f}, RefY: {self.refBuffer[self.index][1]:.3f}, Theta: {np.rad2deg(self.refBuffer[self.index][2]):.2f}°",
            flush=True
            )
        next_time = time.time()
        while self.running:
            if self.updateFlag and self.botIsRunning:
                x, y, theta = self.refBuffer[self.index]
                self.refXValue = x
                self.refYValue = y
                self.thetaRefValue = theta

                #print(f"RefX: {x:.3f}, RefY: {y:.3f}, Theta: {np.rad2deg(theta):.2f}°", flush=True)

                self.index += 1
                if self.index >= self.num_points:
                    self.index = 0  # Loop forever

                # Control loop fixed time
                next_time += self.dt
                sleep_time = next_time - time.time()
                if sleep_time > 0:
                    time.sleep(sleep_time)
                else:
                    print(f"Warning: RefGen loop overran desired time by {-sleep_time} seconds")
                    next_time = time.time()

    def stop(self):
        self.running = False
        self.join()
