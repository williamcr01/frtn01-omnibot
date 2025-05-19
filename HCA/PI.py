import numpy as np
import time
import threading
from omnibot.tcp import Connection
import HCA as hca

# Robot Parameters
r = 0.028 * 0.45 / 18  # Wheel radius (meters)
R = 0.16               # Distance from center to wheels (meters)

# Proportional and Integral Gains HCA
KpX_arr = [0.15, 0.3, 0.25]
KpY_arr = [0.15, 0.25, 0.4]
KiX_arr = [0.0, 0.0145 + 0.0525j, 0.005]
KiY_arr = [0.0, 0.005, 0.013+ 0.051j]
KpTheta_arr = [0.05, 0.1, 0.1]
KiTheta_arr = [0.0, 0.0, 0.0]

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

# Position control HCA and PI
def hca_position_control_arr(
    disp_x, disp_y, disp_theta,           # Dispersion arrays (complex)
    int_x, int_y, int_theta,              # Integral state arrays (complex)
    n_x, n_y, n_theta,                    # Current time step
    N,                                    # Samples per period
):
    # Update integrals
    int_x += disp_x
    int_y += disp_y
    int_theta += disp_theta

    # Optional: anti-windup function per harmonic
    int_x = hca_anti_windup(int_x)
    int_y = hca_anti_windup(int_y)
    int_theta = hca_anti_windup(int_theta)

    # Apply per-harmonic PI control (element-wise)
    ctrl_disp_x = KpX_arr * disp_x + KiX_arr * int_x
    ctrl_disp_y = KpY_arr * disp_y + KiY_arr * int_y
    ctrl_disp_theta = KpTheta_arr * disp_theta + KiTheta_arr * int_theta

    # Assembler: convert to time-domain control signals
    H = len(disp_x) - 1
    harmonics = np.arange(H + 1)

    if n_x == n_y and n_x == n_theta:
        phase_vector = np.exp(1j * 2 * np.pi * harmonics * n_x / N)

        xdot = np.real(ctrl_disp_x[0] + 2 * np.sum(ctrl_disp_x[1:] * phase_vector[1:]))
        ydot = np.real(ctrl_disp_y[0] + 2 * np.sum(ctrl_disp_y[1:] * phase_vector[1:]))
        thetadot = -np.real(ctrl_disp_theta[0] + 2 * np.sum(ctrl_disp_theta[1:] * phase_vector[1:]))
    else:
        phase_vector_x = np.exp(1j * 2 * np.pi * harmonics * n_x / N)
        phase_vector_y = np.exp(1j * 2 * np.pi * harmonics * n_y / N)
        phase_vector_theta = np.exp(1j * 2 * np.pi * harmonics * n_theta / N)

        xdot = np.real(ctrl_disp_x[0] + 2 * np.sum(ctrl_disp_x[1:] * phase_vector_x[1:]))
        ydot = np.real(ctrl_disp_y[0] + 2 * np.sum(ctrl_disp_y[1:] * phase_vector_y[1:]))
        thetadot = -np.real(ctrl_disp_theta[0] + 2 * np.sum(ctrl_disp_theta[1:] * phase_vector_theta[1:]))

    return xdot, ydot, thetadot, int_x, int_y, int_theta


def hca_anti_windup(integral_error):

    # Separate real and imaginary parts of the integral error
    real_part = np.real(integral_error)
    imag_part = np.imag(integral_error)

    # Apply clamping (anti-windup) to the real and imaginary parts
    real_part = np.clip(real_part, -INTEGRAL_LIMIT, INTEGRAL_LIMIT)
    imag_part = np.clip(imag_part, -INTEGRAL_LIMIT, INTEGRAL_LIMIT)

    # Reconstruct the integral error as a complex array
    clamped_integral_error = real_part + 1j * imag_part

    return clamped_integral_error

