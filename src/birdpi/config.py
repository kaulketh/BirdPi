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

    return Config(
        data_path=data_path,
        image_path=data_path / "images",
        camera_width=3280,
        camera_height=2464,
        observation_interval_seconds=300,
    )
