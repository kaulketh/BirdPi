"""
Day/night mode control for BirdPi.

This module controls the infrared lighting depending on daylight conditions.
"""

import time

from birdpi.daylight.sun import Daylight
from birdpi.lighting.ir_lights import IRLights
from birdpi.lighting.ir_lights import IRMode
from birdpi.motion.detector import MotionDetector
from birdpi.utils.logger import get_logger

logger = get_logger(__name__)


class DayNightController:

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

    def update(
            self,
            force: bool = False,
    ) -> None:
        """
        Check daylight state and switch mode when necessary.
        """

        now = time.monotonic()

        if not force and now < self._next_check:
            return

        self._next_check = now + self.check_interval_seconds

        is_night = self.daylight.is_night()

        logger.debug(
            "Daylight check: %s",
            "NIGHT" if is_night else "DAY",
        )

        if is_night == self._night_mode and not force:
            return

        self._night_mode = is_night

        if self._night_mode:
            self.ir_lights.set_mode(IRMode.LEFT)

            logger.info(
                "Switched to NIGHT mode, IR lighting enabled"
            )
        else:
            self.ir_lights.set_mode(IRMode.OFF)

            logger.info(
                "Switched to DAY mode, IR lighting disabled"
            )

        self.motion_detector.reset()

    def close(self) -> None:
        """
        Switch infrared lighting off.
        """

        self.ir_lights.off()
