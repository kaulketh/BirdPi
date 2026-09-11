from dataclasses import dataclass
from enum import StrEnum

from birdpi.daylight.state import DayNightState


class ObservationMode(StrEnum):
    BIRD = "bird"
    WILDLIFE = "wildlife"


@dataclass
class ObservationState:
    day_night: DayNightState = DayNightState.DAY
    mode: ObservationMode = ObservationMode.BIRD

    @property
    def active(self) -> bool:
        """
        Return whether observation should currently be active.
        """

        if self.mode == ObservationMode.WILDLIFE:
            return True

        return self.day_night == DayNightState.DAY

    @property
    def standby(self) -> bool:
        return not self.active
