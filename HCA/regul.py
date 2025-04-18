import numpy as np
import time
import PI
import threading
import PIParameters

class Regul(threading.Thread):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.H = 0.1
        self.PI_x = PI.PI(self.H)
        self.PI_y = PI.PI(self.H)
        self.PI_theta = PI.PI(self.H)
        self.param_theta = PIParameters.PIParameters(K=4.0, Ti=0, Tr=10.0, Beta=1.0, H=self.H, integrator_on=False)
        self.set_PI_param(self.PI_theta, self.param_theta)
        self.refgen = None
        self.should_run = True
        # Robot Parameters
        self.r = 0.028*0.45/18  # Wheel radius (meters)
        self.R = 0.16   # Distance from center to wheels (meters)

    def set_refgen(self, refgen):
        self.refgen = refgen

    def set_PI_param(self, PI, params):
        PI.set_parameters(params)
    
    def get_PI_param(self, pi):
        return pi.p

    def shutdown(self):
        self.should_run = False

    def limit(self, v, min=-1000, max=1000): # ändra dess till riktiga värden
        if v < min:
            v = min
        elif v > max:
            v = max
        return v
    
    def inverse_kinematics(self, theta, xdot, ydot, thetadot):
        #theta = theta * np.pi / 180
        J_inv = (1/self.r) * np.array([
            [-np.sin(theta), np.cos(theta), self.R],
            [-np.sin(theta + 2*np.pi/3), np.cos(theta + 2*np.pi/3), self.R],
            [-np.sin(theta + 4*np.pi/3), np.cos(theta + 4*np.pi/3), self.R]
        ])
        
        wheel_speeds = J_inv @ np.array([xdot, ydot, thetadot])
        return wheel_speeds
    
    def run(self):
        #x_dot, y_dot, theta_dot = 0
        x_old = self.bot.get_x()
        y_old = self.bot.get_y()
        print("regul thread started")
        while self.should_run:
            print("regul thread running")
            theta = self.bot.get_theta()
            theta = theta * np.pi / 180
            x = self.bot.get_x()
            y = self.bot.get_y()
            x_ref, y_ref = self.refgen.get_ref()
            x_dot = self.PI_x.calculate_output(x, x_ref)
            y_dot = self.PI_y.calculate_output(y, y_ref)
            theta_dot = self.PI_theta.calculate_output(theta, 0)
            if abs(x_dot) < 0.5:
                self.PI_x.update_state(x_dot)
            else:
                self.PI_x.update_state(x-x_old)
            if abs(y_dot) < 0.5:
                self.PI_y.update_state(y_dot)
            else:
                self.PI_y.update_state(y-y_old)
            """ if abs(theta_dot) < 0.1:
                self.PI_theta.update_state(theta_dot)
            else:
                self.PI_theta.update_state(0.1) """

            wheel_speeds = self.inverse_kinematics(theta, x_dot, y_dot, theta_dot)
            for i, v in enumerate(wheel_speeds):
                wheel_speeds[i] = self.limit(v)
            self.write_output(wheel_speeds)

            x_old = x
            y_old = y

            time.sleep(self.H)
            

    def write_output(self, wheel_speeds):
        self.bot.set_speeds([round(wheel_speeds[2]), round(wheel_speeds[0]), round(wheel_speeds[1])])
        for i, v in enumerate(wheel_speeds):
            #self.bot.set_speed(i, round(v))
            print(f"wheel {i}: {v}")

    def read_input(self):
        return self.bot.get_x(), self.bot.get_y()