import numpy as np
import time
import PI
import refgen
import threading

class Regul(threading.Thread):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.H = 0.1
        self.PI_x = PI.PI(self.H)
        self.PI_y = PI.PI(self.H)
        self.PI_theta = PI.PI(self.H)
        self.refgen = None
        self.should_run = True
        # Robot Parameters
        self.r = 0.028*0.45/18  # Wheel radius (meters)
        self.R = 0.16   # Distance from center to wheels (meters)

    def set_refgen(self, refgen):
        self.refgen = refgen

    def set_PI_param(self, params):
        self.PI.set_parameter(params)
    
    def get_PI_param(self, pi):
        return pi.p

    def shutdown(self):
        self.should_run = False

    def limit(self, v, min=-10, max=10): # ändra dess till riktiga värden
        if v < min:
            v = min
        elif v > max:
            v = max
        return v
    
    def inverse_kinematics(self, theta, xdot, ydot, thetadot):
        J_inv = (1/self.r) * np.array([
            [-np.sin(theta), np.cos(theta), self.R],
            [-np.sin(theta + 2*np.pi/3), np.cos(theta + 2*np.pi/3), self.R],
            [-np.sin(theta + 4*np.pi/3), np.cos(theta + 4*np.pi/3), self.R]
        ])
        
        wheel_speeds = J_inv @ np.array([xdot, ydot, thetadot])
        return wheel_speeds
    
    def run(self):
        print("regul thread started")
        while self.should_run:
            print("regul thread running")
            theta = self.bot.get_theta()
            x_ref, y_ref = self.refgen.get_ref()
            x_dot = self.PI_x.calculate_output(self.bot.get_x(), x_ref)
            y_dot = self.PI_y.calculate_output(self.bot.get_y(), y_ref)
            theta_dot = self.PI_theta.calculate_output(theta, 0)
            self.PI_x.update_state(x_dot)
            self.PI_y.update_state(y_dot)
            self.PI_theta.update_state(theta_dot)

            wheel_speeds = self.inverse_kinematics(theta, x_dot, y_dot, theta_dot)
            self.write_output(wheel_speeds)

            time.sleep(self.H)
            

    def write_output(self, wheel_speeds):
        for i, v in enumerate(wheel_speeds):
            self.bot.set_speed(i, round(v))
            print(v)

    def read_input(self):
        return self.bot.get_x(), self.bot.get_y()