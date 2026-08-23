"""
Day/night mode control for BirdPi.

This module controls the infrared lighting depending on daylight conditions.
"""

import time

from birdpi.camera.ir_lights import IRLights
from birdpi.daylight.sun import Daylight
from birdpi.motion.detector import MotionDetector


class DayNightController:
    """
    Manage BirdPi day/night mode and infrared lighting.
    """

    def __init__(
            self,
            daylight: Daylight,
            ir_lights: IRLights,
            motion_detector: MotionDetector,
            check_interval_seconds: int,
    ) -> None:
        self.daylight = daylight
        self.ir_lights = ir_lights
        self.motion_detector = motion_detector
        self.check_interval_seconds = check_interval_seconds

        self._night_mode: bool | None = None
        self._next_check = 0.0

    @property
    def night_mode(self) -> bool | None:
        """
        Return the currently active night-mode state.
        """

        return self._night_mode

    def update(self) -> None:
        """
        Check daylight state and switch mode when necessary.
        """

        now = time.monotonic()

        if now < self._next_check:
            return

        self._next_check = now + self.check_interval_seconds

        is_night = self.daylight.is_night()

        if is_night == self._night_mode:
            return

        self._night_mode = is_night

        if self._night_mode:
            self.ir_lights.left_on()
        else:
            self.ir_lights.off()

        self.motion_detector.reset()

    def close(self) -> None:
        """
        Switch infrared lighting off.
        """

        self.ir_lights.off()
