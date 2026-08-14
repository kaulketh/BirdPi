"""
Main application module for the BirdPi system.

This module initializes the core components of the BirdPi application, including the
configuration, camera, storage, and observer systems. It serves as the entry point for
running the BirdPi system.
"""
from sys import path

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
        self.config = config

        self.storage = Storage(config)
        self.storage.ensure_directories()

        self.camera = Camera(config)
        self.observer = Observer(
            config,
            self.camera,
        )

    def run(self) -> None:
        """
        Start BirdPi application.
        """

        logger.info("BirdPi online")
        image = self.camera.capture()
        logger.info("Image captured: %s", image.path)

    def start_observation(self) -> None:
        """
        Start automatic observation.
        """

        self.observer.start()

    def stop_observation(self) -> None:
        """
        Stop automatic observation and persist the completed session.
        """

        self.observer.stop()

        session = self.observer.session

        if session is not None and not session.active:
            path = self.storage.save_session(session)

            logger.info(
                "Observation session saved: %s",
                path,
            )
