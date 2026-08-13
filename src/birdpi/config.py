"""
BirdPi configuration module.

This module contains the configuration management for BirdPi, including
default configuration creation and associated functionality.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Config:
    """
    BirdPi configuration.
    """

    data_path: Path
    image_path: Path
    session_path: Path
    observation_path: Path

    camera_width: int
    camera_height: int

    observation_interval_seconds: int
    web_refresh_interval_seconds: int

    @property
    def status_refresh_seconds(self) -> int:
        return min(self.observation_interval_seconds, 30)


def load_config() -> Config:
    """
    Create the default BirdPi configuration.
    """

    data_path = Path("/home/kaulketh/birdpi-data")
    image_path = data_path / "images"
    session_path = data_path / "sessions"
    observation_path = data_path / "observations"

    resolution = (3280, 2464)

    observer_interval = 300
    web_interval = 10

    return Config(
        data_path=data_path,
        image_path=image_path,
        session_path=session_path,
        observation_path=observation_path,
        camera_width=resolution[0],
        camera_height=resolution[1],
        observation_interval_seconds=observer_interval,
        web_refresh_interval_seconds=web_interval,
    )
