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

    camera_width: int
    camera_height: int

    observation_interval_seconds: int


def load_config() -> Config:
    """
    Create the default BirdPi configuration.
    """

    data_path = Path("/home/kaulketh/birdpi-data")
    images_path = data_path / "images"
    resolution = (3280, 2464)
    observer_interval = 300

    return Config(
        data_path=data_path,
        image_path=images_path,
        camera_width=resolution[0],
        camera_height=resolution[1],
        observation_interval_seconds=observer_interval,
    )
