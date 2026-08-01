"""
A configuration module for BirdPi.

This module provides the `Config` class which contains configuration
settings for the BirdPi application. It defines paths and settings
related to data storage and camera parameters.
"""
from pathlib import Path


class Config:
    """
    BirdPi configuration.
    """

    def __init__(self):
        self.data_path = Path(
            "/home/kaulketh/birdpi-data"
        )

        self.image_path = self.data_path / "images"

        self.camera_width = 1920
        self.camera_height = 1080
