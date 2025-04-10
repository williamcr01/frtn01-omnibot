import numpy as np
import time
from omnibot.tcp import Connection

# Robot Parameters
r = 0.028*0.45/18  # Wheel radius (meters)
R = 0.16   # Distance from center to wheels (meters)
Kp = 0.005  # Proportional control gain

# Inverse Kinematics Matrix Function
def inverse_kinematics(theta, xdot, ydot, thetadot):
    J_inv = (1/r) * np.array([
        [-np.sin(theta), np.cos(theta), R],
        [-np.sin(theta + 2*np.pi/3), np.cos(theta + 2*np.pi/3), R],
        [-np.sin(theta + 4*np.pi/3), np.cos(theta + 4*np.pi/3), R]
    ])
    
    wheel_speeds = J_inv @ np.array([xdot, ydot, thetadot])
    return wheel_speeds

# Position Controller
def position_control(x_ref, y_ref, theta_ref, x, y, theta):
    # Compute error
    ex = x_ref - x
    ey = y_ref - y
    etheta = theta_ref - theta
    
    # Proportional control to generate velocity commands
    xdot = Kp * ex
    ydot = Kp * ey
    thetadot = Kp * etheta
    
    return xdot, ydot, thetadot

# Connection Parameters
HOST = "192.168.0.105"
PORT = 9998

# Control loop
if __name__ == "__main__":
    # Target position
    x_ref, y_ref, theta_ref = 0.0, 0.0, 0  # Modify as needed
    
    with Connection(HOST, PORT) as bot:
        while True:
            # Get current state from robot
            x = bot.get_x()
            y = bot.get_y()
            theta = bot.get_theta()
            
            # Compute velocity commands
            xdot, ydot, thetadot = position_control(x_ref, y_ref, theta_ref, x, y, theta)
            
            # Compute wheel speeds
            wheel_speeds = inverse_kinematics(theta, xdot, ydot, thetadot)
            
            # Send wheel speeds to motors
            for i, v in enumerate(wheel_speeds):
                bot.set_speed(i, round(v))
            
            print("Wheel Speeds:", wheel_speeds)
            print(f"x: {x}, y: {y}, theta: {theta}")
            time.sleep(0.2)
            
