"""
Day/night mode control for BirdPi.

"""

import time
from collections.abc import Callable

from birdpi.daylight.state import DayNightState
from birdpi.daylight.sun import Daylight
from birdpi.lighting.ir_lights import IRLights
from birdpi.lighting.ir_lights import IRMode
from birdpi.motion.detector import MotionDetector
from birdpi.observation.state import ObservationMode
from birdpi.observation.state import ObservationState
from birdpi.utils.logger import get_logger

logger = get_logger(__name__)


class DayNightController:

    def __init__(
            self,
            daylight: Daylight,
            ir_lights: IRLights,
            motion_detector: MotionDetector,
            observation_state: ObservationState,
            check_interval_seconds: int,
            status_callback: Callable[
                                 [bool, IRMode], None] | None = None,
    ) -> None:
        self.daylight = daylight
        self.ir_lights = ir_lights
        self.motion_detector = motion_detector
        self.observation_state = observation_state
        self.check_interval_seconds = check_interval_seconds

        self._day_night_state: DayNightState | None = None
        self._next_check = 0.0

        self.status_callback = status_callback

    @property
    def day_night_state(self) -> DayNightState | None:
        """
        Return the currently active day/night state.
        """

        return self._day_night_state

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

        day_night = self.daylight.state()

        logger.debug(
            "Daylight check: %s",
            day_night.name,
        )

        if day_night == self._day_night_state and not force:
            return

        self._day_night_state = day_night
        self.observation_state.day_night = day_night

        if (
                day_night == DayNightState.NIGHT
                and self.observation_state.mode == ObservationMode.WILDLIFE
        ):
            self.ir_lights.set_mode(IRMode.LEFT)

            logger.info(
                "IR lighting enabled: mode=wildlife, day_night=night"
            )

        else:
            self.ir_lights.set_mode(IRMode.OFF)

            logger.info(
                "IR lighting disabled: mode=%s, day_night=%s",
                self.observation_state.mode.value,
                day_night.value,
            )

        if self.status_callback is not None:
            self.status_callback(
                day_night == DayNightState.NIGHT,
                self.ir_lights.mode,
            )

        self.motion_detector.reset()

    def close(self) -> None:
        """
        Switch infrared lighting off.
        """

        self.ir_lights.off()
