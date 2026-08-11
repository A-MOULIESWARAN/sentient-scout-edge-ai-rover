import time

from config.settings import (
    PAN_MIN,
    PAN_MAX,
    TILT_MIN,
    TILT_MAX
)

try:
    from base_ctrl import BaseController

except Exception as e:

    print(
        f"CRITICAL WARNING: Failed to load base_ctrl. "
        f"The actual error is: {e}"
    )

    BaseController = None


class PanTiltMechanism:

    def __init__(self):

        # Connect to the rover's serial base controller
        if BaseController is not None:

            try:

                self.base = BaseController(
                    "/dev/ttyTHS1",
                    115200
                )

                print(
                    "Hardware Initialized: "
                    "Connected to BaseController on /dev/ttyTHS1"
                )

            except Exception as e:

                print(f"Serial Error: {e}")

                print(
                    "HINT: You might need to run "
                    "the script with 'sudo' for serial port access."
                )

                self.base = None

        else:

            self.base = None

        # Start at the center position
        self.current_pan = 0
        self.current_tilt = 0

        # Move to center position on startup
        self._send_command(
            self.current_pan,
            self.current_tilt
        )

    def move(self, pan_adjust, tilt_adjust):

        # Apply PID adjustments

        self.current_pan += pan_adjust

        self.current_tilt -= tilt_adjust

        # Safety clamps
        self.current_pan = max(
            PAN_MIN,
            min(PAN_MAX, self.current_pan)
        )

        self.current_tilt = max(
            TILT_MIN,
            min(TILT_MAX, self.current_tilt)
        )

        # Send command to hardware
        self._send_command(
            self.current_pan,
            self.current_tilt
        )

    def _send_command(self, pan, tilt):

        # Debug information
        print(
            f"Executing Move -> "
            f"PAN: {int(pan)} | "
            f"TILT: {int(tilt)}"
        )

        # Send physical command over UART
        if self.base is not None:

            # gimbal_ctrl takes:
            # (x_angle, y_angle, speed, acceleration)

            self.base.gimbal_ctrl(
                int(pan),
                int(tilt),
                0,
                0
            )