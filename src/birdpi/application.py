"""
Main application module for the BirdPi system.

This module initializes the core components of the BirdPi application, including the
configuration, camera, storage, and observer systems. It serves as the entry point for
running the BirdPi system.
"""

from birdpi.camera.capture import Camera
from birdpi.config import Config
from birdpi.detection.detector import Detector
from birdpi.detection.dummy import DummyDetector
from birdpi.models import CapturedImage
from birdpi.observer import Observer
from birdpi.storage import Storage
from birdpi.utils.logger import get_logger

logger = get_logger(__name__)


class BirdPi:
    """
    Main application class for the BirdPi system.
    """

    def __init__(self,
                 config: Config,
                 detector: Detector | None = None,
                 ) -> None:
        self.config = config

        self.storage = Storage(config)
        self.storage.ensure_directories()

        self.camera = Camera(config)

        self.detector = detector or DummyDetector()

        self.observer = Observer(
            config,
            self.capture,
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

    def capture(
            self,
            session_id: str | None = None,
    ) -> CapturedImage:
        """
        Capture an image, run detection, and persist observations.
        """

        image = self.camera.capture(
            session_id=session_id,
        )

        observations = self.detector.detect(image)

        for observation in observations:
            self.storage.save_observation(observation)

        logger.info(
            "Image captured: %s",
            image.path,
        )

        logger.info(
            "Detections: %s",
            len(observations),
        )

        return image
