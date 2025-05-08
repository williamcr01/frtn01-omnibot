import numpy as np
import time
import threading
from omnibot.tcp import Connection

# Robot Parameters
r = 0.028 * 0.45 / 18  # Wheel radius (meters)
R = 0.16               # Distance from center to wheels (meters)

# Proportional and Integral Gains
KpX = 0.7
KpY = 0.7
KiX = 0.05
KiY = 0.05
Kptheta = 0.7
Kitheta = 0.02

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

# Position Controller (PI)
def position_control(x_ref, y_ref, theta_ref, x, y, theta, int_err):
    # Compute error
    ex = x_ref - x
    ey = y_ref - y
    etheta = theta_ref - theta

    # Integrate error
    int_err[0] += ex
    int_err[1] += ey
    int_err[2] += etheta

    # Clamp integral error to avoid windup
    int_err = np.clip(int_err, -INTEGRAL_LIMIT, INTEGRAL_LIMIT)

    # Compute control signal
    xdot = KpX * ex + KiX * int_err[0]
    ydot = KpY * ey + KiY * int_err[1]
    thetadot = -(Kptheta * etheta + Kitheta * int_err[2])

    return xdot, ydot, thetadot, int_err

# Control Thread Class
class PID(threading.Thread):
    def __init__(self, refgen):
        super().__init__()
        self.host = "192.168.0.105"  # Define host inside the thread class
        self.port = 9998             # Define port inside the thread class
        self.x_ref = 0
        self.y_ref = 0
        self.x = 0
        self.y = 0
        self.theta_ref = 0
        self.running = True
        self.integral_error = np.zeros(3)  # [int_x, int_y, int_theta]

        self.refgen = refgen

    def run(self):
        with Connection(self.host, self.port) as bot:
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
                xdot, ydot, thetadot, self.integral_error = position_control(
                    self.x_ref, self.y_ref, self.theta_ref + np.radians(90), self.x, self.y, self.theta, self.integral_error
                )

                # Compute wheel speeds
                wheel_speeds = inverse_kinematics(self.theta, xdot, ydot, thetadot)

                # Send wheel speeds to correct motors
                bot.set_speed(1, round(wheel_speeds[2]))
                bot.set_speed(2, round(wheel_speeds[0]))
                bot.set_speed(3, round(wheel_speeds[1]))

                print("Wheel Speeds:", wheel_speeds)
                print(f"x: {self.x:.2f}, y: {self.y:.2f}, theta: {np.rad2deg(self.theta):.2f}")

                # Sleep to control loop rate
                time.sleep(0.01)

    def getState(self):
        return self.x, self.y, self.theta

    def stop(self):
        self.running = False
        self.stop_event.set()