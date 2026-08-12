"""
Main application module for the BirdPi system.

This module initializes the core components of the BirdPi application, including the
configuration, camera, storage, and observer systems. It serves as the entry point for
running the BirdPi system.
"""
from birdpi.camera.capture import Camera
from birdpi.config import Config
from birdpi.observer import Observer
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
        self.observer: Observer = Observer(config, self.camera,)

    def run(self) -> None:
        """
        Start BirdPi application.
        """

        logger.info("BirdPi online")

        image = self.camera.capture()

        logger.info("Image captured: %s", image)