# Control Thread Class
class PI(threading.Thread):
    def __init__(self, refgen, N, H, dt, period, dt_refgen, num_points):
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
        self.distError = 0
        self.angleError = 0
        self.dt = dt
        self.period = period
        self.starterTimer = 0
        self.dt_refgen = dt_refgen

        self.refgen = refgen

        # HCA params and init
        self.H = H
        self.N = N
        self.buffer_x, self.dispersions_x, self.exp_factors_x, self.n_x = hca.initialize_disperser(self.H, self.N)
        self.buffer_y, self.dispersions_y, self.exp_factors_y, self.n_y = hca.initialize_disperser(self.H, self.N)
        self.buffer_theta, self.dispersions_theta, self.exp_factors_theta, self.n_theta = hca.initialize_disperser(self.H, self.N)
        self.int_err_x = np.zeros(H + 1, dtype=complex)
        self.int_err_y = np.zeros(H + 1, dtype=complex)
        self.int_err_theta = np.zeros(H + 1, dtype=complex)
        self.num_points = num_points
        self.count = 0
        self.error_arr_x = []
        self.error_arr_y = []

    def run(self):
        with Connection(self.host, self.port) as bot:
            next_time = time.time()
            self.refgen.botRunning(True)
            if self.refgen.botIsRunning:
                print("refgen on")
            while self.running:
                # Get current state from robot
                self.x = bot.get_x()
                self.y = bot.get_y()
                self.theta = np.radians(bot.get_theta() + 90)  # Convert to radians

                refPoints = self.refgen.getRefPoints()
                self.x_ref = refPoints[0]
                self.y_ref = refPoints[1]
                self.theta_ref = refPoints[2]

                e_x = self.x_ref - self.x
                e_y = self.y_ref - self.y
                e_theta = (self.theta_ref + np.radians(90)) - self.theta

                self.dispersions_x, self.n_x = hca.update_disperser(e_x, self.buffer_x, self.dispersions_x, self.exp_factors_x, self.n_x)
                self.dispersions_y, self.n_y = hca.update_disperser(e_y, self.buffer_y, self.dispersions_y, self.exp_factors_y, self.n_y)
                self.dispersions_theta, self.n_theta = hca.update_disperser(
                    e_theta, self.buffer_theta, self.dispersions_theta, self.exp_factors_theta, self.n_theta
                )

                xdot, ydot, thetadot, self.int_err_x, self.int_err_y, self.int_err_theta, = hca_position_control_arr(
                    self.dispersions_x, self.dispersions_y, self.dispersions_theta, self.int_err_x, self.int_err_y, self.int_err_theta,
                    self.n_x, self.n_y, self.n_theta, self.N
                )
                if self.starterTimer >= self.period:

                # Compute wheel speeds
                    wheel_speeds = inverse_kinematics(self.theta, xdot, ydot, thetadot)
                else:
                    wheel_speeds = np.zeros(3)

                # Send wheel speeds to correct motors
                bot.set_speed(1, round(wheel_speeds[2]))
                bot.set_speed(2, round(wheel_speeds[0]))
                bot.set_speed(3, round(wheel_speeds[1]))

                self.distError = np.sqrt((self.x_ref - self.x) ** 2 + (self.y_ref - self.y) ** 2)
                self.angleError = self.theta_ref - self.theta

                # Control loop fixed time
                next_time += self.dt
                sleep_time = next_time - time.time()
                self.starterTimer += self.dt
                if sleep_time > 0:
                    time.sleep(sleep_time)
                else:
                    print(f"Warning: Control loop overran desired time by {-sleep_time} seconds")
                    next_time = time.time()
                if self.count == self.num_points:
                    print(f"Avg error X: {np.mean(self.error_arr_x)}\nAvg error Y: {np.mean(self.error_arr_y)}")
                    self.count = 0
                    self.error_arr_x = []
                    self.error_arr_y = []
                else:
                    self.count += 1
                    self.error_arr_x.append(e_x)
                    self.error_arr_y.append(e_y)

    def getState(self):
        return self.x, self.y, self.theta
    
    def getErrors(self):
        return self.distError, self.angleError

    def stop(self):
        self.running = False
        self.join()