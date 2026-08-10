"""
Main module for the BirdPi system.

This module provides the main entry point for initializing and running the
BirdPi application. It configures and integrates the necessary parts
such as the camera and application settings.
"""
from birdpi.camera.capture import Camera
from birdpi.config import Config
from birdpi.storage import Storage
from birdpi.utils.logger import get_logger

logger = get_logger(__name__)


class BirdPi:
    """
    Main application class for the BirdPi system.
    """

    def __init__(self, config: Config) -> None:
        self.config: Config = config
        self.camera: Camera = Camera(config)
        self.storage: Storage = Storage(config)

    def run(self) -> None:
        """
        Start BirdPi application.
        """

        logger.info("BirdPi online")

        image = self.camera.capture()

        logger.info("Image captured: %s", image)
