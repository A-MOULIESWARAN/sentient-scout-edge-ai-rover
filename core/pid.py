import time


class PIDController:

    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd

        self.integral = 0.0
        self.previous_error = 0.0
        self.previous_time = time.time()

    def update(self, error):

        current_time = time.time()

        dt = current_time - self.previous_time

        if dt <= 0:
            dt = 0.001

        # Proportional term
        proportional = self.kp * error

        # Integral term
        self.integral += error * dt
        integral = self.ki * self.integral

        # Derivative term
        derivative_error = (
            error - self.previous_error
        ) / dt

        derivative = self.kd * derivative_error

        # PID output
        output = (
            proportional
            + integral
            + derivative
        )

        self.previous_error = error
        self.previous_time = current_time

        return output

    def reset(self):

        self.integral = 0.0
        self.previous_error = 0.0
        self.previous_time = time.time()