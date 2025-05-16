import numpy as np
import time
import threading
from omnibot.tcp import Connection

# Robot Parameters
r = 0.028 * 0.45 / 18  # Wheel radius (meters)
R = 0.16               # Distance from center to wheels (meters)

# Proportional and Integral Gains
KpX = 3.5
KpY = 3.0
Kptheta = 3.0

KiX = 0.08
KiY = 0.08
Kitheta = 0.2

KdX = 0.8
KdY = 0.8
Kdtheta = 0.01

#Kpx = 3.5, KpY = 3.0, Kptheta = 3.0, KiX = 0.13, KiY = 0.13, Kitheta = 0.2, KdX = 0.7, KdY = 0.7, Kdtheta = 0.01 -> AVGDistError:0.130m
#Kpx = 3.0, KpY = 2.7, Kptheta = 3.0, KiX = 0.13, KiY = 0.13, Kitheta = 0.2, KdX = 0.5, KdY = 0.5, Kdtheta = 0.01 -> AVGDistError:0.115m
#Kpx = 3.0, KpY = 2.7, Kptheta = 3.0, KiX = 0.15, KiY = 0.15, Kitheta = 0.2, KdX = 0.5, KdY = 0.5, Kdtheta = 0.01 -> AVGDistError:0.130m
#Kpx = 3.0, KpY = 2.7, Kptheta = 3.0, KiX = 0.10, KiY = 0.10, Kitheta = 0.2, KdX = 0.5, KdY = 0.5, Kdtheta = 0.01 -> AVGDistError:0.120m
#Kpx = 3.5, KpY = 3.0, Kptheta = 3.0, KiX = 0.07, KiY = 0.07, Kitheta = 0.2, KdX = 1.0, KdY = 1.0, Kdtheta = 0.01 -> AVGDistError:0.110m
#Kpx = 3.2, KpY = 2.8, Kptheta = 3.0, KiX = 0.08, KiY = 0.08, Kitheta = 0.2, KdX = 1.2, KdY = 1.2, Kdtheta = 0.01 -> AVGDistError:0.130m

#Kpx = 3.5, KpY = 3.0, Kptheta = 3.0, KiX = 0.08, KiY = 0.08, Kitheta = 0.2, KdX = 0.8, KdY = 0.8, Kdtheta = 0.01 -> AVGDistError:0.110m <--

#Kpx = 3.5, KpY = 3.0, Kptheta = 2.5, KiX = 0.08, KiY = 0.08, Kitheta = 0.2, KdX = 0.8, KdY = 0.8, Kdtheta = 0.01 -> AVGDistError:0.110m



# Anti-windup limit
INTEGRAL_LIMIT = 1.0

# Inverse Kinematics Matrix Function
def inverse_kinematics(theta, xdot, ydot, thetadot):
    J_inv = (1 / r) * np.array([
        [-np.sin(theta), np.cos(theta), R],
        [-np.sin(theta + 2*np.pi/3), np.cos(theta + 2*np.pi/3), R],
        [-np.sin(theta + 4*np.pi/3), np.cos(theta + 4*np.pi/3), R]
    ])
    return J_inv @ np.array([xdot, ydot, thetadot])

# Position Controller (PID)
def position_control(x_ref, y_ref, theta_ref, x, y, theta, int_err, prev_err):
    # Compute error
    ex = x_ref - x
    ey = y_ref - y
    etheta = theta_ref - theta

    # Derivative of error
    dex = ex - prev_err[0]
    dey = ey - prev_err[1]
    detheta = etheta - prev_err[2]

    # Integrate error
    int_err[0] += ex
    int_err[1] += ey
    int_err[2] += etheta

    # Clamp integral error
    int_err = np.clip(int_err, -INTEGRAL_LIMIT, INTEGRAL_LIMIT)

    # PID control signal
    xdot = KpX * ex + KiX * int_err[0] + KdX * dex
    ydot = KpY * ey + KiY * int_err[1] + KdY * dey
    thetadot = -(Kptheta * etheta + Kitheta * int_err[2] + Kdtheta * detheta)

    # Return also current error as new previous error
    return xdot, ydot, thetadot, int_err, np.array([ex, ey, etheta])


