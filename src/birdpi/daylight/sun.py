"""
Daylight calculations for BirdPi.
"""

from datetime import datetime, timedelta

from astral import LocationInfo
from astral.sun import sun

from birdpi.config import Config
from birdpi.daylight.state import DayNightState


class Daylight:
    """
    Determine whether BirdPi is currently in day or night mode.
    """

    def __init__(
            self,
            config: Config,
            sunset_offset_minutes: int = 20,
            sunrise_offset_minutes: int = -20,
    ) -> None:
        self.config = config

        self.sunset_offset = timedelta(
            minutes=sunset_offset_minutes
        )

        self.sunrise_offset = timedelta(
            minutes=sunrise_offset_minutes
        )

    def _sun_times(
            self,
            now: datetime,
    ) -> tuple[datetime, datetime]:
        location = LocationInfo(
            latitude=self.config.location.latitude,
            longitude=self.config.location.longitude,
        )

        times = sun(
            location.observer,
            date=now.date(),
            tzinfo=now.astimezone().tzinfo,
        )

        sunrise = times["sunrise"] + self.sunrise_offset
        sunset = times["sunset"] + self.sunset_offset

        return sunrise, sunset

    def is_night(
            self,
            now: datetime | None = None,
    ) -> bool:
        """
        Return True if the current time is outside the daylight interval.
        """

        return self.state(now) == DayNightState.NIGHT

    def state(
            self,
            now: datetime | None = None,
    ) -> DayNightState:
        """
        Return the current day/night state.
        """

        now = now or datetime.now().astimezone()

        sunrise, sunset = self._sun_times(now)

        if now < sunrise or now >= sunset:
            return DayNightState.NIGHT

        return DayNightState.DAY
