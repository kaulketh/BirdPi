"""
This module provides functionalities to handle configuration for the BirdPi system.

The module defines a `Config` class for storing configuration-related parameters
and a `load_config` function to generate a default configuration instance.
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
    )