# Control Thread Class
class PID(threading.Thread):
    def __init__(self, refgen):
        super().__init__()
        self.host = "192.168.0.105"  # Define host inside the thread class
        self.port = 9998             # Define port inside the thread class
        self.refgen = refgen
        self.x_ref = 0
        self.y_ref = 0
        self.x = 0
        self.y = 0
        self.theta = 0
        self.theta_ref = 0
        self.running = True
        self.integral_error = np.zeros(3)  # [int_x, int_y, int_theta]
        self.distError = 0
        self.angleError = 0
        self.prev_error = np.zeros(3)  # [prev_ex, prev_ey, prev_etheta]
        self.dt = 0.1  # Control loop time step (seconds)

        self.error_history = []
        self.latest_avg_error = 0
        self.x_error_history = []
        self.y_error_history = []
        self.last_refgen_index = self.refgen.getIndex()

    def run(self):
        with Connection(self.host, self.port) as bot:
            next_time = time.time()
            while self.running:
                # Get current state from robot
                self.x = bot.get_x()
                self.y = bot.get_y()
                self.theta = np.radians(bot.get_theta() + 90)  # Convert to radians

                refPoints = self.refgen.getRefPoints()
                self.x_ref = refPoints[0]
                self.y_ref = refPoints[1]
                self.theta_ref = refPoints[2]

                # Compute velocity commands
                xdot, ydot, thetadot, self.integral_error, self.prev_error = position_control(
                    self.x_ref, self.y_ref, self.theta_ref + np.radians(90),
                self.x, self.y, self.theta, self.integral_error, self.prev_error
                )

                # Compute wheel speeds
                wheel_speeds = inverse_kinematics(self.theta, xdot, ydot, thetadot)

                # Send wheel speeds to correct motors
                bot.set_speed(1, round(wheel_speeds[2]))
                bot.set_speed(2, round(wheel_speeds[0]))
                bot.set_speed(3, round(wheel_speeds[1]))

                self.distError = np.sqrt((self.x_ref - self.x) ** 2 + (self.y_ref - self.y) ** 2)
                self.angleError = self.theta_ref - self.theta

                #print("Wheel Speeds:", wheel_speeds)
                #print(f"x: {self.x:.2f}, y: {self.y:.2f}, theta: {np.rad2deg(self.theta):.2f}")

                
                currIndex = self.refgen.getIndex()
                if currIndex != self.last_refgen_index:
                    self.error_history.append(self.distError)
                    self.x_error_history.append(abs(self.prev_error[0]))
                    self.y_error_history.append(abs(self.prev_error[1]))

                    # Keep history capped at 50
                    if len(self.error_history) > 50:
                        self.error_history.pop(0)
                    if len(self.x_error_history) > 50:
                        self.x_error_history.pop(0)
                    if len(self.y_error_history) > 50:
                        self.y_error_history.pop(0)

                    self.last_refgen_index = currIndex

                # Sleep to control loop rate
                # Control loop fixed time
                next_time += self.dt
                sleep_time = next_time - time.time()
                if sleep_time > 0:
                    time.sleep(sleep_time)
                else:
                    print(f"Warning: RefGen loop overran desired time by {-sleep_time} seconds")
                    next_time = time.time()

    def getState(self):
        return self.x, self.y, self.theta
    
    def getErrors(self):
        return self.distError, self.angleError
    
    def getAverageError(self):
        if len(self.error_history) >= 50:
            return sum(self.error_history[-50:]) / 50
        else:
            return 0.0  # Not enough data yet
        
    def getAverageXError(self):
        if len(self.x_error_history) >= 50:
            return sum(self.x_error_history[-50:]) / 50
        else:
            return 0.0

    def getAverageYError(self):
        if len(self.y_error_history) >= 50:
            return sum(self.y_error_history[-50:]) / 50
        else:
            return 0.0

    def stop(self):
        self.running = False