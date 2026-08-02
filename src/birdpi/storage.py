"""
Storage management for BirdPi.

This module provides the Storage class which is responsible for managing
directories and generating file paths for captured images.
"""
from datetime import datetime
from pathlib import Path

from birdpi.config import Config


class Storage:
    """
    Manage BirdPi file storage.
    """

    def __init__(self, config: Config) -> None:
        self.config = config

    def ensure_directories(self) -> None:
        """
        Create required directories if they do not exist.
        """

        self.config.image_path.mkdir(
            parents=True,
            exist_ok=True
        )

    def next_image_path(self, filename: str | None = None) -> Path:
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"image_{timestamp}.jpg"

        return self.config.image_path / filename
