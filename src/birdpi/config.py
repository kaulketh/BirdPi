"""
Configuration module for BirdPi.

This module defines the application's configuration data model and
provides a factory function for creating the default configuration.
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
